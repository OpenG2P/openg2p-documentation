---
description: Preparing an install for production.
---

# Production

A demo install keeps the defaults; a production install changes the items below, during the [install steps](README.md#install-steps). The registries' own production settings are in their guides ([Farmer Registry](../../products/registry/farmer-registry/deployment/README.md#before-going-to-production), [Crop Sown Registry](../../products/registry/crop-sown-registry/deployment/rancher.md#production)).

## Topology

In production, each department and the Exchange usually run on their own clusters: [Separate Clusters](separate-clusters.md).

## Exchange Consent Manager signing key

The demo key is public: anyone could sign consent tokens the departments accept. Create the Secret before installing Commons Services:

```bash
kubectl -n agrix create secret generic agrix-cm-signing \
  --from-file=cm_signing.p12=./cm_signing.p12 --from-literal=password='<p12 password>'
```

## Exchange: Commons Services

| Field | Value | Why |
| --- | --- | --- |
| Base Domain (both commons charts) | The Exchange's domain | The departments find the Exchange CM at `agrix.<parent domain>`; with another name, each department sets **Exchange Domain** |
| Signing Key (Consent Manager) | **existing** | Use your own key |
| Signing Key Secret | `agrix-cm-signing` | The Secret above |
| Signing Key ID | e.g. `agrix-cm-2026-01` | Stamped on each consent token; change it when the key is rotated |
| Install Mock Identity System? | **No** | eSignet connected to the real national ID system |
| Load Sample People | **Off** | |

Step by step: [replacing the demo key](../../consent-management/deployment/README.md#replacing-the-demo-key-for-production-rancher-step-by-step).

## Composite

| Field | Value | Why |
| --- | --- | --- |
| Base Domain | The same as the Exchange's commons | Every hostname sits under it |
| Image Tag, Console UI Image Tag | A released version | `develop` images move |
| Composite Hostname, Console Hostname | Under the Exchange domain | Partners call the Composite there |
| Allowed Browser Origins (CORS) | `https://<partner portal hostname>` | The partner portal reads the use-case list |
| Enable Autoscaling, Min/Max Replicas | On, sized to the load | |
| Edge Rate Limit, Edge Limit (Requests) | On, above the expected peak of all partners together | [Edge rate limit](#edge-rate-limit) |

### Edge rate limit

The Composite chart limits calls to its use-case API (`/composite/v1/use-cases`) at the Istio ingress gateway, for all partners together, before they reach a pod. Other paths of the Composite, and other installs, are not limited. What it is: [Rate Limiting](../composite/rate-limiting.md); the settings: [chart settings](composite-chart-settings.md#scaling-and-rate-limits).

1. In Rancher, **Upgrade** the Composite release (e.g. `agri-composite`), group **Rate Limits**.
2. Turn **Edge Rate Limit** on and set **Edge Limit (Requests)** and **Edge Limit Interval** above the expected peak of all partners together. The limit is counted per gateway pod: two pods allow up to twice the number.
3. Upgrade. The chart creates the EnvoyFilter `<namespace>-<release>-edge-ratelimit` (e.g. `agrix-agri-composite-edge-ratelimit`) in `istio-system`, beside any EnvoyFilters already there:

```bash
kubectl -n istio-system get envoyfilter
```

Turning the setting off, or uninstalling the Composite, removes the EnvoyFilter.

## The Composite's key

The install generates it. Where keys must come from your organisation's own key management, create the Secret `agri-composite-signing` with your `.p12` before installing the Composite ([Keys: use your own key](../administration/keys.md#use-your-own-key)). Only the Composite and its operators may read the Secret.

## Approvals

Separate who raises and who approves Partner Management requests, at the Exchange and in each department ([Managing Partners](../administration/managing-partners.md#onboard-a-partner), [Releasing Registry Data to the Composite](../administration/releasing-data-to-the-composite.md#add-the-policy)).

## Services that stay internal

Partner Management's partner API and the CMs' partner APIs have no login: check that no public route exposes them (the charts put them on the internal gateway). The Composite's API is the only public entry for partners.

## Public catalogue (Master Data)

Commons Services serves Master Data's [public catalogue](../../platform/platform-services/master-data-service/public-catalogue.md) (the anonymous, read-only `/public/` API, with the datasets marked public) on its own host, `catalogue.<base domain>`, which serves only `/public/`. Like every host, it is on the internal gateway: reachable over WireGuard only. Publishing it on the internet is a separate decision: which datasets may be public is each department's.

The API does not limit callers itself (behind proxies it cannot tell them apart), so **limit the public host as a whole at the public nginx**, the only entry from the internet.

1. **DNS:** in Route 53, an A record `catalogue.<base domain>` → the public nginx. It takes precedence over the wildcard `*.<base domain>`, which keeps pointing at the private nginx; every other host stays private.
2. **TLS:** a certificate for the host on the public nginx (e.g. certbot).
3. **nginx:** a server block for the host that forwards only `/public/`, with a rate limit for the whole host:

```nginx
# http { } context, once:
limit_req_zone $server_name zone=mds_catalogue:1m rate=50r/s;

server {
    listen <public-nginx-ip>:443 ssl;
    server_name catalogue.<base domain>;
    ssl_certificate     /etc/letsencrypt/live/catalogue.<base domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/catalogue.<base domain>/privkey.pem;

    location /public/ {
        limit_except GET HEAD OPTIONS { deny all; }
        limit_req        zone=mds_catalogue burst=100 nodelay;
        limit_req_status 429;
        proxy_pass         http://openg2pClusterUpstream;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host  $host;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
    location / { return 404; }
}
```

   * `rate` and `burst` are examples: set them to what the Master Data API handles (here about 50 requests a second for all callers together, with bursts of 100). Beyond them nginx answers `429`.
   * The key `$server_name` makes one limit for the host. Several nginx servers behind a load balancer each count their own: divide the rate by their number.
4. **Refuse unknown hosts** on the public nginx, if not already done. Otherwise a request with another `Host` (e.g. `master-data.<base domain>`) falls into the first server block and reaches a private service:

```nginx
server { listen <public-nginx-ip>:443 ssl default_server; ssl_reject_handshake on; }
server { listen <public-nginx-ip>:80  default_server; return 444; }
```

5. **Check:** `https://catalogue.<base domain>/public/datasets` answers from the internet; any other path there answers `404`; the Master Data host still answers over WireGuard only.

Internal users keep reaching `/public/` on the Master Data host (`master-data.<base domain>/public/…`), which the nginx limit does not touch. For heavy public use, put a CDN with caching (e.g. CloudFront, with AWS WAF rate rules) in front: the API marks its answers cacheable for 5 minutes.

## Remove test leftovers

If the test ran on this install: [Testing: clean up](testing.md#clean-up). Also remove the registries' sample data, and their sanity partner `PARTNER_CM_SANITY` if the sanity tests ran.

## Keep

* The Audit Manager on in every install.
* Backups of each Partner Management and Consent Manager database: partners, keys, policies and consents live there.

# Private Access Channel

A Private Access Channel (PAC) provides control over a user accessing a particular domain. Not all users will be required to control every domain. A PAC implemented as  a tuple of **Wireguard, Load Balancer, and Ingress gateway**.  A channel provides a group of users **access to resources** of the infrastructure. The users assigned to the Wireguard server determine the group of users with access to these channels. All users with access to a Wireguard server have access to all channels to which the Wireguard server is connected. The visual below depicts a high-level view of the PAC setup.

<figure><img src="../../.gitbook/assets/private-access-channel.jpg" alt=""><figcaption></figcaption></figure>

The Wireguard server routes traffic to a specific network interface on Nginx.  The network interface on Nginx is configured to accept traffic for certain domain names only. Nginx forwards traffic to Istio ingress gateway of a cluster which further routes the traffic for these domains to respective resources in the cluster.  Note that a "resource group" is a group of Kubernetes resources, NOT, user groups.  Let's look at an end2end example:

_**RG1**_ is resource group for _\*.dev.openg2p.org_ and _\*.qa.openg2p.org._  We would like only developers to access these domains. The machine that runs Nginx is assumed to have multiple network interface cards (physical or virtual) with unique IPs for each of them.  In our example, we define an Nginx conf file (under `/etc/ngixn/sites-available`  for the above domains associated with _network interface 1_.  This interface has IP 172.29.16.40.  The conf files looks like below:

```
server {
	listen 172.29.16.40:443 ssl;
	server_name qa.openg2p.org *.qa.openg2p.org;

	ssl_certificate /etc/letsencrypt/live/qa.openg2p.org/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/qa.openg2p.org/privkey.pem;

	location / {
		proxy_pass                      http://openg2pClusterUpstream;
		proxy_http_version              1.1;
		proxy_buffering	                on;
		proxy_buffers                   8 16k;
		proxy_buffer_size               16k;
		proxy_busy_buffers_size         32k;
		proxy_set_header                Upgrade $http_upgrade;
		proxy_set_header                Connection "upgrade";
		proxy_set_header                Host $host;
		proxy_set_header                Referer $http_referer;
		proxy_set_header                X-Real-IP $remote_addr;
		proxy_set_header                X-Forwarded-Host $host;
		proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header                X-Forwarded-Proto $scheme;
		proxy_pass_request_headers      on;
	}
}
server {
	listen 172.29.16.40:443 ssl;
	server_name dev.openg2p.org *.dev.openg2p.org;

	ssl_certificate /etc/letsencrypt/live/dev.openg2p.org/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/dev.openg2p.org/privkey.pem;

	location / {
		proxy_pass                      http://openg2pClusterUpstream;
		proxy_http_version              1.1;
		proxy_buffering	                on;
		proxy_buffers                   8 16k;
		proxy_buffer_size               16k;
		proxy_busy_buffers_size         32k;
		proxy_set_header                Upgrade $http_upgrade;
		proxy_set_header                Connection "upgrade";
		proxy_set_header                Host $host;
		proxy_set_header                Referer $http_referer;
		proxy_set_header                X-Real-IP $remote_addr;
		proxy_set_header                X-Forwarded-Host $host;
		proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header                X-Forwarded-Proto $scheme;
		proxy_pass_request_headers      on;
	}
}

```

Note that we can have multiple server definitions for the same network interface (same IP) and all the traffic is forward to `openg2pClusterUpstream`  which points to nodes of one of the Kubernetes clusters.

Multiple Wireguard servers (bastions) can run on a single Virtual Machine (VM).  Similarly, multiple Nginx servers (vhosts) can run on a single Nginx instance.  Each network interface on Nginx has a unique IP. Each Nginx vhost forwards traffic to an Istio Ingress gateway server which further routes traffic to Kubernetes resources.  On the Istio Ingress gateway server,  gateways (or filters) are defined for each wildcard domain specifying the rule to forward traffic to the respective namespace on the cluster. See the example above.

In the above example, Users RG1 can access only RG1 domains.

## Clarifications and operational notes

### "Gateway 1", "Gateway 2" in the diagram are Istio configs, not separate Envoys

The diagram shows multiple gateways, which can read as multiple Istio ingress installations. They are not. They are **Istio `Gateway` CRDs** (configuration objects), all selecting the **same single Envoy ingressgateway pod** in the cluster:

```yaml
spec:
  selector:
    istio: ingressgateway        # one shared Envoy Deployment
  servers:
    - hosts: ["*.qa.openg2p.org"]
      port: { name: http2, number: 8080, protocol: HTTP2 }
```

The shared Envoy listens on the cluster's NodePort (typically `30080`). Routing inside Envoy is by **Host header** / SNI — each `Gateway` CRD declares hostnames it accepts; each `VirtualService` CRD maps a hostname to a backend service.

You only need a **second** Istio ingress Deployment when you want Envoy-layer policy separation (different rate limits, distinct mTLS policies, isolated blast radius). For pure hostname-based routing across channels, one Envoy is enough.

### Channel isolation is enforced at Nginx + Wireguard, not at Istio

Istio routes any hostname to any backend regardless of which "channel" logically owns it. The implicit security model is:

* Nginx is the only path to the K8s NodePort.
* The K8s NodePort is **not reachable from the network** by anyone else.
* Wireguard gates which users reach which Nginx interface.

{% hint style="warning" %}
If a deployment exposes the K8s NodePort publicly (or to a wider network than just Nginx), channel isolation collapses — anyone who knows a hostname can reach any service. Lock down the NodePort with cloud security groups and host-level firewall (e.g. `ufw` on the K8s node accepting `30080` only from the Nginx host's private IP).
{% endhint %}

### Wireguard channel granularity is per-server, not per-user

"All users with access to a Wireguard server have access to all channels to which the Wireguard server is connected" — channel granularity is the **Wireguard server**, not the individual peer. To split RG1 and RG2 access between two groups of users, run **two Wireguard servers** (each connected to a different Nginx network interface), and add peers to whichever WG server matches each user's intended access.

A single WG server with per-peer iptables rules is possible but adds operational complexity and isn't part of the standard PAC pattern.

### TLS certificates are per-server-block

Each Nginx `server` block needs its own (or a wildcard-covering) cert. Each block's `ssl_certificate` path must reference a cert that covers its `server_name`. Two patterns work:

* **One wildcard cert covering all hostnames in the channel** — smaller cert inventory, single rotation date. Best when the customer's CA allows wildcards.
* **One cert per FQDN** — larger inventory, finer rotation control. Common in regulated / government environments where wildcards are restricted by policy or CA. See [DNS & TLS Certificates](../concepts/dns-and-certificates.md) for why per-FQDN dominates gov deployments.

### Multi-NIC setup is non-trivial

The doc speaks of multiple network interfaces as if they're a given. Operationally:

* **AWS** — attach a secondary ENI (Elastic Network Interface) to the Nginx instance (limit varies by instance type, usually 2–8), then bring the address up on the OS side (`sudo ip addr add ...`). Some instance types allow hot-attach; others need a reboot.
* **Bare metal** — physical NICs or VLAN sub-interfaces.

For deployments that don't need multi-channel isolation (small pilots, single-tenant prod), single-NIC with one wildcard channel is fine. PAC's value scales with the number of distinct user groups requiring isolated access.

### Public access channels: same plumbing, no Wireguard

PAC as described above is for **private** access — Wireguard-gated. Citizen-facing **public** services (`registry.openg2p.org`, `payments.gov.eth`, etc.) follow the **same plumbing minus Wireguard**:

```
internet
  ↓
Nginx public NIC (public IP)
   server block: listen <public-IP>:443 ssl;
                 ssl_certificate <customer-cert>;
                 server_name registry.openg2p.org;
                 proxy_pass http://openg2pClusterUpstream;
  ↓
Same Istio ingressgateway (NodePort 30080)
  ↓
Istio Gateway CRD + VirtualService for the public hostname
  ↓
Service in the env namespace
```

Two operational differences from private channels:

1. **No Wireguard layer** — public traffic terminates on a public-IP NIC of the Nginx host.
2. **Customer-supplied certs** rather than the internal CA used for admin tools (commercial CA, ACME-issued via DNS-01, etc.).

The Istio side is identical to a private channel — a `Gateway` CRD with the public hostname, a `VirtualService` pointing at the right service. The shared Envoy doesn't care that one route came in via WG and another from the open internet.

### Hostname uniqueness across channels

A given hostname can be configured in **at most one** channel. If two channels both declare `*.qa.openg2p.org` (different Nginx interfaces, different Wireguard servers, different user groups), the Istio `Gateway` CRD for that hostname is a single cluster-wide resource — whichever `VirtualService` binds the hostname owns it. Channels effectively partition the **hostname namespace**; teams managing different channels must agree on the partition.

If you actually need the same hostname served to two distinct user groups with different backends, that's a separate design (typically traffic-splitting via headers, or two separate Istio ingressgateway Deployments with their own `selector`).


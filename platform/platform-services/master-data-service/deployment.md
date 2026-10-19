---
description: >-
  How the Master Data Service is installed (inside commons-services), the
  settings that matter at install, the object store for boundaries, approval
  mode and the public catalogue host
---

# Deployment

MDS is **not installed on its own**. It ships as part of the
**`commons-services`** Helm chart, with the other shared platform services. See
[Commons Helm Chart](../../../deployment/openg2p-commons-helm-chart.md).

* **Chart repository:** [`github.com/OpenG2P/commons`](https://github.com/OpenG2P/commons)
* **MDS chart:** `openg2p-master-data`, in the
  [MDS repository](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data)

{% hint style="warning" %}
**Version bumps must be made in `commons-services`.** Publishing a new MDS chart
or image does not change any deployment by itself: the version pinned in
`commons-services` is what an install gets. See [Versions](versions.md).
{% endhint %}

## One deployment serves one country

A deployment is seeded with exactly **one country pack**, declared in one place:

```yaml
masterData:
  geoSeed:
    countryPack: ETH    # MDS chart default: XKM, the fictitious demo country
```

Everything MDS holds belongs to that pack; there is no country field on the data.
A second country needs a second deployment. This keeps registry images
country-neutral: the same registry build serves any country, depending only on
the pack its MDS was seeded with.

## Settings at install

In `commons-services` the MDS values sit under `masterData.` Its Rancher form
shows the first four in the **Country Pack** group.

| Setting | Rancher label | Notes |
|---|---|---|
| `geoSeed.countryPack` | Country Pack | The pack's folder name in [`openg2p-data`](https://github.com/OpenG2P/openg2p-data), e.g. `ETH`, or `XKM` (fictitious). MDS chart default `XKM`; `commons-services` default `ETH` |
| `geoSeed.domains` | Dataset Themes | Themes to load besides the core datasets, as a list or comma-separated. Default `agriculture`. A theme the pack lacks is skipped with a warning |
| `geoSeed.load.codelists` | Load Datasets | On by default |
| `geoSeed.load.samples` | Load Sample People | On by default. **Turn it off in production** |
| `geoSeed.load.geo` | Load Geography (MDS chart form only) | On by default |
| `masterDataAPI.catalogue.approvalMode` | — | `permission` (default) or `awe`. See [Approval modes](change-control.md#approval-modes) |
| `masterDataAPI.catalogue.auditManagerUrl` | — | The Audit Manager; by default the one in `commons-services`. Empty turns audit off |
| `masterDataAPI.catalogue.websubHubUrl` | — | A WebSub hub for change notifications. Empty (default) turns them off |
| `masterDataAPI.catalogue.public.*` | Public catalogue (MDS chart form only) | Off by default. See [Public catalogue host](#public-catalogue-host) |
| `iamRegister.runAsHook` | — | MDS chart default `true` (a Helm hook); `commons-services` sets `false`, because an umbrella chart chains or skips hooks |

The country-pack loader has more flags (publish the first load directly,
auto-publish drafts, owner department); see
[Country Packs](country-packs.md#loader-settings).

## Object store for boundaries

Boundary files (GeoJSON) are kept in an **S3-compatible object store**: Garage in
the commons install (see
[Object store (Garage)](../../../deployment/openg2p-commons-helm-chart.md#object-store-garage)).
The country-pack loader uploads them, and the API serves and accepts them. Both
have their own settings; **keep them in step**:

| | Loader | API |
|---|---|---|
| Values | `geoSeed.objectStore.*` | `masterDataAPI.catalogue.boundaryStore.*` |
| Endpoint | `http://commons-garage:3900` in `commons-services` | the same |
| Bucket | `openg2p-geo` | the same |
| Credentials | Secret `commons-minio` (`root-user`, `root-password`) | the same |

The Secret keeps the name `commons-minio` for compatibility; the Garage init job
writes the credentials to it. The MDS chart on its own still defaults to
`http://commons-minio:9000`, so set the endpoint when installing it outside
`commons-services`. Set `publicBaseUrl` when browsers need a different address
than the in-cluster one.

Without an endpoint, the hierarchy still loads; only boundaries are missing.

## Approval through AWE

With `approvalMode: awe`, the chart also:

* creates the callback HMAC secret (`<release>-master-data-awe-callback-hmac`),
  kept across upgrades;
* with `awe.seed.enabled` (default on), registers the two approval policies (one
  for datasets, one for geography) and the callback secret in the shared AWE
  database. Approvers hold the client role `MASTER_DATA_APPROVER`;
  self-approval is forbidden. The stages can be changed in AWE afterwards.

If no AWE base URL is set, MDS falls back to `permission` mode.

## Public catalogue host

The [public catalogue](public-catalogue.md) is off by default. Its values are
under `masterDataAPI.catalogue.public`:

| Value | Default | Meaning |
|---|---|---|
| `enabled` | `false` | Serve `/public`. While off, every `/public` path answers 404 |
| `baseUrl` | `""` | Base of absolute links. Empty: taken from the request |
| `rateLimitPerMinute` | `60` | Per client IP and API worker; `0` disables |
| `trustedProxyHops` | `1` | Proxies that append to `X-Forwarded-For` |
| `cacheSeconds` | `300` | `Cache-Control` max-age |
| `title`, `publisher` | `Master data catalogue`, `""` | DCAT catalogue title and publisher |
| `istio.enabled`, `istio.host`, `istio.gateway` | `false`, `catalogue.<namespace>.openg2p.org`, `internal` | A separate host that routes **only** `/public/` to the API |

{% hint style="warning" %}
The default gateway is the **internal** one, so the catalogue is reachable on the
internal network only. Exposing it to the internet needs an internet-facing Istio
gateway, DNS and a TLS certificate for the host, and a decision that the datasets
marked public may be published. Consider a CDN or gateway rate limiting in front:
the API's limit is per worker and per pod.
{% endhint %}

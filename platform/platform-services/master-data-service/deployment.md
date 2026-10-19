---
description: >-
  How the Master Data Service is installed (inside commons-services), every
  setting that matters at install, the object store for boundaries, approval
  through AWE and the public catalogue host
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
`commons-services` is what an install gets. See [Software Versions](versions.md).
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
| `geoSeed.publishInitial` | — | On by default: a dataset's first load is published at once. Off: left as a draft for approval |
| `geoSeed.autoPublish` | — | Off by default. On: later loads are published at once, without approval. **Development and test only** |
| `geoSeed.ownerOrg` | — | Publisher recorded on what the loader creates. Empty by default |
| `global.authClientId` | — | The Keycloak client that holds the MDS permissions. Default `master-data` |
| `global.csrfEnabled` | — | Double-submit CSRF check on writes. On by default |
| `masterDataAPI.catalogue.approvalMode` | — | `permission` (default) or `awe`. See [Approval modes](change-control.md#approval-modes) and [Approval through AWE](#approval-through-awe) |
| `masterDataAPI.catalogue.defaultOwnerOrg` | — | Publisher given to datasets and the geography created without one; also the DCAT publisher when `public.publisher` is empty. Empty by default |
| `masterDataAPI.catalogue.effectiveRefreshSeconds` | — | How often MDS checks whether a future-dated version has taken effect, so a version takes effect at most this long after its date. Default `300`; `0` checks only on start and on publish |
| `masterDataAPI.catalogue.auditManagerUrl` | — | The Audit Manager; by default the one in `commons-services`. Empty turns audit off |
| `masterDataAPI.catalogue.websubHubUrl` | — | The WebSub hub for version notifications. `commons-services` points it at its own hub (`http://<release>-websub/hub`; installed by default). The MDS chart alone leaves it empty, which turns notifications off |
| `masterDataAPI.catalogue.public.*` | Public catalogue (MDS chart form only) | Off by default. See [Public catalogue host](#public-catalogue-host) |
| `iamRegister.runAsHook` | — | MDS chart default `true` (a Helm hook); `commons-services` sets `false`, because an umbrella chart chains or skips hooks |

Each `geoSeed` setting also has a loader command-line flag and environment
variable (see the chart's `values.yaml`). How loads work:
[Country Packs](country-packs.md#loading-and-upgrading-in-mds).

A few API settings have no chart value of their own. Set them as environment
variables under `masterDataAPI.envVars`:

| Environment variable | Default | Meaning |
|---|---|---|
| `MASTER_DATA_API_CATALOGUE_OUTBOX_RELAY_SECONDS` | `30` | How often the API retries change events not yet accepted by the Audit Manager or WebSub (see [Audit](change-control.md#audit)), and how often each worker notices a publish made by another and drops its cache of the original `/attributes` and `/geo` reads. `0` turns both off |
| `MASTER_DATA_API_CACHE_EXPIRE_SECONDS` | `300` | The longest a cached original `/attributes` or `/geo` read is kept |

## Object store for boundaries

Boundary files (GeoJSON) are kept in an **S3-compatible object store**: Garage in
the commons install (see
[Object store (Garage)](../../../deployment/openg2p-commons-helm-chart.md#object-store-garage)).
Database rows hold only each file's key. The country-pack loader uploads the
files, and the API serves and accepts them. Both have their own settings; **keep
them in step**:

| | Loader | API |
|---|---|---|
| Values | `geoSeed.objectStore.*` | `masterDataAPI.catalogue.boundaryStore.*` |
| Endpoint | `http://commons-garage:3900` in `commons-services` | the same |
| Bucket | `openg2p-geo` | the same |
| Credentials | Secret `commons-minio` (`root-user`, `root-password`) | the same |

The Garage init job writes the credentials to the `commons-minio` Secret; the MDS
chart on its own defaults to `http://commons-minio:9000`, so set the endpoint when
installing it outside `commons-services`. Set `publicBaseUrl` when browsers need
a different address than the in-cluster one.

Without an endpoint, the hierarchy still loads; only boundaries are missing.

## Approval through AWE

The AWE values are under `masterDataAPI.catalogue.awe`:

| Value | Default | Meaning |
|---|---|---|
| `baseUrl` | `""` | AWE's in-cluster address. Empty: MDS falls back to `permission` mode |
| `policyKeyList`, `policyKeyGeo` | `master_data.list_version.v1`, `master_data.geo_version.v1` | The AWE policies for datasets and for geography |
| `seed.enabled` | `true` | Register the two policies and the callback secret in AWE's database |

With `approvalMode: awe`, the chart also:

* creates the callback HMAC secret (`<release>-master-data-awe-callback-hmac`),
  kept across upgrades;
* with `seed.enabled`, registers the two approval policies and the callback
  secret in the shared AWE database. Approvers hold the client role
  `MASTER_DATA_APPROVER`; self-approval is forbidden. The stages can be changed
  in AWE afterwards.

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
| `title`, `publisher` | `Master data catalogue`, `""` | DCAT catalogue title and publisher (empty: `catalogue.defaultOwnerOrg`) |
| `istio.enabled`, `istio.host`, `istio.gateway` | `false`, `catalogue.<namespace>.openg2p.org`, `internal` | A separate host that routes **only** `/public/` to the API |

The language of the plain labels in SKOS and DCAT is the environment variable
`MASTER_DATA_API_PUBLIC_CATALOGUE_DEFAULT_LANGUAGE` (default `en`), set under
`masterDataAPI.envVars`.

{% hint style="warning" %}
The default gateway is the **internal** one, so the catalogue is reachable on the
internal network only. Exposing it to the internet needs an internet-facing Istio
gateway, DNS and a TLS certificate for the host, and a decision that the datasets
marked public may be published. Consider a CDN or gateway rate limiting in front:
the API's limit is per worker and per pod.
{% endhint %}

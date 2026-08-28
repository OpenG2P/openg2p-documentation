---
description: Geography, code lists, partners and sample data — shared across the platform
---

# Master Data Service

The **Master Data Service** (MDS) is where OpenG2P keeps the reference data that
more than one service needs, so it is defined once and reused everywhere.

## What it contains

* **Geography** — the administrative hierarchy for the country this deployment
  serves, every administrative unit with its **P-code**, and a link to where each
  unit's map shape can be fetched.
* **Code lists** — the country's own vocabularies: genders, education levels,
  water sources, crops and so on, with their values.
* **Sample people** — a few dozen individuals and households belonging to the
  country, used for demos and smoke tests.
* **Partners** — the register of partner organisations (mnemonics, key-manager
  reference IDs, active status) used for inter-service trust and routing.

The first three come from a **country pack**. What a pack is, where packs live and
how a country is configured end to end is covered in
[Country Data Architecture](../../country-data-architecture.md) — this page does
not repeat it.

## What it serves, and to whom

| Consumer | What it takes | How |
|---|---|---|
| **Registries** (NSR, Farmer Registry, …) | Code lists, the geo hierarchy, sample people | At **install**, copied into the registry's own tables |
| **Staff portal screens** | Geo units, level by level | At **runtime**, via the Geo API — this is what fills cascading address dropdowns |
| **Bulk data generators** | The hierarchy and code lists | At install, so generated records point at real units |
| **PBMS, Bridge, SPAR** | Partner and geo lookups | At runtime, via the APIs |
| **Map and reporting surfaces** | Map shapes | From the country pack at build time — **not** from MDS at runtime |

{% hint style="info" %}
**Registries depend on MDS at install time, not on every write.** A registry copies
what it needs into its own tables during seeding and validates against that copy
afterwards. MDS being unavailable later does not stop a registration.
{% endhint %}

See the [API Reference](api-reference.md) for the endpoints themselves.

## One deployment serves one country

MDS is **single-tenant with respect to country**. A deployment is seeded with
exactly one country pack, declared in one place:

```yaml
geoSeed:
  countryPack: ETH      # the single place a deployment declares its country
```

Everything MDS holds — the hierarchy, the code lists, the sample people — belongs
to that pack. There is no country dimension on the data and no way to serve two
countries from one instance; serving a second country means a second deployment.

This is what keeps registry images country-agnostic: the same registry build
serves Ethiopia or Kamuntu depending only on which pack the MDS beside it was
seeded with.

## Source code

{% hint style="warning" %}
**The code has moved from GitHub to GitLab.** The GitHub repository is frozen and
no longer receives changes.
{% endhint %}

* **Repository:** [`gitlab.com/openg2p/master-data-service`](https://gitlab.com/openg2p/master-data-service)

One repository holds all of the service's parts together — the FastAPI
application, the Docker image build, the Helm chart, and the country-pack seeder.

## Versions

Versions are tracked in the changelog published by CI:

* **[Master Data Service changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html)**

## Deployment

MDS is **not installed on its own**. It ships as part of the **`commons-services`**
Helm chart, alongside the other shared platform services.

* **Chart repository:** [`gitlab.com/openg2p/commons`](https://gitlab.com/openg2p/commons)

{% hint style="warning" %}
**Version bumps must be made in `commons-services`.** Publishing a new Master Data
chart or image does not change any deployment by itself — the version pinned in
the `commons-services` chart is what an install actually gets. A new MDS version
that is not picked up there is a version nobody runs.
{% endhint %}

Country-pack selection (`geoSeed.countryPack`, and which parts of the pack to
load) is therefore also configured through `commons-services`.

## Legacy versions

{% hint style="info" %}
Superseded by the [changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html)
above, and retained for history. These rows point at the former GitHub repository
and at Docker Hub images predating the move to GitLab.
{% endhint %}

<table><thead><tr><th width="160">Helm version</th><th width="280">Master Data Docker</th><th width="130">Last modified</th><th>Comments</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data">0.0.0-develop.8</a></td><td><a href="https://hub.docker.com/r/openg2p/master-data-api/tags">master-data-api:develop</a></td><td>10-Jul-2026</td><td>Changes since <a href="https://github.com/OpenG2P/master-data-service/commit/2ac3823aeb99baa0c6d91360058109992d8fc8ff"><code>2ac3823</code></a>: registry-DB integration + IAM auth for geo data-policy resolution; new geo-level APIs; <code>0.0.0-develop.N</code> chart versioning.</td></tr><tr><td><a href="https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data">0.0.0-develop</a></td><td><a href="https://hub.docker.com/r/openg2p/master-data-api/tags">master-data-api:develop</a></td><td>15-Jun-2026</td><td><ol><li><strong>Single consolidated repository</strong> <code>master-data-service</code> — master-data source, Docker image, and the Helm chart now live in one repo (previously three separate repositories).</li><li>Single Helm chart <code>openg2p-master-data</code> under <code>deployments/charts</code>.</li><li>Docker image is built from local in-repo source and tagged with the repository ref — on <code>develop</code> the image is tagged <code>develop</code>.</li></ol></td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-gen2-master-data-deployment/tree/1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-gen2-master-data-api/1.0.0/images/sha256-4739fd732e051c0102bea6245a01e3cfc479f00e71729a5e1640e27d475406a9">openg2p-gen2-master-data-api:v1.0.0</a></td><td>17-Apr-2026</td><td><ol><li>Initial version of the Master Data API — Partners and Geo lookup data.</li></ol><p><mark style="color:red;">THIS VERSION HAS BUGS</mark>. Use <code>develop</code>.</p></td></tr></tbody></table>

{% hint style="info" %}
On the `develop` branch the Docker image is tagged `develop` (the image tag always matches the `master-data-service` repository ref — a branch name or git tag). The Helm chart's base version is `0.0.0-develop`, but each publish appends the CI run number, so the artifact published to the Helm repo is `0.0.0-develop.<run-number>` (this keeps Rancher / the GH-Pages CDN from serving a stale cached chart). Release branches publish `N.N.0-develop.<run-number>`, and frozen `N.N.N` releases carry that semantic version with no suffix. The **Last modified** date of the `0.0.0-develop` row should be updated whenever that version changes.
{% endhint %}

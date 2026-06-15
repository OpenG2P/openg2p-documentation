---
description: Master / Reference data for PBMS, Registry, Bridge and SPAR
---

# Master Data Service

The **Master Data Service** is the OpenG2P source of master / reference
data shared across the platform. It holds and serves the common lookup data that
other services depend on — primarily:

* **Geographic data** — the location / administrative-area hierarchy used to
  qualify addresses and target programs.
* **Partner data** — the registry of partner organisations (mnemonics,
  key-manager reference IDs, active status) used for inter-service trust and
  routing.

It exposes simple read/lookup APIs (Geo and Partner) consumed by **PBMS,
Registry, Bridge and SPAR**, so master data is defined once and reused
consistently everywhere.

## Repository organisation

Everything for this service lives in a single consolidated repository:

* **Repository:** [`master-data-service`](https://github.com/OpenG2P/master-data-service)

This one repo contains all of the service's parts together — the application
**code** (the FastAPI master-data API), the **Docker** image build, and the
**Helm** chart used to deploy it. It replaces what were previously three
separate repositories (one each for the code, the Docker build, and the Helm
chart).

## Versions

<table><thead><tr><th width="160">Helm version</th><th width="280">Master Data Docker</th><th width="130">Last modified</th><th>Comments</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data">0.0.0-develop</a></td><td><a href="https://hub.docker.com/r/openg2p/master-data-api/tags">master-data-api:develop</a></td><td>15-Jun-2026</td><td><ol><li><strong>Single consolidated repository</strong> <code>master-data-service</code> — master-data source, Docker image, and the Helm chart now live in one repo (previously three separate repositories).</li><li>Single Helm chart <code>openg2p-master-data</code> under <code>deployments/charts</code>.</li><li>Docker image is built from local in-repo source and tagged with the repository ref — on <code>develop</code> the image is tagged <code>develop</code>.</li></ol></td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-gen2-master-data-deployment/tree/1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-gen2-master-data-api/1.0.0/images/sha256-4739fd732e051c0102bea6245a01e3cfc479f00e71729a5e1640e27d475406a9">openg2p-gen2-master-data-api:v1.0.0</a></td><td>17-Apr-2026</td><td><ol><li>Initial version of the Master Data API — Partners and Geo lookup data.</li></ol><p><mark style="color:red;">THIS VERSION HAS BUGS</mark>. Use <code>develop</code>.</p></td></tr></tbody></table>

{% hint style="info" %}
On the `develop` branch the chart version is `0.0.0-develop` and the Docker image is tagged `develop` (the image tag always matches the `master-data-service` repository ref — a branch name or git tag). Tagged releases will carry semantic versions here. The **Last modified** date of the `0.0.0-develop` row should be updated whenever that version changes.
{% endhint %}

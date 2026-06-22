---
description: G2P Bridge Versions
---

# Versions

{% hint style="warning" %}
**Two similarly-named Helm charts — make sure you pick the right one.**

* The **current, consolidated** chart is named **`openg2p-bridge`**, its Docker images are all prefixed **`openg2p-bridge-*`**, and in the **Rancher** catalog it appears as **“OpenG2P Bridge”**. This is the one to install for any new deployment (see [G2P Bridge Helm Package](#g2p-bridge-helm-package) below).
* The **legacy**, multi-chart line is named **`openg2p-g2p-bridge`**, its Docker images are all prefixed **`openg2p-g2p-bridge-*`**, and in **Rancher** it appears as **“OpenG2P G2P Bridge”** (see [Legacy Versions](#legacy-versions) below).

The two differ only by an extra **`g2p`** — `openg2p-bridge` vs `openg2p-`**`g2p-`**`bridge`, and “OpenG2P Bridge” vs “OpenG2P **G2P** Bridge” — so they are very easy to confuse in the Rancher app list, and they are **not compatible** with each other. For a fresh install, always choose **`openg2p-bridge` (“OpenG2P Bridge”)**.
{% endhint %}

## G2P Bridge Helm Package

The G2P Bridge is now installed from a **single, consolidated Helm chart** —
[`openg2p-bridge`](https://github.com/OpenG2P/g2p-bridge/tree/develop/deployment/charts/openg2p-bridge).
One chart installs the complete subsystem: the partner & beneficiary-portal APIs,
the Celery beat producer and workers, a bundled Redis, the PostgreSQL
database/role (via `postgres-init`), the Keycloak OIDC client (via
`keycloak-init`), and — optionally — the bundled **Example Bank** simulator. All
source now lives in one repository, [`g2p-bridge`](https://github.com/OpenG2P/g2p-bridge).

All Docker images for this chart share the **`openg2p-bridge-*`** prefix — e.g.
`openg2p-bridge-partner-api`, `openg2p-bridge-bene-portal-api`, `openg2p-bridge-celery`,
and `openg2p-bridge-example-bank-*` for the bundled Example Bank.

<table><thead><tr><th width="180">Helm Chart &#x26; Version</th><th>G2P Bridge Runtimes</th><th width="123">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-bridge</code></strong><br>(Rancher: “OpenG2P Bridge”)<br><br><a href="https://github.com/OpenG2P/g2p-bridge/tree/develop/deployment/charts/openg2p-bridge">0.0.0-develop</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-partner-api/tags">openg2p-bridge-partner-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-bene-portal-api/tags">openg2p-bridge-bene-portal-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-celery/tags">openg2p-bridge-celery:develop</a><br>(single image, run as beat <em>and</em> worker)<br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-api/tags">openg2p-bridge-example-bank-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-beat-producers/tags">openg2p-bridge-example-bank-celery-beat-producers:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-workers/tags">openg2p-bridge-example-bank-celery-workers:develop</a></td><td>02-Jun-2026</td><td><ol><li><strong>Single consolidated chart for the complete installation.</strong> All previous sub-charts (api, celery, bene-portal, example-bank) are folded into one chart, <code>openg2p-bridge</code>. <mark style="color:red;">Incompatible with previous Helm chart versions.</mark></li><li>Source consolidated into a <strong>single repository</strong>, <code>g2p-bridge</code> (previously seven repos).</li><li>Added Keycloak client provisioning via the <code>keycloak-init</code> subchart — creates the <code>g2p-bridge</code> OIDC client in the <code>staff</code> realm. <a href="deployment/keycloak-client.md">Learn more &gt;&gt;</a></li><li><strong>Digital cash transfer needs no PBMS or Registry.</strong> The sponsor/treasury account is configured directly in Helm values and the same values seed the bundled Example Bank. In-kind disbursements (which need PBMS/Registry) are behind <code>g2pBridgeInKindEnabled</code>. <a href="deployment/deployment-of-example-bank.md">Learn more &gt;&gt;</a></li><li>Single Celery Docker image, run as beat producer or worker by Helm configuration.</li><li>Added an <a href="deployment/teardown.md">uninstall script</a> that fully removes the release and its Postgres database/role while preserving the shared Postgres instance and other components' data.</li></ol></td></tr></tbody></table>

{% hint style="info" %}
On the `develop` branch the chart is published as `0.0.0-develop.<run-number>`
(the single rolling row above represents this dev line). Docker images are tagged
independently by their own build workflows — `develop` on the develop branch (the
tag matches the `g2p-bridge` repo ref). See
[How the chart version is assigned](#how-the-chart-version-is-assigned) below.
{% endhint %}

### How the chart version is assigned

The **published Helm chart version is derived from the branch name** at publish
time and injected via `helm package --version`; the `version:` field in
`Chart.yaml` is only a placeholder. A unique **run-number suffix** on development
builds guarantees Rancher and the GitHub-Pages CDN never serve a stale, cached
chart (they cache by chart-name + version).

| Branch | Published chart version |
| --- | --- |
| `develop` | `0.0.0-develop.<run-number>` |
| `N.N` (e.g. `1.0`) | `N.N.0-develop.<run-number>` (Helm needs a 3-part SemVer) |
| `N.N.N` (e.g. `1.0.0`) | `N.N.N` — frozen release, no suffix |
| anything else | not published (unless overridden — see below) |

This is the **Helm chart version only** — independent of the Docker image tags in
the table above. A few notes:

* **Pre-releases are hidden by default:** `helm search` / `helm install` need
  `--devel` to see `*-develop.*` builds. Rancher lists them but only treats a
  frozen `N.N.N` as "latest".
* **One-off / custom version:** run the **Publish G2P Bridge Helm chart** workflow
  manually (Actions → *Run workflow*) with an explicit `version` (e.g.
  `1.0.0-g2p5466`) to bypass the branch gate. CLI equivalent:
  `gh workflow run "Publish G2P Bridge Helm chart" --ref <branch> -f version=1.0.0-g2p5466`.
* The table above keeps **one rolling `0.0.0-develop` row** for the dev line
  (suffixed builds are not listed individually); a new row is added only when a
  `N.N.N` version is frozen.

***

## Legacy Versions

These versions predate the repository/chart consolidation. They were built from
the older multi-repository layout (`openg2p-g2p-bridge-deployment`,
`openg2p-g2p-bridge-example-bank-deployment`, etc.) with a separate chart per
service. They are **not compatible** with the consolidated chart above.

Their Docker images use the **`openg2p-g2p-bridge-*`** prefix (the extra `g2p`) —
e.g. `openg2p-g2p-bridge-partner-api`, `openg2p-g2p-bridge-celery-workers` — which
is what distinguishes them from the current chart's `openg2p-bridge-*` images.

<table><thead><tr><th width="170">Helm Chart &#x26; Version</th><th width="298">G2P Bridge Runtimes</th><th width="153">Version date</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-g2p-bridge</code></strong><br>(Rancher: “OpenG2P G2P Bridge”)<br><br><a href="https://github.com/OpenG2P/openg2p-g2p-bridge-deployment/tree/3.0.0">3.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-beat-producers/2.1.0/images/sha256-75edd2dc6b7ad52a679f8e2942263f0718c95ee1016973d463900d3961a481c2">openg2p-g2p-bridge-celery-beat-producers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-workers/2.1.0/images/sha256-736e8872e04993a0e974d56b586c628b5de5ad6ce01b7069a2cbd801f5c86a69">openg2p-g2p-bridge-celery-workers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-partner-api/2.1.0/images/sha256-ea58a48364306cb26124d7af31a486564976dca5222c284dadac13e8a0b345ca">openg2p-g2p-bridge-partner-api:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-bene-portal-api/2.1.0/images/sha256-56b4bc531d25fc0fd71a0adb613b00514a923987801e2b2a0a7a082beb5b606f">openg2p-g2p-bridge-bene-portal-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Complete overhaul of Helm chart. Multiple charts combined into one. <mark style="color:red;">Incompatible with previous Helm chart versions</mark>.</li><li>Embraced new headers from openg2p-fastapi-common</li><li>Caters to cash-digital, cash-physical, commodities and services</li><li>Interfaces to Warehouses and Agents for physical goods &#x26; services</li><li>In line with PBMS Gen2 capabilities</li><li>Introduced Adapter pattern for SPAR</li></ol></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>2.0.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.1.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.0.2</td><td></td><td>06 Dec 2024</td><td><a href="releases/1.0.2.md">Release contents</a></td></tr></tbody></table>

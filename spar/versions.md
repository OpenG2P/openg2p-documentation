---
description: SPAR Versions
---

# Versions

{% hint style="warning" %}
**Two similarly-named Helm charts — make sure you pick the right one.**

* The **current, consolidated** chart is named **`openg2p-spar`** and appears in the **Rancher** catalog as **“OpenG2P SPAR”**. This is the one to install for any new deployment (see [SPAR Helm Package](versions.md#spar-helm-package) below).
* The **legacy** chart is named **`spar`** (see [Legacy Versions](versions.md#legacy-versions) below).

The two differ by the chart name — **`openg2p-spar`** vs **`spar`** — so they are easy to confuse in the Rancher app list, and they are **not compatible** with each other. For a fresh install, always choose **`openg2p-spar` (“OpenG2P SPAR”)**. (Both lines use the same `openg2p-spar-*` Docker images, so the chart name is what distinguishes them.)
{% endhint %}

## SPAR Helm Package

SPAR is now installed from a **single, consolidated Helm chart** — [`openg2p-spar`](https://github.com/OpenG2P/spar/tree/develop/deployment/charts/openg2p-spar). One chart installs the complete subsystem: the Mapper Partner API, the Beneficiary Portal API, the PostgreSQL database/role (via `postgres-init`), the Keycloak realms/clients (via `keycloak-init`), and the SPAR reference (strategy) seed data. All source lives in one repository, [`spar`](https://github.com/OpenG2P/spar).

<table><thead><tr><th width="180">Helm Chart &#x26; Version</th><th>SPAR Runtimes</th><th width="123">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-spar</code></strong><br>(Rancher: “OpenG2P SPAR”)<br><br><a href="https://github.com/OpenG2P/spar/tree/develop">0.0.0-develop.26</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-partner-api/tags">openg2p-spar-mapper-partner-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-spar-bene-portal-api/tags">openg2p-spar-bene-portal-api:develop</a></td><td>01-Jul-2026</td><td><p><strong>Rolling <code>develop</code> build.</strong> Major changes vs 1.0.0:</p><ol><li><strong>Local in-process JWS signature verification</strong> via <code>openg2p-fastapi-common</code> (PyJWTCryptoHelper) — MOSIP <strong>Keymanager no longer used</strong> — verification is in-process (a <code>keymanager</code> backend remains only for legacy/1.0.0 compatibility). SPAR only verifies (no signing key).</li><li><strong>Partner signature verification ON by default</strong>: partner public certs seeded in DB (<code>partner_keys</code>); the trial seeds the G2P Bridge test cert as <code>PARTNER_G2P_BRIDGE</code> so signed Bridge→SPAR resolve verifies out of the box.</li><li>Branch-derived rolling Helm chart versioning (<code>0.0.0-develop.&#x3C;run></code>).</li></ol></td></tr><tr><td><strong><code>openg2p-spar</code></strong><br>(Rancher: “OpenG2P SPAR”)<br><br><a href="https://github.com/OpenG2P/spar/tree/1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-partner-api/tags">openg2p-spar-mapper-partner-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-spar-bene-portal-api/tags">openg2p-spar-bene-portal-api:1.0.0</a></td><td>27-Jun-2026</td><td><p><strong>Stable version</strong></p><p></p><ol><li>Signature verification via <strong>MOSIP Keymanager</strong>; added Keycloak client provisioning via the <code>keycloak-init</code> subchart (the <code>openg2p-spar</code> OIDC client in the <code>staff</code> realm authenticates the Mapper API to Keymanager). From <code>develop</code> this is replaced by in-process local verification.</li><li>Aligned Keycloak/auth configuration with NSR conventions — shared settings moved under <code>global</code> to avoid duplication.</li><li>Fixed Helm rendering errors (<code>sparMapperAPI</code> values key, ingress host, env-var handling) and bumped Istio VirtualServices to <code>networking.istio.io/v1beta1</code>.</li><li>Added an uninstall script that fully removes the release and its Postgres database/role while keeping Keycloak client secrets intact.</li></ol></td></tr></tbody></table>

{% hint style="info" %}
On the `develop` branch the chart is published as `0.0.0-develop.<run-number>` (the row above shows the latest such build). Docker images are tagged independently by their own build workflows — `develop` on the develop branch (the tag matches the `openg2p-spar` repo ref). See [How the chart version is assigned](versions.md#how-the-chart-version-is-assigned) below.
{% endhint %}

### How the chart version is assigned

The **published Helm chart version is derived from the branch name** at publish time and injected via `helm package --version`; the `version:` field in `Chart.yaml` is only a placeholder. A unique **run-number suffix** on development builds guarantees Rancher and the GitHub-Pages CDN never serve a stale, cached chart (they cache by chart-name + version).

| Branch                 | Published chart version                                   |
| ---------------------- | --------------------------------------------------------- |
| `develop`              | `0.0.0-develop.<run-number>`                              |
| `N.N` (e.g. `1.0`)     | `N.N.0-develop.<run-number>` (Helm needs a 3-part SemVer) |
| `N.N.N` (e.g. `1.0.0`) | `N.N.N` — frozen release, no suffix                       |
| anything else          | not published (unless overridden — see below)             |

This is the **Helm chart version only** — independent of the Docker image tags in the table above. A few notes:

* **Pre-releases are hidden by default:** `helm search` / `helm install` need `--devel` to see `*-develop.*` builds. Rancher lists them but only treats a frozen `N.N.N` as "latest".
* **One-off / custom version:** run the **Publish SPAR Helm chart** workflow manually (Actions → _Run workflow_) with an explicit `version` (e.g. `1.0.0-g2p5466`) to bypass the branch gate. CLI equivalent: `gh workflow run "Publish SPAR Helm chart" --ref <branch> -f version=1.0.0-g2p5466`.
* The table above lists the **current `0.0.0-develop.<run>` build** for the dev line (updated on notable dev changes; intermediate suffixed builds are not listed individually); a frozen `N.N.N` row is added on release.

***

## Legacy Versions

These versions predate the chart consolidation. They were built from the older `openg2p-spar-deployment` layout with the chart named **`spar`** (a separate chart per service). They are **not compatible** with the consolidated `openg2p-spar` chart above.

<table><thead><tr><th width="170">Helm Chart &#x26; Version</th><th>SPAR Runtimes</th><th width="153">Version date</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>spar</code></strong><br><br><a href="https://github.com/OpenG2P/openg2p-spar-deployment/tree/2.0.0">2.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-bene-portal-api/2.1.0/images/sha256-dd192b4ba2b36b165407e531b387405356f9017a7f791554139e48c78a6ddadd">spar-bene-portal-api:v2.1.0</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-mapper-partner-api/2.1.0/images/sha256-ac9a12f476b53adb0751f66b0ce032ce1d4f0c3346b3918ae56e4b9b0e55f8aa">spar-mapper-partner-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Incompatible changes w.r.t previous versions. <a href="deployment/helm-charts.md">Learn more >></a></li><li>Moved to Common Headers of openg2p-fastapi-common</li><li>Removed self-service-api and introduced spar-bene-portal-api — in line with OpenG2P Architecture</li><li>Removed spar-mapper-api and introduced spar-partner-api — in line with OpenG2P Architecture</li><li>Rationalized DFSP models (in bene portal, erstwhile self-service) to simplified — BANK, BRANCH and WALLET-PROVIDER models</li></ol></td></tr><tr><td><code>spar</code><br>1.1.0</td><td></td><td>03-Nov-2025</td><td></td></tr><tr><td><code>spar</code><br>1.0.0</td><td></td><td>03-May-2024</td><td><a href="releases/release-notes.md">Release contents</a></td></tr></tbody></table>

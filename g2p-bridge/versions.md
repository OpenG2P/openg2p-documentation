---
description: G2P Bridge Versions
---

# Versions

{% hint style="info" %}
**For the current versions, changelogs, and the exact Helm chart & Docker image links, go here:**

## 👉 [G2P Bridge — Versions & Changelog](https://openg2p.gitlab.io/versions/g2p-bridge-g2p-bridge/CHANGELOG.html)

That page is **generated on every build and is always up to date**. The
[historical tables](#historical-versions) further down are kept only as a record of the
pre-GitLab builds.
{% endhint %}

## How versioning & publishing work

G2P Bridge is now built and published **entirely on GitLab** (previously GitHub + Docker
Hub), using OpenG2P's shared Helm & Docker packaging pipeline. In brief:

* **One immutable version per commit** — `0.0.0-develop.<n>` on `develop` (by commit
  ordinal) and a frozen `N.N.N` on release (promote-on-release). A version is never
  rebuilt or overwritten.
* **Helm charts** are published to the **shared OpenG2P Helm registry**, so one
  Rancher/Helm repo lists every OpenG2P chart (Bridge included):
  [gitlab.com/groups/openg2p/-/packages](https://gitlab.com/groups/openg2p/-/packages).
* **Docker images** live in **each repo's own Container Registry** — the Bridge's are at
  `registry.gitlab.com/openg2p/g2p-bridge/g2p-bridge/<name>` (`partner-api`,
  `bene-portal-api`, `celery`, `example-bank-*`).
* **Changelogs** are generated from commit messages onto the changelog page linked above.

This scheme is the same across all OpenG2P repos and is documented once — for the full
details see
**[Helm & Docker Versioning Strategy and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci)**.

***

## Historical versions

The tables below are a **read-only record of builds published before the GitLab move** —
Docker Hub images and the GitHub `openg2p-helm` chart. They are **not** updated for GitLab
builds; for those, always use the [changelog page](https://openg2p.gitlab.io/versions/g2p-bridge-g2p-bridge/CHANGELOG.html) above.

{% hint style="warning" %}
**Two similarly-named charts — don't confuse them.** The **current** chart is
**`openg2p-bridge`** (images `openg2p-bridge-*`; Rancher: “OpenG2P Bridge”). The
**legacy** line is **`openg2p-g2p-bridge`** (images `openg2p-g2p-bridge-*` — the extra
`g2p`; Rancher: “OpenG2P G2P Bridge”). They differ by a single `g2p`, are easy to confuse
in the Rancher list, and are **not compatible**. For any new install use
**`openg2p-bridge`**.
{% endhint %}

### Previous versions

The last builds of the **current** `openg2p-bridge` chart under the old (Docker Hub +
GitHub `openg2p-helm`) scheme, up to `1.0.0` and the final `0.0.0-develop.<run>` dev build:

<table><thead><tr><th width="180">Helm Chart &#x26; Version</th><th>G2P Bridge Runtimes</th><th width="123">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-bridge</code></strong><br>(Rancher: “OpenG2P Bridge”)<br><br><a href="https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/tree/develop">0.0.0-develop.41</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-partner-api/tags">openg2p-bridge-partner-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-bene-portal-api/tags">openg2p-bridge-bene-portal-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-celery/tags">openg2p-bridge-celery:develop</a><br><br>openg2p-bridge-example-bank-{api,celery-beat-producers,celery-workers}:develop</td><td>01-Jul-2026</td><td><p><strong>Rolling <code>develop</code> build.</strong> Major changes vs 1.0.0:</p><ol><li><strong>Partner signatures verified via the Partner Manager (PM) service</strong> (openg2p-fastapi-common <code>PartnerMgmtKeyStore</code>) — no MOSIP Keymanager and no local key store; the Bridge fetches partner public keys from PM.</li><li><strong>Partner API signature validation enabled by default in the chart</strong> (secure-by-default; the app-config default is off): inbound verify + signed Bridge→SPAR resolve. Partners (incl. <code>PARTNER_G2P_BRIDGE</code>) are onboarded in Partner Manager — the trial's <code>pm-seed</code> Job does this automatically.</li><li>Local <code>.p12</code> signing key with demo / inline / existing-secret modes.</li><li>Sanity smoke + e2e run as a post-install hook by default (can fail the deploy).</li><li>Deployment hardening: pre-upgrade DB password-sync hook + fail-loud <code>migrate</code>.</li></ol></td></tr><tr><td><strong><code>openg2p-bridge</code></strong><br>(Rancher: “OpenG2P Bridge”)<br><br><a href="https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/tree/v1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-partner-api/tags">openg2p-bridge-partner-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-bene-portal-api/tags">openg2p-bridge-bene-portal-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-celery/tags">openg2p-bridge-celery:1.0.0</a><br>(single image, run as beat <em>and</em> worker)<br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-api/tags">openg2p-bridge-example-bank-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-beat-producers/tags">openg2p-bridge-example-bank-celery-beat-producers:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-workers/tags">openg2p-bridge-example-bank-celery-workers:1.0.0</a></td><td>26-Jun-2026</td><td><p><strong>Intermediate Stable Version</strong></p><ol><li><strong>Single consolidated chart for the complete installation.</strong> <mark style="color:red;">Incompatible with previous Helm chart versions.</mark></li><li>Source consolidated into a <strong>single repository</strong>, <code>g2p-bridge</code> (previously seven repos).</li><li>Added Keycloak client provisioning via the <code>keycloak-init</code> <a href="deployment/keycloak-client.md">Learn more >></a></li><li><strong>Digital cash transfer needs no PBMS or Registry.</strong> <a href="deployment/deployment-of-example-bank.md">Learn more >></a></li><li>Single Celery Docker image, run as beat producer or worker by Helm configuration.</li><li>Added an <a href="deployment/teardown.md">uninstall script</a> that fully tears down the release cleanly</li><li><strong>Partner API authentication is disabled by default in this version</strong> — inbound signature validation is off; when enabled, 1.0.0 validates signatures via <strong>MOSIP Keymanager</strong> (the <code>keycloak-init</code> client authenticates to it). From <code>develop</code> this is replaced by in-process local JWS (no Keymanager).</li></ol></td></tr></tbody></table>

***

## Legacy Versions

These versions predate the repository/chart consolidation. They were built from the older multi-repository layout (`openg2p-g2p-bridge-deployment`, `openg2p-g2p-bridge-example-bank-deployment`, etc.) with a separate chart per service. They are **not compatible** with the consolidated chart above.

Their Docker images use the **`openg2p-g2p-bridge-*`** prefix (the extra `g2p`) — e.g. `openg2p-g2p-bridge-partner-api`, `openg2p-g2p-bridge-celery-workers` — which is what distinguishes them from the current chart's `openg2p-bridge-*` images.

<table><thead><tr><th width="170">Helm Chart &#x26; Version</th><th width="298">G2P Bridge Runtimes</th><th width="153">Version date</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-g2p-bridge</code></strong><br>(Rancher: “OpenG2P G2P Bridge”)<br><br><a href="https://github.com/OpenG2P/openg2p-g2p-bridge-deployment/tree/3.0.0">3.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-beat-producers/2.1.0/images/sha256-75edd2dc6b7ad52a679f8e2942263f0718c95ee1016973d463900d3961a481c2">openg2p-g2p-bridge-celery-beat-producers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-workers/2.1.0/images/sha256-736e8872e04993a0e974d56b586c628b5de5ad6ce01b7069a2cbd801f5c86a69">openg2p-g2p-bridge-celery-workers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-partner-api/2.1.0/images/sha256-ea58a48364306cb26124d7af31a486564976dca5222c284dadac13e8a0b345ca">openg2p-g2p-bridge-partner-api:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-bene-portal-api/2.1.0/images/sha256-56b4bc531d25fc0fd71a0adb613b00514a923987801e2b2a0a7a082beb5b606f">openg2p-g2p-bridge-bene-portal-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Complete overhaul of Helm chart. Multiple charts combined into one. <mark style="color:red;">Incompatible with previous Helm chart versions</mark>.</li><li>Embraced new headers from openg2p-fastapi-common</li><li>Caters to cash-digital, cash-physical, commodities and services</li><li>Interfaces to Warehouses and Agents for physical goods &#x26; services</li><li>In line with PBMS Gen2 capabilities</li><li>Introduced Adapter pattern for SPAR</li></ol></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>2.0.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.1.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.0.2</td><td></td><td>06 Dec 2024</td><td><a href="../products/g2p-bridge/_archive/releases/1.0.2.md">Release contents</a></td></tr></tbody></table>

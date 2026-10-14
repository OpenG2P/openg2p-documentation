---
description: G2P Bridge Versions
---

# Versions

Every version, with its changes:

* [G2P Bridge changelog](https://openg2p.github.io/versions/g2p-bridge/CHANGELOG.html) — the `openg2p-bridge` Helm chart and its images.
* [G2P Bridge Connectors changelog](https://openg2p.github.io/versions/g2p-bridge-connectors/CHANGELOG.html) — the reference connectors in [`g2p-bridge-connectors`](https://github.com/OpenG2P/g2p-bridge-connectors). The Celery image pulls them by git ref at build time.

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

The `openg2p-bridge` Helm chart and its Docker images (`openg2p-bridge-partner-api`, `-bene-portal-api`, `-celery`, `-example-bank-*`) carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../releases/helm-docker-versioning-and-ci/README.md).

***

## Earlier versions

The G2P Bridge changelog starts at 1.1.0 (18-Jul-2026). Earlier builds are listed below.

{% hint style="warning" %}
**Two similarly-named charts — don't confuse them.** The **current** chart is
**`openg2p-bridge`** (images `openg2p-bridge-*`; Rancher: “OpenG2P Bridge”). The
**legacy** line is **`openg2p-g2p-bridge`** (images `openg2p-g2p-bridge-*` — the extra
`g2p`; Rancher: “OpenG2P G2P Bridge”). They differ by a single `g2p`, are easy to confuse
in the Rancher list, and are **not compatible**. For any new install use
**`openg2p-bridge`**.
{% endhint %}

### `openg2p-bridge` before 1.1.0

The last builds of the current `openg2p-bridge` chart before the changelog starts:

<table><thead><tr><th width="180">Helm Chart &#x26; Version</th><th>G2P Bridge Runtimes</th><th width="123">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-bridge</code></strong><br>(Rancher: “OpenG2P Bridge”)<br><br><a href="https://github.com/OpenG2P/g2p-bridge/tree/develop">0.0.0-develop.41</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-partner-api/tags">openg2p-bridge-partner-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-bene-portal-api/tags">openg2p-bridge-bene-portal-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-celery/tags">openg2p-bridge-celery:develop</a><br><br>openg2p-bridge-example-bank-{api,celery-beat-producers,celery-workers}:develop</td><td>01-Jul-2026</td><td><p><strong>Rolling <code>develop</code> build.</strong> Major changes vs 1.0.0:</p><ol><li><strong>Partner signatures verified via the Partner Manager (PM) service</strong> (openg2p-fastapi-common <code>PartnerMgmtKeyStore</code>) — no MOSIP Keymanager and no local key store; the Bridge fetches partner public keys from PM.</li><li><strong>Partner API signature validation enabled by default in the chart</strong> (secure-by-default; the app-config default is off): inbound verify + signed Bridge→SPAR resolve. Partners (incl. <code>PARTNER_G2P_BRIDGE</code>) are onboarded in Partner Manager — the trial's <code>pm-seed</code> Job does this automatically.</li><li>Local <code>.p12</code> signing key with demo / inline / existing-secret modes.</li><li>Sanity smoke + e2e run as a post-install hook by default (can fail the deploy).</li><li>Deployment hardening: pre-upgrade DB password-sync hook + fail-loud <code>migrate</code>.</li></ol></td></tr><tr><td><strong><code>openg2p-bridge</code></strong><br>(Rancher: “OpenG2P Bridge”)<br><br><a href="https://github.com/OpenG2P/g2p-bridge/tree/v1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-partner-api/tags">openg2p-bridge-partner-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-bene-portal-api/tags">openg2p-bridge-bene-portal-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-celery/tags">openg2p-bridge-celery:1.0.0</a><br>(single image, run as beat <em>and</em> worker)<br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-api/tags">openg2p-bridge-example-bank-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-beat-producers/tags">openg2p-bridge-example-bank-celery-beat-producers:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-bridge-example-bank-celery-workers/tags">openg2p-bridge-example-bank-celery-workers:1.0.0</a></td><td>26-Jun-2026</td><td><p><strong>Intermediate Stable Version</strong></p><ol><li><strong>Single consolidated chart for the complete installation.</strong> <mark style="color:red;">Incompatible with previous Helm chart versions.</mark></li><li>Source consolidated into a <strong>single repository</strong>, <code>g2p-bridge</code> (previously seven repos).</li><li>Added Keycloak client provisioning via the <code>keycloak-init</code> <a href="deployment/keycloak-client.md">Learn more >></a></li><li><strong>Digital cash transfer needs no PBMS or Registry.</strong> <a href="deployment/deployment-of-example-bank.md">Learn more >></a></li><li>Single Celery Docker image, run as beat producer or worker by Helm configuration.</li><li>Added an <a href="deployment/teardown.md">uninstall script</a> that fully tears down the release cleanly</li><li><strong>Partner API authentication is disabled by default in this version</strong> — inbound signature validation is off; when enabled, 1.0.0 validates signatures via <strong>MOSIP Keymanager</strong> (the <code>keycloak-init</code> client authenticates to it). From <code>develop</code> this is replaced by in-process local JWS (no Keymanager).</li></ol></td></tr></tbody></table>

***

### Legacy versions

These versions predate the repository/chart consolidation. They were built from the older multi-repository layout (`openg2p-g2p-bridge-deployment`, `openg2p-g2p-bridge-example-bank-deployment`, etc.) with a separate chart per service. They are **not compatible** with the consolidated chart above. The legacy `openg2p-g2p-bridge` 1.1.0 below is not the `openg2p-bridge` 1.1.0 in the changelog.

Their Docker images use the **`openg2p-g2p-bridge-*`** prefix (the extra `g2p`) — e.g. `openg2p-g2p-bridge-partner-api`, `openg2p-g2p-bridge-celery-workers` — which is what distinguishes them from the current chart's `openg2p-bridge-*` images.

<table><thead><tr><th width="170">Helm Chart &#x26; Version</th><th width="298">G2P Bridge Runtimes</th><th width="153">Version date</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-g2p-bridge</code></strong><br>(Rancher: “OpenG2P G2P Bridge”)<br><br><a href="https://github.com/OpenG2P/openg2p-g2p-bridge-deployment/tree/3.0.0">3.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-beat-producers/2.1.0/images/sha256-75edd2dc6b7ad52a679f8e2942263f0718c95ee1016973d463900d3961a481c2">openg2p-g2p-bridge-celery-beat-producers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-celery-workers/2.1.0/images/sha256-736e8872e04993a0e974d56b586c628b5de5ad6ce01b7069a2cbd801f5c86a69">openg2p-g2p-bridge-celery-workers:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-partner-api/2.1.0/images/sha256-ea58a48364306cb26124d7af31a486564976dca5222c284dadac13e8a0b345ca">openg2p-g2p-bridge-partner-api:v2.1.0</a><br><a href="https://hub.docker.com/layers/openg2p/openg2p-g2p-bridge-bene-portal-api/2.1.0/images/sha256-56b4bc531d25fc0fd71a0adb613b00514a923987801e2b2a0a7a082beb5b606f">openg2p-g2p-bridge-bene-portal-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Complete overhaul of Helm chart. Multiple charts combined into one. <mark style="color:red;">Incompatible with previous Helm chart versions</mark>.</li><li>Embraced new headers from openg2p-fastapi-common</li><li>Caters to cash-digital, cash-physical, commodities and services</li><li>Interfaces to Warehouses and Agents for physical goods &#x26; services</li><li>In line with PBMS Gen2 capabilities</li><li>Introduced Adapter pattern for SPAR</li></ol></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>2.0.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.1.0</td><td></td><td></td><td></td></tr><tr><td><code>openg2p-g2p-bridge</code><br>1.0.2</td><td></td><td>06 Dec 2024</td><td><a href="../products/g2p-bridge/_archive/releases/1.0.2.md">Release contents</a></td></tr></tbody></table>

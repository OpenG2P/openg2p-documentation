---
description: SPAR Versions
---

# Versions

{% hint style="info" %}
**For the current versions, changelogs, and the exact Helm chart & Docker image links, go here:**

## 👉 [SPAR — Versions & Changelog](https://openg2p.gitlab.io/versions/spar-spar/CHANGELOG.html)

That page is **generated on every build and is always up to date**. The
[historical tables](#historical-versions) further down are kept only as a record of the
pre-GitLab builds.
{% endhint %}

## How versioning & publishing work

SPAR is now built and published **entirely on GitLab** (previously GitHub + Docker
Hub), using OpenG2P's shared Helm & Docker packaging pipeline. In brief:

* **One immutable version per commit** — `0.0.0-develop.<n>` on `develop` (by commit
  ordinal) and a frozen `N.N.N` on release (promote-on-release). A version is never
  rebuilt or overwritten.
* **Helm charts** are published to the **shared OpenG2P Helm registry**, so one
  Rancher/Helm repo lists every OpenG2P chart (SPAR included):
  [gitlab.com/groups/openg2p/-/packages](https://gitlab.com/groups/openg2p/-/packages).
* **Docker images** live in **each repo's own Container Registry** — SPAR's are at
  `registry.gitlab.com/openg2p/spar/spar/<name>` (`mapper-partner-api`, `bene-portal-api`).
* **Changelogs** are generated from commit messages onto the changelog page linked above.

This scheme is the same across all OpenG2P repos and is documented once — for the full
details see
**[Helm & Docker Versioning Strategy and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci)**.

***

## Historical versions

The tables below are a **read-only record of builds published before the GitLab move** —
Docker Hub images and the GitHub `openg2p-helm` chart. They are **not** updated for GitLab
builds; for those, always use the [changelog page](https://openg2p.gitlab.io/versions/spar-spar/CHANGELOG.html) above.

{% hint style="warning" %}
**Two similarly-named charts — don't confuse them.** The **current** chart is
**`openg2p-spar`** (Rancher: “OpenG2P SPAR”). The **legacy** line is the chart named
**`spar`**. Both use the same `openg2p-spar-*` Docker images, so the **chart name** is
what distinguishes them, and they are **not compatible**. For any new install use
**`openg2p-spar`**.
{% endhint %}

### Previous versions

The last builds of the **current** `openg2p-spar` chart under the old (Docker Hub +
GitHub) scheme, up to `1.0.0` and the final `0.0.0-develop.<run>` dev build:

<table><thead><tr><th width="180">Helm Chart &#x26; Version</th><th>SPAR Runtimes</th><th width="123">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>openg2p-spar</code></strong><br>(Rancher: “OpenG2P SPAR”)<br><br><a href="https://gitlab.com/openg2p/spar/spar/-/tree/develop">0.0.0-develop.26</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-partner-api/tags">openg2p-spar-mapper-partner-api:develop</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-spar-bene-portal-api/tags">openg2p-spar-bene-portal-api:develop</a></td><td>01-Jul-2026</td><td><p><strong>Rolling <code>develop</code> build.</strong> Major changes vs 1.0.0:</p><ol><li><strong>Partner signatures verified via the Partner Manager (PM) service</strong> (<code>openg2p-fastapi-common</code> <code>PartnerMgmtKeyStore</code>) — no MOSIP Keymanager and no local key store. SPAR only verifies (no signing key).</li><li><strong>Partner signature verification ON by default</strong>, against public keys fetched from the <strong>Partner Manager (PM)</strong> service (no local key store). Partners are onboarded in PM; the trial's G2P Bridge chart onboards <code>PARTNER_G2P_BRIDGE</code> there, so signed Bridge→SPAR resolve verifies out of the box.</li><li>Branch-derived rolling Helm chart versioning (<code>0.0.0-develop.&#x3C;run></code>).</li></ol></td></tr><tr><td><strong><code>openg2p-spar</code></strong><br>(Rancher: “OpenG2P SPAR”)<br><br><a href="https://gitlab.com/openg2p/spar/spar/-/tree/1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-partner-api/tags">openg2p-spar-mapper-partner-api:1.0.0</a><br><br><a href="https://hub.docker.com/r/openg2p/openg2p-spar-bene-portal-api/tags">openg2p-spar-bene-portal-api:1.0.0</a></td><td>27-Jun-2026</td><td><p><strong>Stable version</strong></p><p></p><ol><li>Signature verification via <strong>MOSIP Keymanager</strong>; added Keycloak client provisioning via the <code>keycloak-init</code> subchart (the <code>openg2p-spar</code> OIDC client in the <code>staff</code> realm authenticates the Mapper API to Keymanager). From <code>develop</code> this is replaced by in-process local verification.</li><li>Aligned Keycloak/auth configuration with NSR conventions — shared settings moved under <code>global</code> to avoid duplication.</li><li>Fixed Helm rendering errors (<code>sparMapperAPI</code> values key, ingress host, env-var handling) and bumped Istio VirtualServices to <code>networking.istio.io/v1beta1</code>.</li><li>Added an uninstall script that fully removes the release and its Postgres database/role while keeping Keycloak client secrets intact.</li></ol></td></tr></tbody></table>

***

## Legacy Versions

These versions predate the chart consolidation. They were built from the older `openg2p-spar-deployment` layout with the chart named **`spar`** (a separate chart per service). They are **not compatible** with the consolidated `openg2p-spar` chart above.

<table><thead><tr><th width="170">Helm Chart &#x26; Version</th><th>SPAR Runtimes</th><th width="153">Version date</th><th>Contents</th></tr></thead><tbody><tr><td><strong><code>spar</code></strong><br><br><a href="https://github.com/OpenG2P/openg2p-spar-deployment/tree/2.0.0">2.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-bene-portal-api/2.1.0/images/sha256-dd192b4ba2b36b165407e531b387405356f9017a7f791554139e48c78a6ddadd">spar-bene-portal-api:v2.1.0</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-mapper-partner-api/2.1.0/images/sha256-ac9a12f476b53adb0751f66b0ce032ce1d4f0c3346b3918ae56e4b9b0e55f8aa">spar-mapper-partner-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Incompatible changes w.r.t previous versions. <a href="deployment/helm-charts.md">Learn more >></a></li><li>Moved to Common Headers of openg2p-fastapi-common</li><li>Removed self-service-api and introduced spar-bene-portal-api — in line with OpenG2P Architecture</li><li>Removed spar-mapper-api and introduced spar-partner-api — in line with OpenG2P Architecture</li><li>Rationalized DFSP models (in bene portal, erstwhile self-service) to simplified — BANK, BRANCH and WALLET-PROVIDER models</li></ol></td></tr><tr><td><code>spar</code><br>1.1.0</td><td></td><td>03-Nov-2025</td><td></td></tr><tr><td><code>spar</code><br>1.0.0</td><td></td><td>03-May-2024</td><td><a href="releases/release-notes.md">Release contents</a></td></tr></tbody></table>

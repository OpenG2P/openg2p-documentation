---
description: SPAR Versions
---

# Versions

## SPAR Helm Package

<table><thead><tr><th width="150">Helm Version</th><th>Spar Runtimes</th><th width="153">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-spar/tree/develop/deployment/charts/spar">0.0.0-develop</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-bene-portal-api/2.1.0/images/sha256-dd192b4ba2b36b165407e531b387405356f9017a7f791554139e48c78a6ddadd">spar-bene-portal-api:v2.1.0</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-mapper-partner-api/2.1.0/images/sha256-ac9a12f476b53adb0751f66b0ce032ce1d4f0c3346b3918ae56e4b9b0e55f8aa">spar-mapper-partner-api:v2.1.0</a></td><td>02-Jun-2026</td><td>Keycloak init; chart fixes and uninstall script. <em>(see details below)</em></td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-spar-deployment/tree/2.0.0">2.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-bene-portal-api/2.1.0/images/sha256-dd192b4ba2b36b165407e531b387405356f9017a7f791554139e48c78a6ddadd">spar-bene-portal-api:v2.1.0</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-mapper-partner-api/2.1.0/images/sha256-ac9a12f476b53adb0751f66b0ce032ce1d4f0c3346b3918ae56e4b9b0e55f8aa">spar-mapper-partner-api:v2.1.0</a></td><td>17-Apr-2026</td><td>Breaking: re-architected APIs and DFSP models. <em>(see details below)</em></td></tr><tr><td>1.1.0</td><td></td><td>03-Nov-2025</td><td></td></tr><tr><td>1.0.0</td><td></td><td>03-May-2024</td><td><a href="releases/release-notes.md">Release contents</a></td></tr></tbody></table>

## Version change details

### 0.0.0-develop

1. Added Keycloak client provisioning via the `keycloak-init` subchart — creates the `openg2p-spar` OIDC client in the `staff` realm.
2. Aligned Keycloak/auth configuration with NSR conventions — shared settings moved under `global` to avoid duplication.
3. Fixed Helm rendering errors (`sparMapperAPI` values key, ingress host, env-var handling) and bumped Istio VirtualServices to `networking.istio.io/v1beta1`.
4. Added an uninstall script that fully removes the release and its Postgres database/role while keeping Keycloak client secrets intact.

### 2.0.0

1. Incompatible changes w.r.t previous versions. [Learn more >>](deployment/helm-charts.md)
2. Moved to Common Headers of openg2p-fastapi-common
3. Removed self-service-api and introduced spar-bene-portal-api — in line with OpenG2P Architecture
4. Removed spar-mapper-api and introduced spar-partner-api — in line with OpenG2P Architecture
5. Rationalized DFSP models (in bene portal, erstwhile self-service) to simplified — BANK, BRANCH and WALLET-PROVIDER models

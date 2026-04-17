---
description: SPAR Versions
---

# Versions

## SPAR Helm Package

<table><thead><tr><th width="150">Helm Version</th><th>Spar Runtimes</th><th width="153">Created on</th><th>Contents</th></tr></thead><tbody><tr><td>1.0.0</td><td></td><td>03 May 2024</td><td><a href="releases/release-notes.md">Release contents</a></td></tr><tr><td>1.1.0</td><td></td><td>03 Nov 2025</td><td></td></tr><tr><td>2.0.0-develop</td><td></td><td>In progress</td><td>Major compatible changes w.r.t previous versions. <a href="deployment/pbms-helm-chart-4.x.md">Learn more >></a></td></tr><tr><td>2.0.1</td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-bene-portal-api/2.1.0/images/sha256-dd192b4ba2b36b165407e531b387405356f9017a7f791554139e48c78a6ddadd">spar-bene-portal-api:v2.1.0</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-spar-mapper-partner-api/2.1.0/images/sha256-ac9a12f476b53adb0751f66b0ce032ce1d4f0c3346b3918ae56e4b9b0e55f8aa">spar-mapper-partner-api:v2.1.0</a></td><td>17-Apr-2026</td><td><ol><li>Moved to Common Headers of openg2p-fastapi-common</li><li>Removed self-service-api and introduced spar-bene-portal-api — in line with OpenG2P Architecture</li><li>Removed spar-mapper-api and introduced spar-partner-api — in line with OpenG2P Architecture</li><li>Rationalized DFSP models (in bene portal, erstwhile self-service) to simplified - BANK, BRANCH and WALLET-PROVIDER models</li></ol></td></tr></tbody></table>

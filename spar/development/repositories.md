---
description: The SPAR subsystem source code
---

# Repositories

All SPAR source code lives in a **single consolidated repository**.

| Repository | Description |
| --- | --- |
| [spar](https://github.com/OpenG2P/spar) | <p>The consolidated SPAR repository. Layout:</p><p><mark style="color:blue;">core/</mark> — the Python projects: <code>models</code>, <code>mapper-core</code>, <code>mapper-partner-api</code>, <code>bene-portal-api</code>.<br><mark style="color:blue;">docker/</mark> — Dockerfiles for the API images.<br><mark style="color:blue;">deployment/</mark> — the <code>openg2p-spar</code> Helm chart (<code>charts/openg2p-spar</code>) and the uninstall script (<code>scripts/uninstall-spar.sh</code>).</p> |

{% hint style="info" %}
The previously separate repos — `openg2p-spar-mapper-api`,
`openg2p-spar-self-service`, `openg2p-spar-self-service-ui` and
`openg2p-spar-deployment` — have been consolidated into `openg2p-spar`. The
Self-Service components were removed in v2.0 and replaced by the Beneficiary
Portal API.
{% endhint %}

You can find the **SPAR test plans** (functional and load testing) in this [Google Drive Folder. ](https://drive.google.com/drive/folders/1SzlkpSnl2E1y9hLOpH\_CeZkVvE9F8qt1)

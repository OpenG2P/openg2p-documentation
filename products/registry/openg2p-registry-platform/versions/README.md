---
description: Registry version history and release tracking.
---

# Versions

This page tracks the released versions of OpenG2P Registry (Gen 2).

{% hint style="info" %}
OpenG2P Registry follows semantic versioning. The Helm chart version corresponds to the platform release version. See [Helm Chart 4.x](../design/deployment/helm-chart-4.x.md) for deployment details.
{% endhint %}



<table><thead><tr><th width="101.64434814453125">Helm Version</th><th width="326.7730712890625">Registry Runtimes</th><th width="129.4669189453125">Creation Date</th><th>Remarks</th></tr></thead><tbody><tr><td>4.0.0</td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-staff-portal-api/1.0.1/images/sha256-edf5d39057347a9533b6f9a813501a772d6dc3e0d877edbb71d09114da2618bd">farmer-registry-staff-portal-api:v1.0.1</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-partner-api/1.0.1/images/sha256-7e396fc51fb70a6da084a6821cba36fd8f09f2c2283f9e71d8653d07ac225a6f">farmer-registry-partner-api:v1.0.1</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-celery/1.0.1/images/sha256-81fe703b1a9c0973bcf914e857460c48eabbdee1613cd1c0de2dcdea1ba63796">farmer-registry-celery:v1.0.1</a><br>(the same celery image is used as a beat-producer as well as a worker - based on an input parameter)</td><td>17-Apr-2026</td><td></td></tr></tbody></table>

More version details will be added as releases progress.

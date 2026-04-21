---
description: Registry version history and release tracking.
---

# Versions

This page tracks the released versions of OpenG2P Registry (Gen 2).

{% hint style="info" %}
OpenG2P Registry follows semantic versioning. The Helm chart version corresponds to the platform release version. See [Helm Chart 4.x](../deployment/helm-chart-4.x.md) for deployment details.
{% endhint %}

<table><thead><tr><th width="101.64434814453125">Helm Version</th><th width="326.7730712890625">Registry Runtimes</th><th width="129.4669189453125">Creation Date</th><th>Remarks</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-registry-gen2-deployment/tree/4.0.0">4.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-staff-portal-api/1.0.2/images/sha256-371a53cdea562456e5ca36f8f27b9e51841503551f475c636f5a294a4cd981c5">farmer-registry-staff-portal-api:v1.0.2</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-partner-api/1.0.2/images/sha256-0537420d01acf8feebcf9df96e480a741c23b2fa670898a04d7b1e5f9d4b98bb">farmer-registry-partner-api:v1.0.2</a><br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-farmer-registry-celery/1.0.2/images/sha256-3c142006b21c2787f91e3c5d4bd5b9d7a56065b235b6751c6d0d052dac8cc516">farmer-registry-celery:v1.0.2</a><br>(the same celery image is used as a beat-producer as well as a worker - based on an input parameter)<br><br><a href="https://hub.docker.com/layers/openg2p/openg2p-registry-staff-portal-ui/1.0.2/images/sha256-41fa5232674073944eaa17d46bdf6c5b373165e3101937ecf093c44000860bd1">registry-staff-portal-ui:v1.0.2</a></td><td>20-Apr-2026</td><td><ol><li>First release of Registry Gen 2 - the domain agnostic registry platform</li><li>4.0.0 manifests the <strong>Farmer Registry</strong> (with the farmer domain models defined in the extensions repository)</li></ol></td></tr></tbody></table>

More version details will be added as releases progresses.

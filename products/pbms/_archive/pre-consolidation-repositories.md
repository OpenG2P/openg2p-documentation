---
noIndex: true
---

# Pre-Consolidation Repositories

{% hint style="warning" %}
**Archived.** PBMS was previously developed across the separate repositories listed below. These have been **consolidated into the single [OpenG2P/pbms](https://github.com/OpenG2P/pbms) monorepo** and will be archived on GitHub. This page is retained for historical reference only — see [Repositories](../../../pbms/developer-zone/repositories.md) for the current code organization.
{% endhint %}

<table><thead><tr><th width="300">Repository (pre-consolidation)</th><th width="150">Consolidated into</th><th>Description</th></tr></thead><tbody>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-odoo">openg2p-pbms-odoo</a></td><td><code>pbms/odoo/</code></td><td>The main PBMS application based on Odoo — benefit program definition, benefit codes, geographies, service providers, rules and cycles, and beneficiary-list creation.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-odoo-extensions">openg2p-pbms-odoo-extensions</a></td><td><code>pbms/odoo/extensions/</code></td><td>The extensibility and customisation modules of PBMS — target registry names &amp; models, the eligibility &amp; entitlement summary views, and the UI theme. Bundled as Odoo modules.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-community-addons">openg2p-pbms-community-addons</a></td><td><code>pbms/odoo/community-addons/</code></td><td>The community Odoo addons required by PBMS.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-bg-tasks">openg2p-pbms-bg-tasks</a></td><td><code>pbms/core/</code></td><td>The two background-task runtimes — Celery Beat Producers and Celery Worker Tasks — that together perform all asynchronous processing for PBMS, plus the shared data models.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions">openg2p-pbms-bg-tasks-extensions</a></td><td><code>pbms/extensions/</code></td><td>The extensibility modules for the background tasks — registry models and the APIs behind the eligibility &amp; entitlement summary views.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-apis">openg2p-pbms-apis</a></td><td><code>pbms/apis/</code></td><td>The PBMS portal APIs — Staff Portal, Beneficiary Portal, Agency-App and partner systems.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-docker">openg2p-pbms-docker</a></td><td><code>pbms/docker/</code></td><td>The Docker build scripts that created the PBMS runtime images (Odoo, and the Celery beat/worker runtimes).</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-gen2-deployment">openg2p-pbms-gen2-deployment</a></td><td><code>pbms/deployment/</code></td><td>The Helm charts, templates and values for deploying PBMS-Odoo and the background tasks in a Kubernetes cluster.</td></tr>
</tbody></table>

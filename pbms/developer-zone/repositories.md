# Repositories

## Code organization

PBMS is developed as a single **consolidated repository**. All the components that make up PBMS — the Odoo application, the decoupled background-task engine, the portal APIs, the Docker packaging, and the Helm chart — live together in one monorepo.

**Repository:** [OpenG2P/pbms](https://github.com/OpenG2P/pbms)

<table><thead><tr><th width="220">Folder</th><th>Description</th></tr></thead><tbody>
<tr><td><code>odoo/</code></td><td>The main PBMS application built on Odoo — benefit program definition, benefit codes, geographies, service providers, rules and cycles, and beneficiary-list creation. Includes the core modules, the extension modules (target registry names &amp; models, eligibility &amp; entitlement summary views, and the UI theme under <code>odoo/extensions/</code>), and the bundled community addons under <code>odoo/community-addons/</code>.</td></tr>
<tr><td><code>core/</code></td><td>The decoupled eligibility &amp; entitlement engine — the Celery Beat Producers and Celery Worker tasks that perform all asynchronous processing (beneficiary lists, entitlements, summaries, disbursement envelopes and batches), together with the shared PBMS and background-task data models.</td></tr>
<tr><td><code>extensions/</code></td><td>Registry adapter extensions for the background-task engine — the registry models and the APIs behind the eligibility &amp; entitlement summary views.</td></tr>
<tr><td><code>apis/</code></td><td>The FastAPI portal services — the Beneficiary (self-service) Portal API and the Staff Portal API.</td></tr>
<tr><td><code>docker/</code></td><td>Dockerfiles that build the PBMS runtime images (Odoo, the two Celery runtimes, and the portal APIs) from the local source in this repository.</td></tr>
<tr><td><code>deployment/</code></td><td>The single Helm chart (<code>openg2p-pbms</code>) that installs and runs all of PBMS.</td></tr>
</tbody></table>

## Other repositories used by PBMS

Besides its own repository, PBMS builds on a small number of shared OpenG2P libraries and services. These are **not** part of PBMS and are consumed as external dependencies:

<table><thead><tr><th width="300">Repository</th><th>Used for</th></tr></thead><tbody>
<tr><td><a href="https://github.com/OpenG2P/openg2p-fastapi-common">openg2p-fastapi-common</a></td><td>Shared FastAPI base libraries (configuration, controllers, authentication, and crypto/signing) used by the portal APIs and the background-task engine.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-odoo-commons">openg2p-odoo-commons</a></td><td>Shared Odoo addons baked into the PBMS Odoo (<code>core</code>) image at build time.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/g2p-bridge">g2p-bridge</a></td><td>Provides the G2P Bridge data models used by the Celery workers, and is the downstream component PBMS hands disbursements to.</td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-helm">openg2p-helm</a></td><td>The OpenG2P Helm chart repository from which the published PBMS chart is served.</td></tr>
</tbody></table>

{% hint style="info" %}
PBMS also depends at runtime on shared OpenG2P **commons** services (PostgreSQL, Keycloak, MinIO, Keymanager, mail) and reads from a **Social Registry** (e.g. [national-social-registry](https://github.com/OpenG2P/national-social-registry)). These are deployed separately and are not part of the PBMS build.
{% endhint %}

## Previous (pre-consolidation) repositories

PBMS was previously developed across several separate repositories, which have now been consolidated into the single [OpenG2P/pbms](https://github.com/OpenG2P/pbms) repository. Those repositories will be archived on GitHub. For reference, see [Pre-Consolidation Repositories](../../products/pbms/_archive/pre-consolidation-repositories.md) in the archive.

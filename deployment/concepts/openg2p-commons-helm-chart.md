# OpenG2P Commons Helm Chart

#### Overview

**Purpose:**

* This guide explains the **design rationale** behind the OpenG2P Commons Helm chart.
* It also provides **references for Helm chart development** and links to:
  * The [**source code**](https://github.com/OpenG2P/openg2p-deployment-commons) of the chart.
  * The [**new architecture**](openg2p-deployment-model.md) documentation.

**Design Update (from v2.x.x onward):**

* In OpenG2P **version 2.x.x**, many dependency modules were installed **separately** for each application.
* In the new design, these have been **centralized under the `openg2p-commons` chart**.
* Only the **common dependency modules** shared across all applications are included in this chart.

**List of Commons Dependencies:**\
The `openg2p-commons` Helm chart bundles the following core components:

* **PostgreSQL**  &#x20;
* **Mail SMTP Server**
* **MinIO**
* **ODK Central**
* **Keymanager** (includes keygen job to generate the keys for all modules)
* **OpenSearch**
* **Reporting** (includes _Reporting Framework_ + _Reporting Init_)
* **Superset**
* **eSignet** (includes _eSignet_ + _Mock Identity System_)

#### Bitnami Secure Images Transition

**From August 28th, 2025**, Bitnami is evolving its public catalog under the **Bitnami Secure Images** initiative.

**Key points:**

* Community users now get access to **security-hardened container images** of popular software.
* **Non-hardened Debian-based images** will be deprecated and gradually removed from the free public catalog.
* Only **latest tags** of hardened images will remain available — meant for **development use only**.
* Older versioned images (e.g., `10.6`, `2.50.0`) will move to the **Bitnami Legacy** repo (`docker.io/bitnamilegacy`) and will no longer receive updates.
* For **production workloads**, users are encouraged to adopt **Bitnami Secure Images** — featuring hardened containers, SBOMs, CVE transparency, and enterprise support.

**Our Action:**

* Since Bitnami removed free access to their Helm charts and Docker images,\
  we extracted the **existing charts and versions** we depend on and uploaded them to **our own private Helm repository**.
* All our Helm charts are now updated to reference these **internal chart paths** instead of Bitnami’s public sources.

#### How to Deploy OpenG2P Commons

Refer the instructions [here](../deployment-instructions/environment-installation.md#common-resources).

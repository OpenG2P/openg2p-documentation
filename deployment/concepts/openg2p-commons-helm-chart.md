# OpenG2P Commons Helm Chart 1.x

## Context

* This guide explains the **design rationale** behind the OpenG2P Commons Helm chart.
* It also provides references for Helm chart development and links to:
  * The [**source code**](https://github.com/OpenG2P/openg2p-deployment-commons) of the chart.
  * The [**new architecture**](openg2p-deployment-model.md) documentation.

## **Design update (from v2.x.x onward)**

* In OpenG2P **version 2.x.x**, many dependency modules were installed separately for each application.
* In the new design, these have been centralized under the `openg2p-commons` chart.
* Only the common dependency modules shared across all applications are included in this chart.

## **Dependencies**

The `openg2p-commons` Helm chart bundles the following core components.

1. **PostgreSQL**
2. **Mail SMTP Server**
3. **MinIO**
4. **ODK Central**
5. **Keymanager** (includes keygen job to generate the keys for all modules)
6. **OpenSearch**
7. **Reporting** (includes _Reporting Framework_ + _Reporting Init_)
8. **Superset**
9. **eSignet** (includes _eSignet_ + _Mock Identity System_)

{% hint style="info" %}
### Bitnami secure images transition

**From August 28th, 2025**, Bitnami is evolving its public catalog under the **Bitnami Secure Images** initiative.

**Key points:**

* Community users now get access to **security-hardened container images** of popular software.
* **Non-hardened Debian-based images** will be deprecated and gradually removed from the free public catalog.
* Only latest tags of hardened images will remain available — meant for **development use only**.
* Older versioned images (e.g., `10.6`, `2.50.0`) will move to the **Bitnami Legacy** repo (`docker.io/bitnamilegacy`) and will no longer receive updates.
* For production workloads, users are encouraged to adopt **Bitnami Secure Images** — featuring hardened containers, SBOMs, CVE transparency, and enterprise support.

**Our action:**

* Since Bitnami removed free access to their Helm charts and Docker images,\
  we extracted the existing charts and versions we depend on and uploaded them to our own private Helm repository.
* All our Helm charts are now updated to reference these internal chart paths instead of Bitnami’s public sources.
{% endhint %}

## Versions

| HelmVesion    | Last Modified | Comments                                                                                                                                                                                                                                   |
| ------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1.0.0         | 21-Jan-2026   | Frozen stable version.                                                                                                                                                                                                                     |
| 1.1.0-develop | 13-Feb-2026   | Several major changes. See [https://openg2p.atlassian.net/browse/G2P-4036](https://openg2p.atlassian.net/browse/G2P-4036). Works well with internal DB. With external DB, there are some issues.                                           |
| 1.2.0-develop | 24-Mar-2026   | Works well when run via command line using `install.sh` script but not from Rancher. <mark style="color:$danger;">DO NOT USE</mark> install from Rancher.                                                                                  |
| 2.0.0-develop | 30-Mar-2026   | Completely rearchitected. NOT COMPATIBLE WITH PREVIOUS VERSIONS. Chart split into two charts as Rancher would not honor the install hooks. The 'base' chart installs Postgres etc, while other services are installed by 'services' chart. |

## How to deploy openg2p commons

Refer the instructions [here](../deployment-instructions/environment-installation.md#common-resources).

## Tear down

To completely clean up the OpenG2P-Commons installation, follow these steps:

1. Uninstall OpenG2P-Commons from Rancher
   * Go to **Apps → Installed Apps**
   * Select **OpenG2P-Commons**
   * Click **Delete**
2. Manually remove all remaining workloads associated with OpenG2P-Commons, such as Pods, Deployments, StatefulSets, Jobs, and related resources.
3. Delete secrets created by this chart only
   * Remove **application/user secrets** created by OpenG2P-Commons
   * **Do not delete any Keycloak client or Keycloak-related secrets**
4. Delete Persistent Volume Claims (PVCs)
   * Identify PVCs created by OpenG2P-Commons
   * Delete those PVCs
5. Delete corresponding Persistent Volumes (PVs)
   * Identify PVs associated with the deleted PVCs
   * Delete PVs that are in **Released** state

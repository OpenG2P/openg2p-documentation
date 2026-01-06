# Environment Installation

The instructions here pertain to the deployment of common components for an environment on the Kubernetes cluster.  All the components are installed in the same namespace.

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ [Infrastruction setup](infrastructure-setup.md) is completed&#x20;
* ✅ [Environment](environment-installation.md) has been setup with common resources installed.
* ✅ Domain name `esignet.<your environment>.<your domain name>` (e.g. `esignet.qa.openg2p.org`) is available along with SSL certificate for the domain (_the wild certificate should have already been loaded during Infrastructure setup_)
* ✅ **Project Owner access** on the OpenG2P namespace

## Installation using Rancher UI

## Post Installation

### Keycloak

#### Assigning roles to users

Create[ Keycloak client roles](https://www.keycloak.org/docs/latest/server_admin/#con-client-roles_server_administration_guide) for the following components and assign them to users:

<table><thead><tr><th width="336">Component</th><th>Role name</th></tr></thead><tbody><tr><td>OpenSearch Dashboards for logging</td><td><code>admin</code></td></tr><tr><td>OpenSearch Dashboards for <a href="../../monitoring-and-reporting/reporting-framework/">Reporting</a> </td><td><code>admin</code></td></tr><tr><td>Kafka UI for <a href="../../monitoring-and-reporting/reporting-framework/">Reporting</a></td><td><code>Admin</code></td></tr><tr><td>Apache Superset</td><td><code>Admin</code></td></tr><tr><td>Minio Console</td><td><code>consoleAdmin</code></td></tr></tbody></table>

#### Assigning roles to clients

* For Social Registry to be able to access Keymanager APIs, create a realm role in Keycloak with the name "KEYMANAGER\_ADMIN" and assign this as a service account role to the Social Registry Keycloak client.

## Modules

Install the modules and other utility apps individually using their respective instructions:

1. [Registry](../../social-registry/deployment/registry-installation.md)
2. [PBMS](https://docs.openg2p.org/pbms/deployment)&#x20;
3. [SPAR](https://docs.openg2p.org/spar/deployment)&#x20;
4. [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui)&#x20;
5. Beneficiary Portal


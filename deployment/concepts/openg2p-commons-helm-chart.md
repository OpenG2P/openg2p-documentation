# Commons Helm Charts 2.x

## Context

* This guide explains the **design rationale** behind the OpenG2P Commons Helm charts.
* It also provides references for Helm chart development and links to:
  * The [**source code**](https://github.com/OpenG2P/openg2p-deployment-commons) of the charts.
  * The [**new architecture**](openg2p-deployment-model.md) documentation.

## Architecture (v2.x onward)

From version 2.0, the commons deployment is split into **two Helm charts**:

1. **`openg2p-commons-base`** - Infrastructure layer (installed first)
2. **`openg2p-commons-services`** - Application services layer (depends on base)

This split was necessary because Rancher's Helm integration does not execute Helm hooks, which caused ordering issues with a single chart.

### openg2p-commons-base

Installs all infrastructure components:

| Component               | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| **Keycloak**            | Per-environment identity provider (OIDC/OAuth2)                     |
| **Keycloak Init**       | Creates realms, clients, and themes in Keycloak                     |
| **PostgreSQL**          | Shared database server                                              |
| **Postgres Init**       | Creates databases and users for all services                        |
| **Redis**               | Cache (without auth)                                                |
| **Redis Auth**          | Cache with authentication (for eSignet)                             |
| **Kafka**               | Message broker                                                      |
| **Kafka UI**            | Kafka management dashboard                                          |
| **OpenSearch**          | Search and analytics engine with dashboards                         |
| **MinIO**               | Object storage                                                      |
| **SoftHSM**             | Software HSM for key management                                     |
| **Mail**                | SMTP relay server (optional)                                        |
| **Client Secrets Sync** | Fetches OIDC client secrets from Keycloak and stores in K8s secrets |

### openg2p-commons-services

Installs application services:

| Component                | Description                        |
| ------------------------ | ---------------------------------- |
| **Superset**             | Data visualization and dashboards  |
| **eSignet**              | Digital signature service          |
| **Mock Identity System** | Mock identity provider for testing |
| **Keymanager**           | Cryptographic key management       |
| **ODK Central**          | Data collection                    |
| **OpenG2P Master Data**  | Master data service                |
| **Reporting**            | Reporting framework                |
| **Artifactory**          | Artifact repository                |
| **OpenG2P IAM Service**  | Identity and access management API |

## Key Design Decisions

### Per-environment Keycloak

Each environment gets its own Keycloak instance (installed as part of `openg2p-commons-base`). This eliminates the need for a shared Keycloak server and simplifies credential management - the Keycloak admin user is used directly for client initialization.

* Keycloak URL: `https://keycloak.<baseDomain>`
* Admin credentials are auto-generated and stored in a K8s secret
* OIDC clients are created automatically by `keycloak-init`
* Client secrets are synced to K8s secrets by `client-secrets-sync`

### Keycloak Realms and Clients

The `keycloak-init` job creates:

* **`master` realm** - with `openg2p-admin` login and admin themes
* **`staff` realm** - with `staff-portal` login and admin themes, containing OIDC clients:
  * `openg2p-superset`, `openg2p-opensearch`, `openg2p-kafka`, `openg2p-minio`, `openg2p-odk`, `staff-portal`

### Keycloak Themes

Themes are specified per realm in the `keycloak-init` configuration:

```yaml
keycloak-init:
  realms:
    master:
      themes:
        loginTheme: openg2p-admin
        adminTheme: openg2p-admin
      clients: []
    staff:
      themes:
        loginTheme: staff-portal
        adminTheme: staff-portal
      clients:
        - clientId: staff-portal
          name: Staff Portal
          redirectUris: ["*"]
```

### No Helm Hooks

Neither chart uses Helm hooks. All init jobs (postgres-init, keycloak-init, client-secrets-sync) run as regular Kubernetes resources. This ensures compatibility with Rancher, which skips hooks.

### Shared PostgreSQL

Keycloak uses the same PostgreSQL instance as other services. The `postgres-init` job creates a dedicated `keycloak` database and user.

## Versions

| Version       | Last Modified | Comments                                                                                                  |
| ------------- | ------------- | --------------------------------------------------------------------------------------------------------- |
| 2.0.0-develop | 30-Mar-2026   | Split into two charts (base + services). Per-environment Keycloak. NOT COMPATIBLE WITH PREVIOUS VERSIONS. |

## How to deploy

Refer to the instructions [here](../deployment-instructions/environment-installation.md).

## Tear down

Use the provided uninstall scripts:

```bash
# Uninstall services first
./uninstall.sh <namespace> <services-release-name>

# Then uninstall base
./uninstall-base.sh <namespace> <base-release-name>
```

The uninstall scripts handle cleanup of secrets (including those with `helm.sh/resource-policy: keep`), PVCs, and released PVs.

## Previous versions

Previous version of Helm chart (1.x) was a single Helm chart that deployed all modules.  These are available in  [https://github.com/OpenG2P/openg2p-commons-deployment](https://github.com/OpenG2P/openg2p-commons-deployment) the repective branches.

| Version       | Last Modified | Comments                                            |
| ------------- | ------------- | --------------------------------------------------- |
| 1.0.0         | 21-Jan-2026   | Frozen stable version (single chart).               |
| 1.1.0-develop | 13-Feb-2026   | Several major changes. Works well with internal DB. |
| 1.2.0-develop | 24-Mar-2026   | Works via CLI but not Rancher.                      |


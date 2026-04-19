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

* **External URL:** `https://keycloak.<baseDomain>` (browser-facing, used for OAuth redirects)
* **Internal URL:** `http://<release>-keycloak:80` (pod-to-pod, used by backend services for token validation, OIDC discovery)
* Admin credentials are auto-generated and stored in K8s secret `<release>-keycloak`
* Keycloak image tag is configurable (default: `24.0.5-debian-12-r1-g2p1`)
* OIDC clients are created automatically by `keycloak-init`
* Client secrets are synced to K8s secrets by `client-secrets-sync`
* Keycloak shares the commons PostgreSQL instance (dedicated `keycloak` database)

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

All services (including Keycloak) share the same PostgreSQL instance. The `postgres-init` job creates dedicated databases and users for each service. For production deployments, an external PostgreSQL server can be used by disabling the embedded PostgreSQL and setting `global.postgresqlHost`.

### Internal vs External URLs

The charts maintain two Keycloak URL paths:

* `global.keycloakInternalUrl` — used by backend pods (OIDC discovery, token validation, JWK fetching). Points to the in-cluster Keycloak service via HTTP.
* `global.keycloakBaseUrl` / `global.keycloakExternalIssuerUrl` — used for browser-facing OAuth redirects. Points to the external HTTPS URL.

This separation ensures backend services work without external DNS, while browsers are correctly redirected to the public Keycloak URL.

### Logging and Log Retention

Pod logs from selected services are shipped to OpenSearch using the Fluent Operator. The **commons-services** chart creates a Flow resource that captures logs from configured containers (master-data, IAM, ODK, eSignet, keymanager, etc.) and routes them to the OpenSearch Output created by commons-base.

Log retention is managed automatically via an OpenSearch **ISM (Index State Management) policy**. By default, logstash indexes older than 7 days are deleted. This is configurable:

```bash
# Set retention to 30 days
--set opensearch.ismPolicy.retentionDays=30

# Disable automatic log retention
--set opensearch.ismPolicy.enabled=false
```

The ISM policy is applied by a Job that runs as part of the base chart installation. It auto-attaches to all new `logstash-*` indexes and also applies to any pre-existing indexes on upgrade.

A **default logs dashboard** is automatically imported into OpenSearch Dashboards on install. It includes a Discover view with columns for timestamp, log level, kubernetes pod, and message. To disable automatic dashboard import:

```bash
--set opensearch.defaultDashboards.enabled=false
```

### Helm `global` value propagation

Helm automatically propagates the parent chart's `global.*` values to all subcharts. When the same `global` key is defined in both the parent and a subchart override, the **parent's value takes precedence**. Subchart-specific `global` overrides only work for keys that do not exist in the parent's `global`.

This means infrastructure names (like `postgresqlHost`, `redisInstallationName`) set in the parent's `global` are automatically available to all subcharts. IAM-specific globals (like `iamDB`, `iamDBUser`) work because they are unique to the IAM subchart.

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


# Commons Helm Charts 2.x

## Context

* This guide explains the **design rationale** behind the OpenG2P Commons Helm charts.
* It also provides references for Helm chart development and links to:
  * The [**source code**](https://github.com/OpenG2P/openg2p-commons-deployment) of the charts.
  * The [**new architecture**](openg2p-deployment-model.md) documentation.

## Versions

| Chart                                          | Version                                                                         | Date        | Comments                                                                                                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| openg2p-commons-base, openg2p-commons-services | [2.0.1](https://github.com/OpenG2P/openg2p-commons-deployment/tree/v2.0.1)      | 08-May-2026 | Substantial additions - dashboards, external postgres configurations.                                                                                    |
| openg2p-commons-base, openg2p-commons-services | [2.0.0](https://github.com/OpenG2P/openg2p-commons-deployment/tree/v2.0.0)      | 21-Apr-2026 | Stable version. Two charts (base + services). Per-environment Keycloak. NOT COMPATIBLE WITH 1.x VERSIONS.                                                |
| openg2p-commons-base, openg2p-commons-services | [2.0.0-develop](https://github.com/OpenG2P/openg2p-commons-deployment/tree/2.0) | In progress | Default logs saved search added in OpenSearch (with ERROR filter toggle and pod-name substring search). Audit Manager service added to commons-services. Each chart now owns its own Keycloak clients (no cross-chart hostname duplication). Simplified DB names (e.g. `iam`, `audit_manager`, `master_data` — no release-name prefix). MinIO split into two VirtualServices (`minio.<domain>` for Console, `minio-api.<domain>` for S3 API). |

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

| Component                 | Description                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Superset**              | Data visualization and dashboards                                                  |
| **eSignet**               | Digital signature service                                                          |
| **Mock Identity System**  | Mock identity provider for testing                                                 |
| **Keymanager**            | Cryptographic key management                                                       |
| **ODK Central**           | Data collection                                                                    |
| **OpenG2P Master Data**   | Master data service                                                                |
| **Reporting**             | Reporting framework                                                                |
| **Artifactory**           | Artifact repository                                                                |
| **OpenG2P IAM Service**   | Identity and access management API                                                 |
| **OpenG2P Audit Manager** | Centralized audit event collector (Kafka-backed, stores audit trail in PostgreSQL) |

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

All services (including Keycloak) share the same PostgreSQL instance. The `postgres-init` job creates dedicated databases and users for each service. For production deployments, an external PostgreSQL server can be used — see the [External PostgreSQL](openg2p-commons-helm-chart.md#external-postgresql) section below for the full setup steps.

### MinIO Console vs S3 API

MinIO exposes two ports on a single Kubernetes Service: **9001 (Console UI)** and **9000 (S3 API)**. To route browser traffic to the console and S3-client traffic to the API without manual port juggling, the chart creates **two Istio VirtualServices**:

* `minio.<baseDomain>` → port 9001 (Console UI)
* `minio-api.<baseDomain>` → port 9000 (S3 API)

Pod-to-pod S3 calls (e.g., from ODK Central) use the internal cluster service `http://commons-minio:9000` — they don't go through Istio. Both hostnames work out of the box on a fresh install; no manual VirtualService edits required.

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

A **default logs saved search** is automatically imported into OpenSearch Dashboards on install and set as the landing page (via `defaultRoute`). It opens a Discover view with columns for timestamp, log level, kubernetes pod, and message, with 10-second auto-refresh enabled and a default time range of the last 1 hour. A pre-saved `level: ERROR` filter pill is shown at the top — it is **disabled by default** and can be **temporarily enabled or disabled with a single click** to toggle an ERROR-only view without touching the query bar. Typing a substring in the query bar (e.g., `odk`) filters to pods whose name contains that substring, thanks to an ngram-indexed subfield on `kubernetes.pod_name` applied via an OpenSearch index template. To disable automatic saved-search import:

```bash
--set opensearch.savedSearch.enabled=false
```

### Resource Limits (Sandbox vs Production)

All components are configured with **sandbox-friendly resource limits** by default — designed for development and testing environments where Keycloak, OpenSearch, and Kafka see minimal load. This prevents components like Keycloak from consuming 3GB+ of RAM on idle clusters.

**Default sandbox limits:**

| Component                   | Memory Limit | JVM Heap | Notes                                                           |
| --------------------------- | ------------ | -------- | --------------------------------------------------------------- |
| Keycloak                    | 1Gi          | 512m     | Increase to 2Gi / 1g for production                             |
| PostgreSQL                  | 1Gi          | N/A      | Increase to 2-4Gi for production                                |
| OpenSearch                  | 1Gi          | 512m     | Heap should be \~50% of limit; increase to 4-8Gi for production |
| Kafka (controller + broker) | 1Gi each     | 512m     | Increase to 2Gi / 1g for production                             |
| MinIO                       | 512Mi        | N/A      | Increase to 1-2Gi for heavy S3 usage                            |
| Redis (x2)                  | 128Mi each   | N/A      | Sufficient for most workloads                                   |
| OpenSearch Dashboards       | 512Mi        | N/A      | Sufficient for most workloads                                   |
| Kafka UI                    | 512Mi        | 256m     | Sufficient for most workloads                                   |
| SoftHSM                     | 128Mi        | N/A      | Sufficient                                                      |
| Artifactory                 | 512Mi        | N/A      | Sufficient                                                      |

To scale up for production, override the relevant values:

```bash
# Example: scale Keycloak and OpenSearch for production
--set keycloak.resources.limits.memory=2Gi \
--set keycloak.extraEnvVars[2].value="-Xms512m -Xmx1g" \
--set opensearch.master.heapSize=2g \
--set opensearch.master.resources.limits.memory=4Gi
```

**How to detect resource constraints:**

* **OOMKilled** restarts — check `kubectl get pods` for high restart counts
* **CPU throttling** — check `kubectl top pods` for CPU at limit
* **Application-specific** — OpenSearch `_cluster/health` turning `yellow`/`red`, Kafka consumer lag increasing, Keycloak login latency

Enable Rancher Monitoring (Prometheus + Grafana) to get dashboards and alerts for memory/CPU pressure across all pods.

### Helm `global` value propagation

Helm automatically propagates the parent chart's `global.*` values to all subcharts. When the same `global` key is defined in both the parent and a subchart override, the **parent's value takes precedence**. Subchart-specific `global` overrides only work for keys that do not exist in the parent's `global`.

This means infrastructure names (like `postgresqlHost`, `redisInstallationName`) set in the parent's `global` are automatically available to all subcharts. IAM-specific globals (like `iamDB`, `iamDBUser`) work because they are unique to the IAM subchart.

## External PostgreSQL

By default, **commons-base** installs an embedded PostgreSQL (Bitnami chart) inside the cluster. For production deployments, you typically want to use an external PostgreSQL server — a managed service (AWS RDS, Cloud SQL) or a dedicated VM. The charts support this with a few configuration overrides.

### What gets created in PostgreSQL

The `postgres-init` job (running as a regular Kubernetes Job) connects to PostgreSQL using the **superuser** credentials and creates:

* Databases (one per service): `superset`, `odkdb`, `mosip_keymgr`, `mosip_mockidentitysystem`, `mosip_esignet`, `keycloak`, plus `<release>_iam` and `<release>_auditmanager` from the services chart
* One database user per database, with a randomly generated password
* Per-user secrets in Kubernetes (`superset-db-user`, `odk-db-user`, `keymgr-db-user`, `keycloak-db-user`, `commons-services-iam`, `commons-services-auditmanager`, etc.) — services read these for their own connections

So your **external PostgreSQL user must have `CREATE DATABASE` and `CREATE ROLE` privileges**. A managed-service master user (e.g. RDS master) typically works.

### Configuration overrides

Three globals control PostgreSQL connectivity. They are wired identically in both `openg2p-commons-base` and `openg2p-commons-services`:

| Global                       | Purpose                                           | Default (embedded)     | Set for external                             |
| ---------------------------- | ------------------------------------------------- | ---------------------- | -------------------------------------------- |
| `global.postgresqlHost`      | Hostname or IP of the PostgreSQL server           | `<release>-postgresql` | External hostname or IP                      |
| `global.postgresqlSecret`    | Name of K8s secret holding the superuser password | `<release>-postgresql` | Your pre-created secret name                 |
| `global.postgresqlSecretKey` | Key inside the secret                             | `postgres-password`    | Override if your secret uses a different key |

### Why pre-creation of the secret is required

Multiple subcharts reference the superuser secret at template render time (postgres-init, Keycloak's externalDatabase, keymanager's postgresInit, eSignet, mock-identity-system, IAM service, audit-manager). Helm cannot create a secret on the fly that other resources within the same release reference — chicken-and-egg. So the secret must exist **before** `helm install` runs.

### Steps to install with external PostgreSQL

**1. Pre-create the K8s secret** with the PostgreSQL superuser password:

```bash
kubectl create namespace <namespace> 2>/dev/null || true

kubectl create secret generic commons-postgresql \
  -n <namespace> \
  --from-literal=postgres-password='<superuser-password>'
```

**2. Install commons-base** with external PG overrides:

```bash
./install-base.sh <namespace> commons <base-domain> \
  --set postgresql.enabled=false \
  --set global.postgresqlHost=<external-pg-host-or-ip> \
  --set global.postgresqlSecret=commons-postgresql
```

The `install-base.sh` script verifies the secret exists in the namespace before proceeding (fails fast with the exact `kubectl create` command if missing).

**3. Install commons-services** with the same overrides:

```bash
./install.sh <namespace> commons-services commons <base-domain> \
  --set global.postgresqlHost=<external-pg-host-or-ip> \
  --set global.postgresqlSecret=commons-postgresql
```

### From the Rancher UI

The same three globals are exposed in `questions.yaml` for both charts under the **Postgres** / **Infrastructure** group. Set them through the UI and the chart behaves identically. Remember to pre-create the secret in the target namespace using `kubectl` first — Rancher's installer doesn't have a pre-flight check for it, so a missing secret will surface as `CreateContainerConfigError` on the postgres-init pods.

### Notes

* If your external secret uses a different key than `postgres-password`, also set `global.postgresqlSecretKey=<your-key>`.
* The connection assumes standard PostgreSQL port `5432`. Override `postgres-init.postgresql.port` if your service exposes a different port.
* TLS is not configured by default. If your provider requires SSL, you'd need to extend the postgres-init job (out of scope for the standard chart).
* For embedded PostgreSQL (default), no manual secret creation is needed — the Bitnami PostgreSQL chart auto-creates `<release>-postgresql` with key `postgres-password`, which the charts reference by default.

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

Previous version of Helm chart (1.x) was a single Helm chart that deployed all modules. These are available in [https://github.com/OpenG2P/openg2p-commons-deployment](https://github.com/OpenG2P/openg2p-commons-deployment) the repective branches.

| Version       | Last Modified | Comments                                            |
| ------------- | ------------- | --------------------------------------------------- |
| 1.0.0         | 21-Jan-2026   | Frozen stable version (single chart).               |
| 1.1.0-develop | 13-Feb-2026   | Several major changes. Works well with internal DB. |
| 1.2.0-develop | 24-Mar-2026   | Works via CLI but not Rancher.                      |

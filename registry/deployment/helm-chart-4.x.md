# Helm Chart 4.x

## Overview

The **OpenG2P Registry Helm Chart** (`openg2p-registry`) is a comprehensive Kubernetes deployment package that installs the Registry module along with all its required services. Chart version 4.x is designed for the Gen2 architecture of the Registry.

{% hint style="info" %}
This guide assumes that the Kubernetes infrastructure and the **commons** environment have already been set up as described in the [Deployment Instructions](https://docs.openg2p.org/deployment/deployment-instructions) and [Automation](https://docs.openg2p.org/deployment/automation) guides. The commons release provides shared services such as **PostgreSQL**, **Keycloak**, **MinIO**, **IAM**, and **Keymanager** that the Registry chart depends on.
{% endhint %}

## Components

The chart deploys the following application components and subcharts:

| Component                  | Type        | Default  | Description                                                                      |
| -------------------------- | ----------- | -------- | -------------------------------------------------------------------------------- |
| **Staff Portal API**       | Application | Enabled  | Backend API for the staff-facing registry portal                                 |
| **Staff Portal UI**        | Application | Enabled  | Next.js frontend for registry staff operations                                   |
| **Partner API**            | Application | Enabled  | API for partner/external system integrations                                     |
| **Beneficiary Portal API** | Application | Disabled | API for beneficiary self-service portal                                          |
| **Celery Beat Producer**   | Application | Enabled  | Periodic task scheduler for async processing                                     |
| **Celery Worker**          | Application | Enabled  | Worker for background tasks (ingestion, deduplication, etc.)                     |
| **Redis**                  | Subchart    | Enabled  | Message broker and result backend for Celery                                     |
| **postgres-init**          | Subchart    | Enabled  | Initialises the registry database, user, and extensions in the shared PostgreSQL |
| **ID Generator**           | Subchart    | Enabled  | Generates unique IDs for registrants and households                              |
| **Keycloak Init**          | Subchart    | Enabled  | Creates the OIDC client and RBAC roles in Keycloak                               |

### Architecture diagram

```
                        +---------------------------+
                        |    Keycloak (commons)      |
                        +---------------------------+
                                    ^
                                    | OIDC / RBAC
          +-------------------------+-------------------------+
          |                         |                         |
+---------+----------+  +-----------+---------+  +------------+--------+
| Staff Portal UI    |  | Staff Portal API    |  | Partner API         |
| (Next.js)          |->| (FastAPI)           |  | (FastAPI)           |
+--------------------+  +----------+----------+  +----------+----------+
                                   |                         |
                        +----------+-----------+             |
                        |     PostgreSQL       |<------------+
                        |     (commons)        |
                        +----------+-----------+
                                   ^
                                   |
          +------------------------+------------------------+
          |                        |                        |
+---------+--------+  +------------+--------+  +------------+--------+
| Celery Beat      |  | Celery Worker       |  | ID Generator        |
| Producer         |  |                     |  | (subchart)          |
+--------+---------+  +---------------------+  +---------------------+
         |                        |
         v                        v
   +------------+          +------------+
   |   Redis    |          |   MinIO    |
   | (subchart) |          | (commons)  |
   +------------+          +------------+
```

## Prerequisites

Before installing the Registry chart, ensure the following are available in the target namespace:

| Prerequisite    | Provided by       | Details                                                                                                        |
| --------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- |
| PostgreSQL      | `commons` release | Shared database server. The postgres superuser secret must exist as `commons-postgresql`.                      |
| Keycloak        | `commons` release | Namespace-local Keycloak at `keycloak.<namespace>.openg2p.org`. Admin secret must exist as `commons-keycloak`. |
| MinIO           | `commons` release | Object storage for document templates. Secret: `commons-minio`.                                                |
| IAM Service     | `commons` release | Authentication provider at `http://commons-services-iam-staff-portal-api`.                                     |
| Keymanager      | `commons` release | Key management service at `commons-services-keymanager`.                                                       |
| Master Data API | `commons` release | Reference/master data service at `http://commons-services-master-data-api`.                                    |
| Istio           | Infrastructure    | Service mesh with ingress gateway for routing.                                                                 |
| Wildcard DNS    | Infrastructure    | `*.<namespace>.openg2p.org` resolving to the cluster ingress.                                                  |

{% hint style="warning" %}
The commons release name is assumed to be **`commons`** throughout the chart defaults. If your commons release has a different name, you must override the relevant service URLs (`keycloak-init.keycloak.url`, `keycloak-init.keycloak.existingSecret`, `global.iamServiceUrl`, `global.keymanagerInstallationName`, etc.).
{% endhint %}

## Installation

### Using Rancher (recommended)

1. Navigate to **Apps > Charts** in the Rancher UI for your cluster.
2. Select the **OpenG2P Registry** chart from the `openg2p` catalogue.
3. Choose the target **namespace** (e.g. `trial`, `qa`, `production`).
4. Set the **release name** (e.g. `farmer-registry`). This name is used to derive hostnames, database names, and Kubernetes resource names.
5. Fill in the configuration form (see [Configuration](helm-chart-4.x.md#configuration) below). For advanced options, switch to **Edit YAML**.
6. Under Helm Options, **disable the `wait` flag** to avoid timeouts on first install.
7. Click **Install** and wait for all pods to reach `Running` state.

### Using Helm CLI

```bash
# Add the OpenG2P Helm repository
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

# Install the chart
helm -n <namespace> install <release-name> openg2p/openg2p-registry \
  --set global.registryHostname=<release-name>.<namespace>.openg2p.org
```

**Example:**

```bash
helm -n trial install farmer-registry openg2p/openg2p-registry \
  --set global.registryHostname=farmer-registry.trial.openg2p.org
```

To upgrade an existing release:

```bash
helm -n trial upgrade farmer-registry openg2p/openg2p-registry -f custom-values.yaml
```

To perform a dry-run and inspect the rendered manifests:

```bash
helm -n trial template farmer-registry openg2p/openg2p-registry \
  --debug > output.yaml
```

## Configuration

### Hostname and domain conventions

The chart uses Go template expressions in `values.yaml` to derive hostnames automatically from the Helm release name and namespace:

| Service          | Default hostname pattern                        | Example (`farmer-registry` in `trial`)          |
| ---------------- | ----------------------------------------------- | ----------------------------------------------- |
| Staff Portal UI  | `<release>.<namespace>.openg2p.org`             | `farmer-registry.trial.openg2p.org`             |
| Staff Portal API | `staff-<release>.<namespace>.openg2p.org`       | `staff-farmer-registry.trial.openg2p.org`       |
| Partner API      | `partner-<release>.<namespace>.openg2p.org`     | `partner-farmer-registry.trial.openg2p.org`     |
| ID Generator     | `idgenerator-<release>.<namespace>.openg2p.org` | `idgenerator-farmer-registry.trial.openg2p.org` |
| Keycloak         | `keycloak.<namespace>.openg2p.org`              | `keycloak.trial.openg2p.org`                    |

The base hostname is controlled by `global.registryHostname`.

### Global parameters

These parameters are shared across all components:

| Parameter                           | Default                                                    | Description                                        |
| ----------------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| `global.registryVariant`            | `farmer`                                                   | Registry variant name. Affects Docker image names. |
| `global.registryHostname`           | `{{ .Release.Name }}.{{ .Release.Namespace }}.openg2p.org` | Base hostname for all services.                    |
| `global.postgresqlHost`             | `commons-postgresql`                                       | PostgreSQL server hostname.                        |
| `global.keycloakBaseUrl`            | `https://keycloak.{{ .Release.Namespace }}.openg2p.org`    | Keycloak base URL.                                 |
| `global.keycloakRealm`              | `staff-{{ .Release.Namespace }}`                           | Keycloak realm name for staff authentication.      |
| `global.authClientId`               | `registry-staff-portal`                                    | OIDC client ID in Keycloak.                        |
| `global.authClientSecret`           | `registry-staff-portal`                                    | K8s Secret name holding the OIDC client password.  |
| `global.iamServiceUrl`              | `http://commons-services-iam-staff-portal-api`             | Internal URL of the IAM service.                   |
| `global.masterDataApiUrl`           | `http://commons-services-master-data-api`                  | Internal URL of the Master Data API.               |
| `global.keymanagerInstallationName` | `commons-services-keymanager`                              | Internal service name for keymanager.              |

### Rancher UI questions

The chart provides a simplified Rancher UI form (`questions.yaml`) with the most commonly configured parameters:

| Field                         | Parameter                 | Group        |
| ----------------------------- | ------------------------- | ------------ |
| Registry Hostname             | `global.registryHostname` | General      |
| PostgreSQL Server Host        | `global.postgresqlHost`   | General      |
| Keycloak Base URL             | `global.keycloakBaseUrl`  | General      |
| Keycloak Init toggle          | `keycloak-init.enabled`   | General      |
| Staff Portal API toggle       | `staffPortalApi.enabled`  | General      |
| Staff Portal UI toggle        | `staffPortalUi.enabled`   | General      |
| Partner API toggle            | `partnerApi.enabled`      | General      |
| Beneficiary Portal API toggle | `benePortalApi.enabled`   | General      |
| ID Generator toggle           | `idgenerator.enabled`     | General      |
| ID Types Configuration        | _(see note)_              | ID Generator |

{% hint style="info" %}
ID type configuration (types, lengths, pool settings) cannot be expressed as simple form fields. The Rancher UI shows a note directing users to switch to **Edit YAML** to modify the `idgenerator.idGenerator.appConfig.idTypes` section.
{% endhint %}

### Database configuration

The chart automatically derives database names and user names from the release name to avoid collisions:

| Component    | Database name                                        | User name                         |
| ------------ | ---------------------------------------------------- | --------------------------------- |
| Registry     | `<release_name>` (hyphens replaced with underscores) | `<release_name>_user`             |
| ID Generator | `<release_name>_idgenerator`                         | `<release_name>_idgenerator_user` |

For example, release `farmer-registry` creates databases `farmer_registry` and `farmer_registry_idgenerator`.

The `postgres-init` subchart handles database and user creation automatically. It generates a random password, stores it in a Kubernetes Secret, and creates the database/user in PostgreSQL.

{% hint style="info" %}
The `postgres-init` chart uses the Helm `lookup` function to check if the DB user secret already exists. If it does, the secret is **not overwritten** -- the existing password is preserved. The secret is annotated with `helm.sh/resource-policy: keep` so it survives Helm uninstalls.
{% endhint %}

### Keycloak and OIDC

The `keycloak-init` subchart creates:

* The Keycloak **realm** (e.g. `staff-trial`)
* An OIDC **client** (`registry-staff-portal`) with a randomly generated secret
* **RBAC roles** on the client (see below)

The Keycloak Init Job connects to the namespace-local Keycloak using the admin credentials from the `commons-keycloak` secret.

**Default RBAC roles created:**

| Category      | Roles                                                                                                                         |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Operations    | Intake Officer, Intake Validator, Data Editor, Data Validator, Data Supervisor, Integration Manager, Operations Administrator |
| Configuration | Schema Designer, Integration Specialist, Reference Data Specialist, Technical Administrator                                   |

See [RBAC Roles and Permissions](https://docs.openg2p.org/registry/design/detailed-design-notes/rbac-roles-and-permissions) for detailed role descriptions.

**Keycloak-init parameters:**

| Parameter                                  | Default                      | Description                               |
| ------------------------------------------ | ---------------------------- | ----------------------------------------- |
| `keycloak-init.enabled`                    | `true`                       | Enable/disable Keycloak client creation.  |
| `keycloak-init.keycloak.url`               | `http://commons-keycloak:80` | Internal Keycloak URL.                    |
| `keycloak-init.keycloak.user`              | `admin`                      | Keycloak admin username.                  |
| `keycloak-init.keycloak.existingSecret`    | `commons-keycloak`           | K8s Secret containing the admin password. |
| `keycloak-init.keycloak.existingSecretKey` | `admin-password`             | Key within the secret.                    |

### ID Generator

The ID Generator subchart (`idgenerator`) provides unique ID generation for registrants. Configuration is under `idgenerator.idGenerator.appConfig`:

```yaml
idgenerator:
  idGenerator:
    appConfig:
      idTypes:
        farmer_id:
          idLength: 12
        household_id:
          idLength: 10
      poolMinThreshold: 1000
      poolGenerationBatchSize: 5000
      poolCheckIntervalSeconds: 30
```

| Parameter                  | Default                               | Description                                       |
| -------------------------- | ------------------------------------- | ------------------------------------------------- |
| `idTypes`                  | `farmer_id` (12), `household_id` (10) | Map of ID type names to their configuration.      |
| `poolMinThreshold`         | `1000`                                | Minimum IDs in pool before regeneration triggers. |
| `poolGenerationBatchSize`  | `5000`                                | Number of IDs generated per batch.                |
| `poolCheckIntervalSeconds` | `30`                                  | How often the pool level is checked.              |

### Component toggles

Each application component can be individually enabled or disabled:

```yaml
staffPortalApi:
  enabled: true     # Staff Portal API

staffPortalUi:
  enabled: true     # Staff Portal UI (Next.js frontend)

partnerApi:
  enabled: true     # Partner/external integration API

benePortalApi:
  enabled: false    # Beneficiary Portal API (disabled by default)

celeryBeatProducer:
  enabled: true     # Celery periodic task scheduler

celeryWorker:
  enabled: true     # Celery background worker

redis:
  enabled: true     # Redis (broker for Celery)

idgenerator:
  enabled: true     # ID Generator service

keycloak-init:
  enabled: true     # Keycloak OIDC client/role setup
```

## Key concepts and notes

### Template-driven defaults

Many values in `values.yaml` use Go template expressions (e.g. `{{ .Release.Name }}`, `{{ .Release.Namespace }}`). These are resolved at install time, making the chart portable across different release names and namespaces without manual edits.

When a value contains a template that is referenced by another template, the chart uses the `tpl` function to ensure nested resolution. For example:

```yaml
# global.keycloakBaseUrl is itself a template:
keycloakBaseUrl: 'https://keycloak.{{ .Release.Namespace }}.openg2p.org'

# keycloakIssuerUrl must use tpl to resolve keycloakBaseUrl:
keycloakIssuerUrl: '{{ tpl .Values.global.keycloakBaseUrl $ }}/realms/{{ tpl .Values.global.keycloakRealm $ }}'
```

### Secret lifecycle

The chart involves two distinct secret flows:

1. **Database secrets** -- Created by `postgres-init` using Helm's `lookup` function. If the secret already exists, it is preserved. Annotated with `helm.sh/resource-policy: keep` to survive uninstalls.
2. **OIDC client secret** -- Created by `keycloak-init`'s `client-secrets.yaml` template with a random password. The Keycloak Init Job reads this secret and pushes it to Keycloak when creating the OIDC client.

{% hint style="warning" %}
If you uninstall and reinstall the chart, the database may retain the old password while a new secret is generated. Ensure secrets are not manually deleted between installs if the databases persist.
{% endhint %}

### Subchart isolation

The ID Generator runs its own `postgres-init` instance for its database. To avoid Kubernetes resource name collisions with the parent chart's `postgres-init`, the subchart uses `nameOverride: idgen-pg-init`. This keeps ServiceAccount and Job names unique and within the Kubernetes 63-character label limit.

### Shared commons services

The chart references several services from the `commons` release by their internal Kubernetes service names:

| Service         | Default internal name                   |
| --------------- | --------------------------------------- |
| PostgreSQL      | `commons-postgresql`                    |
| Keycloak        | `commons-keycloak:80`                   |
| MinIO           | `minio.<namespace>.openg2p.org`         |
| IAM             | `commons-services-iam-staff-portal-api` |
| Keymanager      | `commons-services-keymanager`           |
| Master Data API | `commons-services-master-data-api`      |

These names assume the commons release is named `commons`. Override the corresponding global parameters if your commons release uses a different name.

## Troubleshooting

### Secret ownership conflict on install

```
Error: Secret "xyz" in namespace exists and cannot be imported into the current release
```

This occurs when a Kubernetes Secret already exists and is owned by a different Helm release. Common causes:

* The `keycloak-init` subchart's default realm configuration includes clients (e.g. `openg2p-superset`) that are already created by the commons release. Override the `keycloak-init.realms` section to include only the registry-specific realm and clients.
* The `authClientSecret` name collides with another registry release in the same namespace. See the note on multiple releases below.

### Keycloak Init Job fails with `CreateContainerConfigError`

The Job cannot find the Keycloak admin secret. Ensure:

* The commons release is installed and the `commons-keycloak` secret exists in the namespace.
* If your commons release name differs, update `keycloak-init.keycloak.existingSecret` accordingly.

### IAM `Invalid Login Provider Id`

The `LOGIN_PROVIDER_ID` in the Staff Portal UI must match a configured login provider in the IAM service database. The default value `4` may not exist in your environment. Check the IAM service's login provider configuration and update the value in `staffPortalUi.envVars.LOGIN_PROVIDER_ID`.

### Database password mismatch after reinstall

If the chart is uninstalled and the DB user secret is deleted manually, but the database user persists in PostgreSQL with the old password, a fresh install will generate a new random password that does not match. To resolve:

* Delete the database user from PostgreSQL before reinstalling, or
* Recreate the secret with the correct password before installing.

## Installing multiple releases

The chart can be installed multiple times in the same namespace with different release names (e.g. `farmer-registry` and `livestock-registry`). Most resource names are derived from `{{ .Release.Name }}` and will not collide. However, the following values are currently hardcoded and **will clash**:

| Parameter                 | Hardcoded value         | Impact                                        |
| ------------------------- | ----------------------- | --------------------------------------------- |
| `global.authClientId`     | `registry-staff-portal` | Both releases create the same Keycloak client |
| `global.authClientSecret` | `registry-staff-portal` | Both releases try to own the same K8s Secret  |
| `keycloak-init` clientId  | `registry-staff-portal` | Duplicate client in Keycloak                  |

{% hint style="warning" %}
When installing multiple registry releases in the same namespace, you **must** override `global.authClientId`, `global.authClientSecret`, and the `keycloak-init.realms` clientId to be unique per release (e.g. `farmer-registry-staff-portal`).
{% endhint %}

## Source code and references

* **Chart source**: [openg2p-registry-gen2-deployment](https://github.com/OpenG2P/openg2p-registry-gen2-deployment)
* **Helm repository**: `https://openg2p.github.io/openg2p-helm`
* **RBAC documentation**: [RBAC Roles and Permissions](https://docs.openg2p.org/registry/design/detailed-design-notes/rbac-roles-and-permissions)
* **Commons chart**: [OpenG2P Commons Helm Chart](https://docs.openg2p.org/deployment/concepts/openg2p-commons-helm-chart)

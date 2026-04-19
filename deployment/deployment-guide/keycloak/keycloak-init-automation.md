---
description: Automate Keycloak realm and client creation using the keycloak-init tool
---

# Keycloak Init Automation

## Overview

The **keycloak-init** tool automates the creation of Keycloak realms and clients. It is useful during environment setup where multiple clients need to be created in bulk across one or more realms. The tool comprises a Python script packaged as a Docker image and a Helm chart for Kubernetes deployment.

### Source code

[https://github.com/OpenG2P/keycloak-init](https://github.com/OpenG2P/keycloak-init/tree/develop)

## Functionality

* **Realm management**: Define any number of realms. If a realm does not exist, it is created automatically. If it already exists, it is left untouched.
* **Client creation**: Create multiple clients under each realm with appropriate OIDC settings, protocol mappers, and audience configuration.
* **Client secrets**: Automatically generated and stored as Kubernetes secrets in your namespace. Module Helm charts can securely read these secrets instead of passing them as parameters during installation.
* **Client roles**: Client-specific roles (e.g., `Admin`, `consoleAdmin`) are created as specified. Supports composite roles that contain other roles.
* **Themes**: Optionally apply login and admin themes to each realm (e.g., `openg2p-admin` for the master realm, `staff-portal` for the staff realm). Themes are only updated if they differ from the current setting.
* **Users**: Optionally create users with temporary passwords and assign realm and client roles. Users are prompted to change their password on first login.
* **Idempotent**: Running the tool multiple times produces the same result. Existing realms, clients, roles, secrets, themes, and users are not modified.

## Configuration

The keycloak-init chart ships with no default realms or clients. The calling chart (or user) must define all realms and clients in `values.yaml` under the `realms` key. This ensures that parent chart overrides fully replace the configuration rather than merging with defaults.

Each realm is a map entry with its clients listed underneath:

```yaml
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
      - clientId: openg2p-sr
        name: Social Registry
        redirectUris:
          - "*"
      - clientId: openg2p-superset
        name: Superset
        redirectUris:
          - "*"
        clientRoles:
          - "Admin"
  agent:
    clients: []
```

Realms with no clients can be defined with `clients: []` — they will still be created in Keycloak. The `themes` section is optional; if omitted, the realm's themes are left unchanged.

### Themes

Login and admin themes can be applied per realm. The theme names must match themes already installed in Keycloak (e.g., via the [keycloak-themes](https://github.com/OpenG2P/keycloak-themes) image).

Available OpenG2P themes (from [keycloak-themes](https://github.com/OpenG2P/keycloak-themes)):

| Theme Name      | Type         | Description                   |
| --------------- | ------------ | ----------------------------- |
| `openg2p-admin` | Login, Admin | OpenG2P branded admin console |
| `staff-portal`  | Login, Admin | Staff portal theme            |
| `g2p-advisor`   | Login        | G2P Advisor login theme       |

Each theme folder contains `login` and/or `admin` subdirectories. The theme name in Keycloak matches the folder name. Use the same name for both `loginTheme` and `adminTheme` when both types are available:

```yaml
themes:
  loginTheme: staff-portal     # Applied to the realm's login page
  adminTheme: staff-portal     # Applied to the realm's admin console
```

Themes are only updated when they differ from the current setting in Keycloak, keeping the operation idempotent.

Each client supports the following parameters:

| Parameter      | Required | Description                                                              |
| -------------- | -------- | ------------------------------------------------------------------------ |
| `clientId`     | Yes      | Unique client identifier.                                                |
| `name`         | No       | Display name. Defaults to `clientId`.                                    |
| `redirectUris` | No       | List of valid redirect URIs. Defaults to `["*"]`.                        |
| `secret`       | No       | Client secret. If not provided, a random secret is generated and stored. |
| `clientRoles`  | No       | List of client roles to create. See below.                               |

### Client roles

Roles can be defined as simple strings or as objects with composite child roles. Both formats can be mixed in the same list:

```yaml
clientRoles:
  # Simple roles (string format)
  - intake-officer
  - data-editor
  - data-validator
  # Composite role (object format) — contains the roles listed under composites
  - name: super-admin
    composites:
      - intake-officer
      - data-editor
      - data-validator
```

Composite roles are created in two passes: all roles are created first, then composite relationships are established. This is fully backward compatible — existing charts that pass `clientRoles` as a list of strings continue to work unchanged.

### Users

Users can be optionally created under each realm. Users are created after clients and roles so that role assignments succeed. If a user already exists, creation is skipped (idempotent).

```yaml
users:
  - username: admin@openg2p.org
    password: changeme
    email: admin@openg2p.org
    realmRoles:
      - default-roles-staff
    clientRoleMappings:
      registry-staff-portal:
        - registry-ops-super-operator
        - registry-config-super-configurator
```

| Parameter             | Required | Description                                                              |
| --------------------- | -------- | ------------------------------------------------------------------------ |
| `username`            | Yes      | Login username.                                                          |
| `password`            | No       | Initial password. Required only when creating a new user. Marked as temporary — user must change on first login. If the user already exists and only role assignments are needed, this can be omitted. |
| `email`               | No       | Email address.                                                           |
| `firstName`           | No       | First name. Defaults to the username.                                    |
| `lastName`            | No       | Last name. Defaults to empty.                                            |
| `realmRoles`          | No       | List of realm-level role names to assign.                                |
| `clientRoleMappings`  | No       | Map of client ID to list of client role names to assign.                 |

{% hint style="info" %}
The initial password is always set as temporary. The user will be prompted to change it on first login.
{% endhint %}

## Helm chart

### Prerequisites

A Keycloak **admin** user with permissions to create realms, clients, and roles.

### Installation

{% hint style="info" %}
The Helm chart must be installed on the cluster and namespace of interest (e.g., `sandbox`) since all client secrets are created in the same namespace. The cluster and namespace may not be the same as where Keycloak itself runs.
{% endhint %}

1. Clone the [keycloak-init repo](https://github.com/OpenG2P/keycloak-init/tree/develop).
2. Create a secret for the Keycloak admin **in the installation namespace**. You may create this using Rancher instead of command line:
   * Type: `Opaque`
   * Secret name: `keycloak-admin`
   * Key: `keycloak-admin-password`
   * Value: _\<password of the Keycloak admin user>_
3. Review and update `values.yaml`. Pay attention to the following:

```yaml
keycloak:
  url: "https://keycloak2.openg2p.org"
  user: "admin"
  password: ""
  existingSecret: "keycloak-admin"
  existingSecretKey: "keycloak-admin-password"
```

4. Review the `realms` section for the list of realms and clients. Update as required.
5. Run the Helm chart:

```bash
helm -n <namespace> install keycloak-init .
```

6. Verify:
   * Realms have been created on Keycloak (if they did not already exist).
   * Clients have been created on Keycloak with the expected client roles.
   * Kubernetes secrets for all clients have been created in the namespace.

### Versions

| Helm Chart Version                                               | Date        | Contents                                                                                        |
| ---------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| [**1.0.0**](https://github.com/OpenG2P/keycloak-init/tree/1.0.0) | 17 Apr 2026 | Stable version. No diff w.r.t previous version (0.0.0-develop, Mar 2026).                       |
| 0.0.0-develop                                                    | Mar 2026    | Realm creation, composite client roles, global.keycloakBaseUrl fallback, suffix on realm names. |

### Tear down

Uninstall the Helm chart:

```bash
helm -n <namespace> uninstall keycloak-init
```

{% hint style="warning" %}
Uninstalling the Helm chart **does not delete** realms or clients on Keycloak, nor the Kubernetes secrets. Delete them manually:

* Keycloak clients and realms (via the Keycloak Admin console)
* Kubernetes secrets for all clients (via Rancher or command line)
{% endhint %}

## Docker image

The Python script is packaged as a Docker image published to Docker Hub:

```
docker.io/openg2p/keycloak-init:<branch-name>
```

The image tag corresponds to the Git branch name. A GitHub Actions workflow automatically builds and publishes the image on every push to the `docker/` directory.

## CI/CD

Two GitHub Actions workflows are configured:

| Workflow           | Trigger paths                                       | Description                                  |
| ------------------ | --------------------------------------------------- | -------------------------------------------- |
| **Docker Publish** | `docker/**`, `.github/workflows/docker-publish.yml` | Builds and pushes Docker image to Docker Hub |
| **Helm Publish**   | `helm/**`, `.github/workflows/helm-publish.yml`     | Packages and publishes the Helm chart        |

## Local testing

A Docker Compose-based test setup is provided under `tests/` to run the tool locally against a real Keycloak instance.

### Steps

1. Start Keycloak:

```bash
cd tests
docker compose up keycloak -d
```

2. Wait for Keycloak to be healthy. You can verify by accessing [http://localhost:8080](http://localhost:8080) in a browser.
   * Admin credentials: `admin` / `admin`
3. Review `tests/local_clients.yaml` for the test realm and client definitions.
4. Run the init script:

```bash
docker compose up --build --no-deps keycloak-init
```

5. Log into the Keycloak Admin console at [http://localhost:8080](http://localhost:8080) and verify that the realm and clients have been created.
6. To stop and clean up:

```bash
docker compose down
```

Alternatively, run everything in one command using the test script:

```bash
./run_docker_test.sh
```

{% hint style="info" %}
The local Keycloak instance runs version 24.0.5 in dev mode.
{% endhint %}

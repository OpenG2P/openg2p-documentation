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
* **Client roles**: Client-specific roles (e.g., `Admin`, `consoleAdmin`) are created as specified.
* **Namespace suffix**: A suffix (default: Kubernetes namespace) is appended to client names to distinguish clients created for different namespaces.
* **Idempotent**: Running the tool multiple times produces the same result. Existing realms, clients, roles, and secrets are not modified or regenerated.

## Configuration

Realms and their clients are defined in `values.yaml` under the `realms` key. Each realm is a map entry with its clients listed underneath:

```yaml
realms:
  master:
    clients:
      - clientId: 'openg2p-sr-{{ .suffix }}'
        name: 'Social Registry {{ .suffix }}'
        redirectUris:
          - "*"
      - clientId: 'openg2p-superset-{{ .suffix }}'
        name: 'Superset {{ .suffix }}'
        redirectUris:
          - "*"
        clientRoles:
          - "Admin"
  another-realm:
    clients:
      - clientId: 'my-app-{{ .suffix }}'
        name: 'My App {{ .suffix }}'
        redirectUris:
          - "*"
```

Each client supports the following parameters:

| Parameter      | Required | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `clientId`     | Yes      | Unique client identifier. Supports `{{ .suffix }}` template.                |
| `name`         | No       | Display name. Defaults to `clientId`.                                       |
| `redirectUris` | No       | List of valid redirect URIs. Defaults to `["*"]`.                           |
| `secret`       | No       | Client secret. If not provided, a random secret is generated and stored.    |
| `clientRoles`  | No       | List of client role names to create.                                        |

Default clients are listed in [values.yaml](https://github.com/OpenG2P/keycloak-init/blob/develop/helm/values.yaml).

## Helm chart

### Prerequisites

A **client manager** user on Keycloak with limited permissions:

* User name (example: `client-manager@openg2p.org`)
* Password-based credentials
* Roles (limited to only these):
  * `default-role-master`
  * `manage-clients`
  * `query-clients`
  * `view-clients`

### Installation

{% hint style="info" %}
The Helm chart must be installed on the cluster and namespace of interest (e.g., `sandbox`) since all client secrets are created in the same namespace. The cluster and namespace may not be the same as where Keycloak itself runs.
{% endhint %}

1. Clone the [keycloak-init repo](https://github.com/OpenG2P/keycloak-init/tree/develop).
2. Create a secret for the client manager **in the installation namespace**. You may create this using Rancher instead of command line:
   * Type: `Opaque`
   * Secret name: `keycloak-client-manager`
   * Key: `keycloak-client-manager-password`
   * Value: _\<password of the client manager user>_
3. Review and update `values.yaml`. Pay attention to the following:

```yaml
keycloak:
  url: "https://keycloak2.openg2p.org"
  user: "client-manager@openg2p.org"
  password: ""
  existingSecret: "keycloak-client-manager"
  existingSecretKey: "keycloak-client-manager-password"
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

| Helm Chart Version | Last Modified | Contents                                                                                          |
| ------------------ | ------------- | ------------------------------------------------------------------------------------------------- |
| 0.0.0-develop      | Mar 2026      | Realm creation added. Clients are now defined under realms.                                       |
| 0.0.0-develop      | Jan 2026      | Tested version. After sufficient usage, this will be tagged to a fixed version. Compatible with Keycloak 24.0.5. |

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

| Workflow           | Trigger paths                                  | Description                                      |
| ------------------ | ---------------------------------------------- | ------------------------------------------------ |
| **Docker Publish** | `docker/**`, `.github/workflows/docker-publish.yml` | Builds and pushes Docker image to Docker Hub     |
| **Helm Publish**   | `helm/**`, `.github/workflows/helm-publish.yml`     | Packages and publishes the Helm chart            |

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


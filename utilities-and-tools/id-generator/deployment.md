---
description: >-
  Deployment guide for the ID Generator service — Helm chart installation,
  configuration, Docker setup, and local development.
---

# Deployment

## Helm chart (Kubernetes)

The `openg2p-id-generator` Helm chart deploys the service on Kubernetes, following OpenG2P conventions.

### Prerequisites

* Kubernetes 1.24+
* Helm 3.x
* PostgreSQL (typically `commons-postgresql` in the OpenG2P cluster)
* Istio (optional, for VirtualService routing)

### Quick install

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

helm install id-generator openg2p/openg2p-id-generator \
  -n <namespace> --create-namespace
```

### Install with custom ID types

```bash
helm install id-generator openg2p/openg2p-id-generator \
  -n trial --create-namespace \
  -f my-values.yaml
```

Example `my-values.yaml`:

```yaml
global:
  idGeneratorHostname: idgenerator.production.openg2p.org
  postgresqlHost: my-postgresql

idGenerator:
  replicaCount: 3
  appConfig:
    idTypes:
      farmer_id:
        idLength: 12
      household_id:
        idLength: 10
      national_id:
        idLength: 12
    poolMinThreshold: 5000
    poolGenerationBatchSize: 10000
```

### Upgrade

```bash
helm upgrade id-generator openg2p/openg2p-id-generator -n trial -f my-values.yaml
```

To add or remove ID types, update `appConfig.idTypes` and run `helm upgrade`. Pods restart with the new ConfigMap.

### Uninstall

```bash
helm uninstall id-generator -n trial
```

{% hint style="info" %}
The database and its data are preserved after uninstall. The postgres-init Job uses `resource-policy: keep`.
{% endhint %}

### Helm values reference

#### Global parameters

| Parameter                             | Description                                | Default                        |
| ------------------------------------- | ------------------------------------------ | ------------------------------ |
| `global.idGeneratorHostname`          | Hostname for Istio VirtualService          | `idgenerator.trial.openg2p.org`|
| `global.postgresqlHost`              | PostgreSQL server host                     | `commons-postgresql`           |

#### Application config

| Parameter                                        | Description                                    | Default  |
| ------------------------------------------------ | ---------------------------------------------- | -------- |
| `idGenerator.appConfig.idTypes`                  | Map of ID type name → config                   | See below|
| `idGenerator.appConfig.idTypes.<name>.idLength`  | Number of digits (2–32)                        | —        |
| `idGenerator.appConfig.poolMinThreshold`         | Min available IDs before replenishment         | `1000`   |
| `idGenerator.appConfig.poolGenerationBatchSize`  | IDs generated per replenishment cycle          | `5000`   |
| `idGenerator.appConfig.poolCheckIntervalSeconds` | Seconds between pool checks                    | `30`     |

Default ID types:

```yaml
idTypes:
  farmer_id:
    idLength: 12
  household_id:
    idLength: 10
```

#### Scaling

| Parameter                              | Description                | Default |
| -------------------------------------- | -------------------------- | ------- |
| `idGenerator.replicaCount`            | Number of pod replicas     | `1`     |
| `idGenerator.autoscaling.enabled`     | Enable HPA                 | `false` |
| `idGenerator.autoscaling.minReplicas` | Minimum replicas           | `1`     |
| `idGenerator.autoscaling.maxReplicas` | Maximum replicas           | `5`     |

#### Istio

| Parameter                                    | Description              | Default     |
| -------------------------------------------- | ------------------------ | ----------- |
| `idGenerator.istio.enabled`                 | Enable Istio resources   | `true`      |
| `idGenerator.istio.virtualservice.enabled`  | Create VirtualService    | `true`      |
| `idGenerator.istio.virtualservice.gateway`  | Istio gateway name       | `internal`  |
| `idGenerator.istio.virtualservice.prefix`   | URL prefix match         | `/v1/idgenerator/` |

### Startup sequence

1. **postgres-init Job** — creates the database and user in PostgreSQL
2. **Init container** — waits until the database is accessible with the correct credentials
3. **Main container** — starts the service, creates tables, fills the initial pool
4. **Startup probe** — waits up to 5 minutes for the service to be ready

### Kubernetes resources created

| Resource       | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| ConfigMap      | Application config YAML (ID types, filters, pool)      |
| Deployment     | ID Generator pods                                      |
| Service        | ClusterIP service (port 80 → 8000)                     |
| Secret         | Auto-generated DB user password                        |
| Job            | postgres-init (creates database and user)              |
| VirtualService | Istio routing (if enabled)                             |
| HPA            | Horizontal Pod Autoscaler (if enabled)                 |

---

## Docker

### Docker Compose (recommended for local)

Start both PostgreSQL and the service with a single command:

```bash
docker compose up --build
```

This will:

1. Start PostgreSQL 16 with a persistent volume
2. Wait for PostgreSQL to be healthy
3. Build the ID Generator image and start it on port 8000

```bash
docker compose down          # Stop (data preserved)
docker compose down -v       # Stop and delete data
```

### Docker run (with existing database)

```bash
# Build
docker build -t id-generator:latest \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ") .

# Run
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=idgenerator \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  id-generator:latest
```

{% hint style="info" %}
`host.docker.internal` allows the container to reach PostgreSQL on the host (macOS/Windows). On Linux, use `--network=host` or the host's IP address.
{% endhint %}

---

## Local development (without Docker)

### Prerequisites

* Python 3.11+
* PostgreSQL 14+

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the service
pip install -e .

# Set database connection
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=idgenerator
export DB_USER=postgres
export DB_PASSWORD=postgres

# Run
uvicorn id_generator.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment variables

| Variable           | Default              | Description                    |
| ------------------ | -------------------- | ------------------------------ |
| `DB_HOST`          | `localhost`          | PostgreSQL host                |
| `DB_PORT`          | `5432`               | PostgreSQL port                |
| `DB_NAME`          | `idgenerator`        | Database name                  |
| `DB_USER`          | `postgres`           | Database user                  |
| `DB_PASSWORD`      | `postgres`           | Database password              |
| `CONFIG_PATH`      | `config/default.yaml`| Path to YAML config file       |
| `UVICORN_WORKERS`  | `1`                  | Uvicorn worker processes       |
| `UVICORN_LOG_LEVEL`| `info`               | Log level                      |

---
description: >-
  Deployment guide for the Audit Manager — local development with Docker
  Compose, Helm chart installation, configuration reference, operational
  runbook, and security considerations.
---

# Deployment

## Local development

### With Docker Compose (one command)

```bash
docker compose up --build
```

Starts Postgres, Kafka (KRaft single-node), and the audit-manager service.
After a few seconds:

* API: http://localhost:8000/v1/auditmanager/
* Swagger: http://localhost:8000/v1/auditmanager/docs
* Health: http://localhost:8000/v1/auditmanager/health

### Smoke test

```bash
curl -sX POST http://localhost:8000/v1/auditmanager/events \
  -H 'content-type: application/json' -d '{
    "specversion": "1.0",
    "id": "demo-1",
    "source": "/demo",
    "type": "org.openg2p.auth.login",
    "time": "2026-04-22T14:03:21Z",
    "data": {
      "actor":   { "type": "user", "id": "u_1", "name": "demo" },
      "action":  "login",
      "outcome": "success"
    }
  }'
```

Expected: `202 Accepted` immediately. Within a few seconds the row appears
in Postgres:

```bash
docker compose exec postgres psql -U postgres -d auditmanager \
  -c "SELECT id, type, actor_id, outcome, occurred_at FROM audit_events ORDER BY ingested_at DESC LIMIT 5;"
```

### Running outside Docker

```bash
pip install -e .
export DB_HOST=localhost DB_NAME=auditmanager DB_USER=postgres DB_PASSWORD=postgres
export AUDIT_MANAGER__KAFKA__BOOTSTRAP_SERVERS=localhost:9092
uvicorn audit_manager.main:app --reload
```

## Kubernetes deployment

### Prerequisites

* A Kubernetes cluster with the OpenG2P `common` and `postgres-init`
  charts available (pulled from https://openg2p.github.io/openg2p-helm).
* A running Kafka cluster reachable from the target namespace.
* A PostgreSQL instance reachable from the target namespace.

### Install

The Audit Manager chart is published to the shared **GitLab** catalogue
(`openg2p/charts`), not the GitHub Helm repo:

```bash
# openg2p/charts — the numeric project id is required (the encoded-path form
# breaks Rancher's link resolution). Public: no credentials needed.
helm repo add openg2p https://gitlab.com/api/v4/projects/84460547/packages/helm/stable
helm repo update

helm install audit-manager openg2p/openg2p-audit-manager \
  -n openg2p --create-namespace \
  -f values-<env>.yaml
```

{% hint style="info" %}
Same URL in **Rancher** (Apps → Repositories → *http(s) URL to an index generated
by Helm*) — it lists every OpenG2P chart, not just this one. See
[Publishing to GitLab](../../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md).
{% endhint %}

### Minimal per-environment values file

```yaml
# values-prod.yaml
global:
  auditManagerHostname: auditmanager.prod.openg2p.org
  postgresqlHost: commons-postgresql
  kafkaBootstrapServers: "commons-kafka:9092"

auditManager:
  image:
    tag: "1.0.0"
  autoscaling:
    minReplicas: 3
    maxReplicas: 12
  topicInit:
    partitions: 12
    replicationFactor: 3
```

### What the chart provisions, in order

1. **`postgres-init`** subchart creates the `auditmanager` DB + user (Helm
   hook, weight 0).
2. **Kafka topic init Job** (`topicInit.enabled: true`, hook weight 10)
   creates `openg2p.audit.events` and `openg2p.audit.dlq` with the
   configured partitions, replication factor, and retention. Idempotent —
   creates if missing, grows partitions if below target.
3. **ConfigMap** rendering `config/config.yaml` from
   `auditManager.appConfig.*`.
4. **Deployment** with:
   * `postgres-checker` initContainer that blocks until the DB is reachable.
   * Main container running `uvicorn audit_manager.main:app`.
   * Startup / liveness / readiness probes on `/v1/auditmanager/health`.
   * Rolling update strategy.
5. **Service** (ClusterIP) + **Istio VirtualService** routing
   `/v1/auditmanager/` to the service.
6. **HorizontalPodAutoscaler** (CPU-based, 2–12 replicas by default).

### Kafka topic management alternatives

If topics are managed outside this chart (e.g. a Strimzi `KafkaTopic` CR
or a separate platform-level GitOps repo), set:

```yaml
auditManager:
  topicInit:
    enabled: false
```

## Uninstall

`helm uninstall audit-manager` cleans up the workloads, Service, Istio
VirtualService, and Helm-owned secrets/configmaps. It does **not**:

* Drop the Postgres database + role created by the `postgres-init`
  subchart hook (those live inside `commons-postgresql`, not in the
  audit-manager release).
* Delete the Kafka topics created by the `topicInit` Helm hook.
* Remove leftover hook Jobs (postgres-init, topic-init) that pin
  themselves with `helm.sh/hook-delete-policy`.

Use the bundled
[`scripts/uninstall-audit-manager.sh`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/scripts/uninstall-audit-manager.sh)
to do the full teardown. Same flag style as the AWE uninstaller.

```bash
# 1. Always dry-run first to see what will go
./scripts/uninstall-audit-manager.sh --namespace trial --dry-run

# 2. Real uninstall — interactive confirmation
./scripts/uninstall-audit-manager.sh --namespace trial

# 3. Full blast including Kafka topics, no prompt (CI / scripted teardown)
./scripts/uninstall-audit-manager.sh --namespace trial \
  --delete-kafka-topics --yes
```

What it does, in order:

| Step | Action |
| --- | --- |
| 1 | `helm uninstall <release>` |
| 2 | Delete leftover Jobs + completed pods (postgres-init, topic-init) |
| 3 | Sweep any other Secrets / ConfigMaps labelled with the release |
| 4 | Drop Postgres DB + role inside `commons-postgresql` |
| 5 | (optional, `--delete-kafka-topics`) delete `openg2p.audit.events` and `openg2p.audit.dlq` from `commons-kafka` |
| 6 | Delete PVCs labelled with the release (audit-manager has none today; included for parity) |
| 7 | Delete PVs released by step 6 (skip with `--keep-pvs`) |

Common flags (full list in the script header — `--help`):

| Flag | Default | Purpose |
| --- | --- | --- |
| `--release <name>` | `audit-manager` | Helm release to uninstall |
| `--namespace <ns>` | required | Namespace the release is in |
| `--postgres-release <name>` | `commons-postgresql` | Helm release name of the shared Postgres |
| `--kafka-release <name>` | `commons-kafka` | Helm release name of the shared Kafka |
| `--delete-kafka-topics` | off | Also drop the audit topic + DLQ |
| `--keep-pvs` | off | Delete PVCs but keep PVs (useful when the underlying volumes hold long-retained audit data and you intend to reattach them on a new install) |
| `--dry-run` | off | Print actions, change nothing |
| `--yes` | off | Skip the interactive "type the release name" confirmation |

Requires `kubectl` (cluster admin), `helm`, `bash 4+`, `jq`.

## Configuration reference

All configuration is layered, highest priority first:

1. Environment variables (with `__` as nested key delimiter)
2. YAML config file at `$CONFIG_PATH` (default `/app/config/config.yaml`
   in the container)
3. Built-in defaults in `src/audit_manager/config.py`

### Environment variables

| Variable                                              | Purpose                 | Default                      |
| ----------------------------------------------------- | ----------------------- | ---------------------------- |
| `DB_HOST` / `DB_PORT` / `DB_NAME`                     | Postgres connection     | localhost/5432/auditmanager  |
| `DB_USER` / `DB_PASSWORD`                             | Postgres credentials    | postgres/postgres (dev only) |
| `AUDIT_MANAGER__KAFKA__BOOTSTRAP_SERVERS`             | Kafka brokers           | `kafka:9092`                 |
| `AUDIT_MANAGER__KAFKA__TOPIC`                         | Audit events topic      | `openg2p.audit.events`       |
| `AUDIT_MANAGER__INGEST__QUEUE_MAX_SIZE`               | In-process queue bound  | `10000`                      |
| `AUDIT_MANAGER__DATABASE__PARTITION_RETENTION_MONTHS` | Retention in months     | `84` (7 years)               |
| `CONFIG_PATH`                                         | YAML config path        | `config/default.yaml`        |
| `UVICORN_HOST` / `UVICORN_PORT` / `UVICORN_WORKERS`   | Uvicorn server settings | 0.0.0.0 / 8000 / 1           |
| `UVICORN_LOG_LEVEL`                                   | Log level               | `info`                       |

### YAML config

See [`config/default.yaml`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/config/default.yaml)
for the full reference. Top-level keys:

* `audit_manager.ingest.*` — queue size, batch limits
* `audit_manager.kafka.*` — topic, DLQ, producer/consumer tuning
* `audit_manager.database.*` — partition maintenance knobs

### Helm values

See [`helm/openg2p-audit-manager/values.yaml`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/helm/openg2p-audit-manager/values.yaml) and
[`helm/openg2p-audit-manager/questions.yaml`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/helm/openg2p-audit-manager/questions.yaml)
for the full schema of user-facing values and their Rancher UI groupings.

## Operational runbook

### "Audit events are being rejected with 503"

Check in order:

1. `GET /v1/auditmanager/health` — if it returns 503, the service itself
   is unhealthy (startup incomplete or DB unreachable).
2. Pod logs for `Audit ingest queue full — backpressure` — indicates the
   in-process queue is full. Root causes, in order of likelihood:
   * Kafka is slow or unreachable. Check broker health.
   * Consumer is lagging, causing producer back-pressure (rare here —
     producer and consumer are independent).
   * Instantaneous traffic spike. Scale replicas or raise
     `ingest.queue_max_size`.

### "Consumer lag is growing"

1. Check Postgres health — most common cause.
2. Check consumer group:

   ```
   kafka-consumer-groups.sh --bootstrap-server <broker> \
     --group openg2p-audit-consumer --describe
   ```
3. If lag persists after Postgres recovers, increase replicas (up to
   partition count) or optimize Postgres (indexes, disk IO).

### "Schema-invalid events in Kafka"

Check the DLQ topic `openg2p.audit.dlq` and service logs. Common causes:

* Emitter sending pre-1.0 payloads
* Missing required fields (`actor`, `action`, `outcome`)
* Non-RFC3339 timestamps

The consumer drops malformed events so the main pipeline keeps flowing.
Fix the emitter, then optionally replay from the DLQ.

### "Need to investigate a specific incident"

Indexed query patterns:

```sql
-- Everything a specific actor did in a window
SELECT occurred_at, type, action, outcome, resource_type, resource_id
FROM audit_events
WHERE actor_id = 'u_4421'
  AND occurred_at >= '2026-04-01' AND occurred_at < '2026-05-01'
ORDER BY occurred_at;

-- Everything that happened to a specific resource
SELECT occurred_at, actor_id, action, outcome, reason
FROM audit_events
WHERE resource_type = 'beneficiary' AND resource_id = 'b_1029384756'
ORDER BY occurred_at;

-- All denied or failed events in the last 24h (uses flat `outcome` + `reason`)
SELECT occurred_at, actor_id, type, outcome, reason
FROM audit_events
WHERE outcome IN ('denied', 'failure')
  AND occurred_at > now() - interval '24 hours'
ORDER BY occurred_at DESC;

-- Correlate across services via trace id
SELECT occurred_at, source, type, action, outcome
FROM audit_events
WHERE trace_id = '4bf92f3577b34da6a3ce929d0e0e4736'
ORDER BY occurred_at;

-- Drill into structured extras — show field diffs for a beneficiary update
SELECT id, occurred_at, actor_id, details->'changes' AS changes
FROM audit_events
WHERE type = 'org.openg2p.beneficiary.updated'
  AND resource_id = 'b_1029384756'
ORDER BY occurred_at DESC;

-- All payments above 10k INR (uses details.resource.amount)
SELECT id, occurred_at, actor_id, details->'resource' AS resource
FROM audit_events
WHERE type = 'org.openg2p.payment.approved'
  AND (details->'resource'->>'currency') = 'INR'
  AND (details->'resource'->>'amount')::numeric > 10000
ORDER BY occurred_at DESC;
```

### "Need to grow the Kafka partition count"

The `topicInit` Job idempotently grows partitions on the next `helm
upgrade`. To trigger manually:

```bash
helm upgrade audit-manager openg2p/openg2p-audit-manager \
  -n openg2p -f values-<env>.yaml \
  --set auditManager.topicInit.partitions=24
```

Remember to raise `autoscaling.maxReplicas` accordingly.

### "Need to change retention"

Set `auditManager.appConfig.database.partitionRetentionMonths` and `helm
upgrade`. The partition maintainer picks it up on its next run (hourly by
default).

## Security considerations

* **Authentication:** not built in. Deploy behind Istio / an API gateway
  that enforces service-to-service auth (JWT, mTLS). Direct internet
  exposure of this service is not supported.
* **Authorization:** there is no per-caller authorization at the audit
  service. Any caller with network access can emit events. If that is a
  concern, require a signed JWT at the Istio layer.
* **PII:** see [PII handling](functional-specifications.md#pii-handling).
  The `details` JSONB column may carry structured PII (e.g. field diffs in
  `changes[]`); access to `details` should be restricted to compliance /
  investigators.
* **DB role:** the service's DB user needs only `CONNECT`, `USAGE`,
  `INSERT`, `SELECT` on its schema. A separate read-only role is
  recommended for investigators (no `INSERT` / `UPDATE` / `DELETE` —
  audits are append-only).
* **Tamper evidence:** this first release stores events as-is. If
  compliance requires cryptographic non-repudiation, a subsequent release
  can add hash-chaining at the sink (each row stores `prev_hash` and
  `hash(prev_hash || event)`).
* **Secret handling:** DB password comes from a Kubernetes Secret created
  by the `postgres-init` chart. Never baked into the image. `docs/` never
  contains configuration.

## License

SPDX-License-Identifier: MPL-2.0. Part of the
[OpenG2P](https://www.openg2p.org/) platform.

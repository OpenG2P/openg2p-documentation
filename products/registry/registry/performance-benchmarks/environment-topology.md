# Environment & Topology

The benchmark targets the **OpenG2P 3-node production deployment** defined in
`openg2p-deployment/automation/production`. What runs where — and the
constraints each node imposes — shapes how the tests are run and how results
are interpreted.

## The 3 nodes (default AWS sizing)

| Node | Instance | vCPU / RAM | Disk | Role |
|------|----------|-----------|------|------|
| Reverse Proxy (RP) | `t3a.medium` | **2 / 4 GB** | 64 GB gp3 @ 3000 IOPS | Public ingress: WireGuard endpoint + admin Nginx + TLS. The internet-facing hop. |
| **Compute** | `m5a.4xlarge` | **16 / 64 GB** | 128 GB gp3 @ 3000 IOPS | Single **RKE2 Kubernetes** node. Runs **all** application pods. |
| **Storage** | `t3a.2xlarge` | **8 / 32 GB** | 256 GB gp3 @ 3000 IOPS | **Host PostgreSQL 16** (not a K8s pod) + NFS server. |

Source: `automation/production/aws/aws-config.example.yaml` and `prod-config.example.yaml`.

## How this topology shapes the tests

This topology has concrete implications for how the tests are run:

1. **All app pods share one compute node (16 vCPU / 64 GB).**
   The 1-pod / 2-pod / 3-pod horizontal-scaling test runs on the *same* node, so
   the pods compete for cores with **all the other platform pods** (Keycloak,
   Redis, MinIO, Kafka, Istio, master-data, eSignet, Superset, observability,
   AWE, …). Realistic free headroom for the registry pods is well under
   16 vCPU — budgeted at roughly 8–10 vCPU. Node-level CPU/mem is captured
   throughout each run, and node saturation is treated as a real ceiling, not
   just pod limits.

2. **PostgreSQL is host-based on the storage node — not a K8s pod.**
   It's a single host Postgres on a fixed 8 vCPU / 32 GB VM, so DB "scaling"
   doesn't mean adding DB pods — it means:
   - **postgresql.conf tuning** (shared_buffers, work_mem, effective_cache_size,
     max_connections, autovacuum) — the primary, in-place lever.
   - **Connection pooling** (PgBouncer) in front — usually the real ceiling.
   - **VM resize** as discrete scenarios (e.g. 8/32 → 16/64) — a provisioning
     change, not a `kubectl scale`.
   - Optional **read replica** for the read-heavy search/dedup load.

3. **The storage node is a burstable `t3a` instance (CPU credits).**
   Under sustained DB load — especially the 8-hour soak — a t3a can exhaust
   CPU credits and throttle, which would silently corrupt results. T3
   Unlimited mode on the storage node (or, as an alternative, a temporary
   non-burstable instance of equal vCPU such as `m5a`/`m6a`) is how that risk
   is addressed for DB load tests. The compute node (`m5a`) is non-burstable
   already, so it carries no such caveat.

4. **gp3 at 3000 IOPS / 125 MB/s is a fixed I/O ceiling.**
   Large-table scans (search/dedup over 50–100M rows) and write-heavy phases
   can saturate disk before CPU. Disk IOPS/throughput/await on the storage
   node is tracked alongside CPU for this reason. A gp3 IOPS/throughput bump
   is one of the `db-sweep` scenarios (`test-scenarios.md` §3) for the
   I/O-bound case.

5. **Two ingress points, measured and labeled separately.**
   - **In-cluster** (Locust pod → service ClusterIP): isolates the
     microservice — the source for per-pod capacity and scaling-factor
     numbers.
   - **End-to-end** (through RP Nginx → Istio gateway → Keycloak): the
     real-world latency users see. The RP is only `t3a.medium` (2 vCPU) and
     can itself bottleneck end-to-end throughput — that's a finding, not a
     defect.

6. **Auth is on the hot path.** Every API validates an OIDC token against
   Keycloak (`commons-keycloak`). The load scripts use realistic tokens with
   cache effects accounted for (fetched once, reused until expiry — see
   `locust/api/`), so what's being benchmarked is the registry, not
   Keycloak's token endpoint.

7. **Audit middleware** logs every API call (non-blocking, to
   `commons-services-auditmanager`), adding per-request overhead and its own
   load. It stays enabled throughout, keeping the benchmark
   production-representative.

## Test rig

- **Load generator (Locust):** runs as a pod (or small deployment) on the
  cluster for in-cluster tests, so the generator isn't bottlenecked by the RP
  or the internet. For end-to-end tests, Locust runs from a separate,
  well-provisioned host (not the 3 nodes) hitting the public hostname — never
  co-located on the compute node under test.
- **Metrics:** the prod stack's Prometheus + Grafana (rancher-monitoring) and
  OpenTelemetry + Loki cover pod CPU/mem, node CPU/mem, and app logs. For the
  host Postgres, `node_exporter` / `postgres_exporter` run on the storage node
  for the test window, alongside `pg_stat_statements`.
- **Isolation:** HPA is off and `requests == limits` on the pod under test;
  runs happen during a quiet window on the shared compute node, with
  co-tenant activity on the node recorded at test time.

## Pod configuration

The actual specs the Smoke and Primary tier runs (`staff-api/test-scenarios.md`
§3/§7) ran against — the source other docs in this directory link to rather
than repeating these numbers:

| Service | Pod spec |
|---|---|
| farmer-registry (`staff-portal-api`) | 2 vCPU / 2 GB RAM |
| AWE | 2 vCPU / 2 GB RAM |
| Keycloak | 1 vCPU / 1 GB RAM |
| Master Data Service | to be configured |
| Audit Manager | to be configured |
| ID Generator | to be configured |

AWE and Keycloak are fixed-count pods on the shared compute node regardless
of `staff-portal-api`'s Pod-Scale — the specs above are the ceiling each
independently operates under while `staff-portal-api` scales 1→2→3.
`requests == limits`, HPA off (per the Test rig section above); gunicorn/
uvicorn worker count is tuned separately, tracked in the "Environment pinning
fields" below (the API Dockerfiles default to `NO_OF_WORKERS=8`, sized for a
much larger pod than 2 vCPU).

## PostgreSQL & PgBouncer configuration

From [`postgres-settings/pg-settings.txt`](../postgres-settings/pg-settings.txt)
and [`postgres-settings/pgbouncer-config.txt`](../postgres-settings/pgbouncer-config.txt)
— the storage node (`t3a.2xlarge`, 8 vCPU / 32 GB, ~31 GB usable) is tuned as:

| PostgreSQL parameter | Value | Rationale |
|---|---|---|
| `shared_buffers` | 8 GB | ~25% of RAM |
| `work_mem` | 16 MB | per query operation |
| `maintenance_work_mem` | 2 GB | ~6.5% of RAM |
| `effective_cache_size` | 15.5 GB | ~50% of RAM |

| PgBouncer parameter | Value |
|---|---|
| `listen_port` | 6432 |
| `pool_mode` | transaction |
| `max_client_conn` | 200 |
| `default_pool_size` | 50 |
| `min_pool_size` | 10 |
| `reserve_pool_size` | 10 |
| `reserve_pool_timeout` | 5s |

`max_connections` isn't set in either checked-in config file — not yet
recorded per run.

## Environment pinning fields (recorded per result set)

- Chart version + image tags (registry images, `appVersion`), git SHA.
- **Consent/signature posture** — `global.consentEnforcementEnabled` and
  `global.partnerSignatureValidationEnabled` (both default **on**). With them on,
  each DCI search includes a PM key fetch + CM `/validate` hop, so results are not
  comparable with a gates-off run. See [`test-scenarios.md`](staff-api/test-scenarios.md) §8 "Prep".
- Node instance types + whether T3 Unlimited was enabled on storage.
- Pod resource requests/limits and **gunicorn/uvicorn worker count** (the API
  Dockerfiles default to `NO_OF_WORKERS=8` — see "Pod configuration" above;
  tuned for the actual 2-vCPU pod rather than the Dockerfile default).
- PostgreSQL version + any postgresql.conf/PgBouncer values changed from
  "PostgreSQL & PgBouncer configuration" above.
- Data volume (row counts per register + history + supporting tables).
- Locust version, run location (in-cluster vs external), and config.

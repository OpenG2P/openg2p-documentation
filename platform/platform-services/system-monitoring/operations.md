# Operations Guide

> Concepts are in the [System Monitoring overview](README.md). This is a how-to.
> All commands assume `kubectl` is pointed at the cluster.

## Storage & retention

Logs are stored in **Loki**, which keeps its log chunks in a **dedicated MinIO**
object store installed alongside it (internal-only, in the `observability`
namespace — not the application MinIO). Buckets: `chunks`, `ruler`, `admin`.

### Which PVC to watch

| PVC (namespace `observability`) | Size | What it holds |
| --- | --- | --- |
| **`loki-minio`** | `loki_minio_size` (default `50Gi`) | **All log chunks — WATCH THIS one** |
| `storage-loki-0` | 10Gi | Loki WAL / index cache — low risk |

```bash
kubectl -n observability get pvc                                  # sizes
kubectl -n observability exec deploy/loki-minio -- df -h /export  # current usage
```

### Retention — why storage does NOT grow forever

Retention is **enabled and capped at 7 days** by default. Loki's **compactor**
deletes chunks older than the retention period, so usage converges to roughly
*N days of log volume* rather than growing indefinitely. Verify it's active:

```bash
kubectl -n observability get cm loki -o yaml | grep -E "retention_period|retention_enabled"
# expect: retention_period: 168h   and   retention_enabled: true
```

**To change retention:** set `loki_retention_hours` (default `168` = 7 days) in
`prod-config.yaml` / `single-node-config.yaml` and re-sync the `loki` release.

{% hint style="warning" %}
**Retention deletes by _age_, not _size_.** The `loki-minio` PVC is a fixed size,
and the `nfs-csi` StorageClass has `allowVolumeExpansion: false` (can't grow in
place). So if daily log volume is high enough that *7 days > the PVC size*, the
PVC fills **before** retention kicks in. **Watch `loki-minio`; if it passes ~70–80%**,
either **reduce `loki_retention_hours`** or provision a larger PVC. Best practice:
add a PrometheusRule alerting on `kubelet_volume_stats_used_bytes` for this PVC.
{% endhint %}

> Loki runs in **SingleBinary** mode (one pod) — the OpenG2P cluster has a single
> compute node per environment. Scale out only if compute nodes are added.

## Alerting

Both **log-based** alerts (Loki ruler) and **resource/health** alerts (Prometheus —
OOMKilled, CrashLoopBackOff, memory, pod-not-ready, etc.) flow into the **same
Alertmanager**. Default log alert rules:

| Alert | Fires when |
| --- | --- |
| `HighApplicationErrorRate` | error log rate stays high (warning) |
| `ApplicationFatalOrCrash` | panic / fatal / OutOfMemory logged (critical) |
| `AuthFailureBurst` | burst of auth failures — possible attack (critical) |
| `LoggingPipelineSilent` | no logs received cluster-wide — pipeline broken (critical) |

**Delivering alerts:** set the channel credentials in `prod-config.yaml`
(`alert_smtp_*`, `alert_slack_webhook_url`, `alert_telegram_*`) — until then alerts
are evaluated but **not delivered**.

* **Email** is the recommended default (works with any internal SMTP, no third-party account).
* The **Slack** webhook config also works for **Mattermost** and **Rocket.Chat**
  (same webhook format) — useful where self-hosted chat is required.

## Health checks

```bash
kubectl -n observability get pods                 # Loki, MinIO, OTel agent/gateway
kubectl -n observability logs ds/otel-agent-opentelemetry-collector-agent --tail=20
# is Loki receiving logs? (run from inside the cluster)
# GET http://loki.observability.svc:3100/loki/api/v1/labels  -> should list k8s_* labels
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No logs in Grafana | OTel agent running? Loki pod `1/1` Ready? Time range set and not in Live mode? |
| Loki panels **No data** (pink warning), Prometheus panels OK | Grafana must query Loki at `http://loki.observability.svc:3100` (not the nginx gateway). Hard-refresh; restart `rancher-monitoring-grafana` if the datasource was just updated. |
| "Loki" missing in Grafana | Hard-refresh the browser; confirm you're an Editor (via Rancher) |
| Live tail error `undefined` | Expected — use a range query + auto-refresh (proxy blocks WebSockets) |
| Loki pod `CrashLoopBackOff` | Usually MinIO buckets or DNS — check `kubectl -n observability logs loki-0 -c loki` |
| Alerts not arriving | Channel credentials set in `prod-config.yaml`? Alertmanager receiver configured? |

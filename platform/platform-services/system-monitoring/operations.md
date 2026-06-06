# Operations Guide

> Concepts are in the [System Monitoring overview](README.md). This is a how-to.
> All commands assume `kubectl` is pointed at the cluster.

## Storage & retention

Logs are stored in **Loki**, which keeps its log chunks in a **dedicated MinIO**
object store installed alongside it (internal-only, in the `observability`
namespace — not the application MinIO). Buckets: `chunks`, `ruler`, `admin`.

* **Default retention:** 7 days. Change `loki_retention_hours` in `prod-config.yaml`
  and redeploy.
* **Disk:** sized by `loki_minio_size` (default `50Gi`). Increase if you raise
  retention or log volume.

```bash
# observability components
kubectl -n observability get pods
# disk used by Loki's MinIO
kubectl -n observability exec deploy/loki-minio -- df -h /export
```

> On the single-compute-node deployment Loki runs in **SingleBinary** mode (one
> pod). It can be scaled out only if compute nodes are added.

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
# GET http://loki-gateway.observability.svc/loki/api/v1/labels  -> should list k8s_* labels
```

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No logs in Grafana | OTel agent pod running? Loki pod `2/2`? Time range set and not in Live mode? |
| "Loki" missing in Grafana | Hard-refresh the browser; confirm you're an Editor (via Rancher) |
| Live tail error `undefined` | Expected — use a range query + auto-refresh (proxy blocks WebSockets) |
| Loki pod `CrashLoopBackOff` | Usually MinIO buckets or DNS — check `kubectl -n observability logs loki-0 -c loki` |
| Alerts not arriving | Channel credentials set in `prod-config.yaml`? Alertmanager receiver configured? |

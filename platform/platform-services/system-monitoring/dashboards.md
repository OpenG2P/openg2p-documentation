# Dashboards & Viewing Logs

> Concepts are in the [System Monitoring overview](README.md). This is a how-to.

## The OpenG2P — Logs & Health dashboard

A ready-made dashboard is provisioned automatically. Open Grafana → **Dashboards**
and search for **"OpenG2P"** (`OpenG2P — Logs & Health`).

It combines logs (Loki) and health (Prometheus) in one view:

| Panel | Shows |
| --- | --- |
| Error lines (1h), CrashLooping pods, Total log rate, OOMKilled (1h) | At-a-glance health stats |
| Log volume by namespace | Where logs are coming from / spikes |
| Error rate by service | Which service is erroring |
| Top erroring pods (table) | The noisiest failures right now |
| Pod restarts (15m) | Crash/restart activity |
| Recent errors (logs) | Live list of error lines, click-through to detail |

> _Screenshot: add an image at `.gitbook/assets/system-monitoring-dashboard.png` and embed it here._

**Adding your own dashboards:** drop a dashboard `*.json` into the automation's
`charts/grafana-dashboards/dashboards/` directory; it is imported automatically on
the next deploy (no Grafana restart).

## Viewing logs ad-hoc (Explore)

Use **Explore** (compass icon) → select the **Loki** datasource → write a query in
LogQL. Set a **time range** (top-right) and click **Run query**.

```logql
{k8s_namespace_name="kube-system"}                 # all logs in a namespace
{service_name="esignet"}                           # one service
{k8s_namespace_name=~".+"} |~ `(?i)error|fatal`    # only errors, cluster-wide
{service_name="esignet"} | json | level="ERROR"    # parse JSON logs and filter
```

Useful labels: `k8s_namespace_name`, `k8s_pod_name`, `k8s_container_name`,
`k8s_deployment_name`, `service_name`.

* **Patterns tab** — Loki auto-groups similar log lines into templates, so you can
  spot *"this error happened 4,000×"* without writing a query.
* **Near-real-time:** use the **auto-refresh** dropdown (e.g. `10s`) for live-style updates.

{% hint style="info" %}
**Live tail** (the streaming "Live" button) does **not** work through the Rancher
proxy — it needs WebSockets, which the proxy blocks. Use a range query with
auto-refresh instead.
{% endhint %}

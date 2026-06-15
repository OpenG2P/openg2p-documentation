# View System Logs in Grafana (Loki)

Cluster logs are collected and queried through the **OpenTelemetry + Grafana Loki** stack — there is no OpenSearch in the current deployment. An OpenTelemetry agent (a DaemonSet) tails every pod's logs, ships them through an OTel gateway to **Grafana Loki** (backed by its own dedicated MinIO object store), and you query them in **Grafana** using LogQL. PII is redacted in the OTel pipeline before logs are stored.

{% hint style="info" %}
This replaces the old OpenSearch Dashboards flow. OpenSearch and the Fluentd-based pipeline have been removed; logging is handled cluster-wide by OpenTelemetry + Loki at the infrastructure layer.
{% endhint %}

## Open Grafana

Grafana ships with the cluster's monitoring stack and is reached **through the Rancher UI** — it does not have its own public hostname:

* In Rancher, open the **`local` cluster → Monitoring → Grafana** (Cluster Explorer → Monitoring → Grafana dashboards), or
* port-forward it from your workstation (Wireguard up, kubeconfig set):

  ```bash
  kubectl -n cattle-monitoring-system port-forward svc/rancher-monitoring-grafana 3000:80
  # then open http://localhost:3000
  ```

## View and filter logs

1. **Open Explore** — in Grafana's left menu, click **Explore**, then select the **Loki** data source (top-left dropdown).
2. **Pick the logs you want** with a LogQL label selector. Labels include `namespace`, `pod`, `container`, and `app`:
   * `{namespace="prod"}` — all logs in the `prod` environment namespace.
   * `{namespace="prod", pod=~"commons-services-esignet.*"}` — a specific service.
   * `{namespace="cattle-system"}` — Rancher's own logs.
3. **Filter by content / severity** with pipeline filters:
   * `{namespace="prod"} |= "ERROR"` — lines containing `ERROR`.
   * `{namespace="prod"} |~ "(?i)exception|panic|oom"` — case-insensitive regex match.
   * `{namespace="prod"} |= "ERROR" != "healthcheck"` — include `ERROR`, exclude `healthcheck`.
4. **Set the time range** — use the time picker (top-right): Last 15 minutes, Last 1 hour, Today, or a custom range.
5. **Save / share** — pin a useful query to a dashboard panel, or use **Share** to copy a link that reproduces the query + time range.
6. **Inspect a line** — expand any log line to see its labels and the full message; click a label value to add it to the query.

## Log-based alerts

Loki's ruler evaluates **LogQL alert rules** (high error rate, fatals/panics/OOM, auth-failure bursts, and a dead-man's-switch if the pipeline goes silent) and forwards firing alerts to the same **Alertmanager** that ships with Rancher monitoring. Tune the thresholds per environment; see the alerting configuration in the production automation.

{% hint style="info" %}
The production automation installs this whole pipeline (OTel agent → gateway → Loki + dedicated MinIO → Grafana datasource) as part of the infrastructure stage — no manual setup is needed.
{% endhint %}

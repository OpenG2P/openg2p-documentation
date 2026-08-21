# Setup & Configuration

> Concepts are in the [System Monitoring overview](README.md). This is a how-to.

## Installation

The monitoring stack is **installed automatically** as part of infrastructure
deployment — no manual steps. That includes the single-node install
(`roles/infra/run.sh` via `openg2p-single-node.sh`) and the multi-node production
install (`openg2p-prod`). The infra Helmfile creates the `observability` namespace
and deploys the OTel collectors, Loki, its MinIO, the Grafana Loki datasource,
the alert rules and the ready-made dashboard.

See the [Deployment documentation](https://docs.openg2p.org/operations/deployment)
for the overall install.

## Configuration

Settings are provided in `prod-config.yaml` (multi-node) or
`single-node-config.yaml` (sandbox) before install (all have sensible defaults).
The main ones:

| Key | Default | Purpose |
| --- | --- | --- |
| `loki_retention_hours` | `168` | Log retention (168h = 7 days) |
| `loki_minio_root_user` | `loki` | Loki object-store user |
| `loki_minio_root_password` | _(auto-generated)_ | Loki object-store password |
| `loki_minio_size` | `50Gi` | Disk for Loki's MinIO |
| `alert_smtp_*` | _(blank)_ | Email alert channel (host, from, user, password, to) |
| `alert_slack_webhook_url` | _(blank)_ | Slack / Mattermost / Rocket.Chat webhook |
| `alert_telegram_bot_token` / `_chat_id` | _(blank)_ | Telegram channel |
| `ai_enabled` | `false` | Optional AI layer (off by default) |

Alert channels are **inert until you fill in their credentials** — see the
[Operations Guide → Alerting](operations.md#alerting).

## Accessing Grafana

Grafana is reached through the **Rancher UI → cluster → Monitoring → Grafana**
(it is not exposed on its own hostname). You are signed in automatically via your
Rancher session as an **Editor** — no separate Grafana login. That link should
open Grafana Home directly.

> If Grafana shows **Page not found** on first load, click **Home** in the
> Grafana bar (or hard-refresh). Do **not** add `/k8s/clusters/local` to the
> URL — for this stack the Rancher proxy path is
> `…/api/v1/namespaces/cattle-monitoring-system/services/http:rancher-monitoring-grafana:80/proxy/`.

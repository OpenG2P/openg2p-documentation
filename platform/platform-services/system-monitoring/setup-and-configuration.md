# Setup & Configuration

> Concepts are in the [System Monitoring overview](README.md). This is a how-to.

## Installation

The monitoring stack is **installed automatically** as part of the production
deployment automation (the production `openg2p-prod` install) — no manual steps. The
infra Helmfile creates the `observability` namespace and deploys the OTel
collectors, Loki, its MinIO, the Grafana Loki datasource, the alert rules and the
ready-made dashboard.

See the [Deployment documentation](https://docs.openg2p.org/operations/deployment)
for the overall install.

## Configuration

Settings are provided in `prod-config.yaml` before install (all have sensible
defaults). The main ones:

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
Rancher session as an **Editor** — no separate Grafana login.

> If a bookmarked Grafana URL shows "page not found", make sure it includes the
> Rancher cluster prefix: `…/k8s/clusters/local/api/v1/namespaces/cattle-monitoring-system/services/http:rancher-monitoring-grafana:80/proxy/`.

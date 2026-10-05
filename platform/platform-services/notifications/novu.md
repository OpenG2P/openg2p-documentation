---
description: >-
  Default self-hosted Novu 3.19 from the commons chart, and how workflow
  copy and channels are seeded.
---

# Novu

Novu is the default `NOTIFICATION_PROVIDER`. Product services do not embed Novu. They call the [connector](connector.md). This page is the commons install and the workflow seed those services expect.

## Commons chart

The chart lives in [openg2p-commons-base values](https://github.com/OpenG2P/commons/blob/develop/charts/openg2p-commons-base/values.yaml) under `novu`. It is published from openg2p-deployment. Commons passes values and owns the overlays in `templates/novu` (secret, API-key Job, Istio).

`novu.enabled` defaults to `false` until a standalone Novu release is removed from the namespace. Under a release named `commons`, the API Service is `commons-novu-api` and the Secret is `commons-novu`.

| Piece | Value |
| --- | --- |
| API image | `ghcr.io/novuhq/novu/api:3.19.0` |
| Worker image | `ghcr.io/novuhq/novu/worker:3.19.0` |
| WebSocket image | `ghcr.io/novuhq/novu/ws:3.19.0` |
| Dashboard image | `ghcr.io/novuhq/novu/dashboard:3.19.0` |
| In-cluster API | `http://commons-novu-api:3000` |
| API port | 3000 |
| WebSocket port | 3002 |
| Dashboard port | 4000 |
| MongoDB | enabled by the subchart |
| Object storage | MinIO in the same release (`S3_LOCAL_STACK`) |

Public hostnames come from commons `global`:

| Value | Default shape |
| --- | --- |
| `novuApiHostname` | `novu-api.{baseDomain}` |
| `novuWsHostname` | `novu-ws.{baseDomain}` |
| `novuDashboardHostname` | `novu.{baseDomain}` |

The API container sets `API_ROOT_URL` and `FRONT_BASE_URL` from those hosts. Istio virtual services for the API, WebSocket, and dashboard are on the commons chart, not on the Novu subchart's own gateway (`novu.api.istio.enabled` and the worker and dashboard equivalents are false).

### Secret

The parent Secret is `{release}-novu` (`existingSecret`). The bootstrap Job writes key `api-key`. That value is what product services mount as `NOTIFICATION_PROVIDER_API_KEY`.

The same Secret holds `novu-secret-key` (`NOVU_SECRET_KEY`). Staff UI mounts that key as `NOTIFICATION_SECRET_KEY` for inbox HMAC. It is not the send key. Do not put `NOVU_SECRET_KEY` in `NOTIFICATION_PROVIDER_API_KEY`.

Bootstrap also has an admin email `admin@openg2p.org`. The password is empty in the chart values and must be set for the environment. `DISABLE_USER_REGISTRATION` defaults to false on the API container.

## What you still set in the dashboard

The chart does not create email or SMS providers, and it does not store the in-app application identifier.

* Add the email provider and the SMS provider the workflows use. In-app does not need an external provider.
* Copy the environment application identifier into `global.notificationApplicationIdentifier` so the staff UI can load the inbox. See [Inbox](inbox.md).
* For a production inbox, turn on HMAC for the in-app integration. Novu documents this in [Prepare for production](https://docs.novu.co/platform/inbox/prepare-for-production).

## Workflows

Workflows are the copy and the channel steps. Python sends a payload. It does not render a title or a body.

Seed them with `POST /v2/workflows` so the Novu 3.19 dashboard can open them. The older `POST /v1/notification-templates` API creates `novu-cloud-v1` workflows that the dashboard will not edit. The seeded origin must be `novu-cloud`.

Trigger ids cannot contain dots. The event key `change_request.created` becomes the trigger id `change-request-created`. The same replacement applies to underscores. `NOTIFICATION_WORKFLOWS` maps the dotted key to that trigger id. The map is also the allow-list: remove a key to stop that event.

Locale is fixed as `/en` inside the workflow URL. The staff UI origin is the payload field `staff_portal_base_url`, taken from `NOTIFICATION_STAFF_PORTAL_BASE_URL`. Do not put the host or the locale in the Python path fields.

| Audience | Channels | Buttons |
| --- | --- | --- |
| Registrant change request and intake | Email and SMS. No in-app step | None |
| Staff register export | In-app and email | Primary: Open register. URL `{staff_portal_base_url}/en/register/{register_mnemonic}` |
| AWE staff, except quorum skipped | In-app and email. No SMS | Primary: View task. Secondary: Show all tasks |
| AWE quorum skipped | In-app only | Same two buttons |

View task is `{staff_portal_base_url}/en{task_path}`. Show all tasks is `{staff_portal_base_url}/en{tasks_list_path}`. The paths already start with `/`. The event list and the fields each template reads are in [Workflows and payloads](workflows-and-payloads.md).

Cluster installs can also define workflows with `@novu/framework` and sync them through the commons Novu bridge Job. Prefer that catalog when you add a product. A one-off seed against a running API uses `POST /v2/workflows` and replaces a workflow that already has the same trigger id.

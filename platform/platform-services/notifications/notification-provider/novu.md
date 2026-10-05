---
description: >-
  Default self-hosted Novu 3.19 from the commons chart, workflow seeding,
  the trigger body the connector sends, and which workflows need email
  or SMS.
---

# Novu

Novu is the default notification provider (`NOTIFICATION_PROVIDER=novu` on the [connector](../connector.md), `provider: "novu"` on the [client](../client.md)). Product services do not embed Novu. They call the connector. This page is the commons install, the workflow seed those services expect, and which OpenG2P workflows need an email or SMS integration.

## Commons chart

The chart lives in [openg2p-commons-base values](https://github.com/OpenG2P/commons/blob/develop/charts/openg2p-commons-base/values.yaml) under `novu`. It is published from openg2p-deployment. Commons passes values and owns the overlays in `templates/novu` (secret, API-key Job, workflow Job, Istio).

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

* Add the email provider and the SMS provider the workflows use. Which workflows need which channel, and Novu's own setup guides, are in [Email and SMS](#email-and-sms).
* Copy the environment application identifier into `global.notificationApplicationIdentifier` so the staff UI can load the inbox. See [Client](../client.md).
* For a production inbox, turn on HMAC for the in-app integration. Novu documents this in [Prepare for production](https://docs.novu.co/platform/inbox/prepare-for-production).

## Email and SMS

The commons chart seeds workflow steps that already say email or SMS. It does not create the integrations those steps deliver through. Add them in the Novu dashboard. Novu documents the provider list and the dashboard steps. The table records which OpenG2P workflows depend on them.

| Channel | Novu guide | OpenG2P workflows that use it |
| --- | --- | --- |
| Email | [Email integrations](https://docs.novu.co/platform/integrations/email), [Add an email provider](https://docs.novu.co/platform/integrations/email/adding-email) | Registrant change request and intake. Staff export. AWE staff events except quorum skipped |
| SMS | [SMS integrations](https://docs.novu.co/platform/integrations/sms), [Add an SMS provider](https://docs.novu.co/platform/integrations/sms/adding-sms) | Registrant change request and intake |
| In-app | No external provider. See [Prepare for production](https://docs.novu.co/platform/inbox/prepare-for-production) for HMAC | Staff export and AWE. The bell is the [client](../client.md) |

How Novu picks the primary integration, stores credentials, and scopes them to an environment is in [Integrations](https://docs.novu.co/platform/concepts/integrations).

The registry staff UI does not collect these credentials. It only opens the in-app inbox. See [Client](../client.md#staff-ui).

## Workflows

Workflows are the copy and the channel steps. Python sends a payload. It does not render a title or a body.

Seed them with `POST /v2/workflows` so the Novu 3.19 dashboard can open them. The older `POST /v1/notification-templates` API creates `novu-cloud-v1` workflows that the dashboard will not edit. The seeded origin must be `novu-cloud`. The commons chart does this from `files/novu/workflow.json` in the workflow Job.

Trigger ids cannot contain dots. The event key `change_request.created` becomes the trigger id `change-request-created`. The same replacement applies to underscores. `NOTIFICATION_WORKFLOWS` maps the dotted key to that trigger id. The map is also the allow-list: remove a key to stop that event.

Locale is fixed as `/en` inside the workflow URL. The staff UI origin is the payload field `staff_portal_base_url`, taken from `NOTIFICATION_STAFF_PORTAL_BASE_URL`. Do not put the host or the locale in the Python path fields.

| Audience | Channels | Buttons |
| --- | --- | --- |
| Registrant change request and intake | Email and SMS. No in-app step | None |
| Staff register export | In-app and email | Primary: Open register. URL `{staff_portal_base_url}/en/register/{register_mnemonic}` |
| AWE staff, except quorum skipped | In-app and email. No SMS | Primary: View task. Secondary: Show all tasks |
| AWE quorum skipped | In-app only | Same two buttons |

View task is `{staff_portal_base_url}/en{task_path}`. Show all tasks is `{staff_portal_base_url}/en{tasks_list_path}`. The paths already start with `/`. The event list and the fields each template reads are in [Workflows and payloads](../workflows-and-payloads.md).

Cluster installs can also define workflows with `@novu/framework` and sync them through the commons Novu bridge Job. Prefer that catalog when you add a product. A one-off seed against a running API uses `POST /v2/workflows` and replaces a workflow that already has the same trigger id.

## What the connector sends

The Novu provider maps `Recipient` onto the trigger body: `subscriber_id`, and `email`, `phone`, and `first_name` when those fields are set. Source: [`novu.py`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/providers/novu.py).

`send` builds one trigger. `send_bulk` sends `{ "events": [ ... ] }` and refuses more than 100 events.

```json
{
  "workflow_id": "change-request-created",
  "transaction_id": "change_request.created:cr-1:person:p-1",
  "to": {
    "subscriber_id": "person:p-1",
    "email": "ada@example.com",
    "phone": "+10000000000",
    "first_name": "Ada"
  },
  "payload": {
    "record_name": "Ada"
  }
}
```

`email`, `phone`, and `first_name` are omitted when the recipient does not set them. `transaction_id` is omitted when the notification id is empty. Novu treats `transaction_id` as the idempotency key for that trigger. Reuse it and Novu will not start a second run of the same workflow for the same id.

`first_name` is the whole `recipient_name`. The connector does not split a name into first and last.

A skipped send (disabled, or event not in the map) returns status `SUCCESS` with response `skipped`. A Novu result whose status is not `processed` returns `FAILURE`. An empty API key raises `ValueError` before the HTTP call. A missing `recipient_id` or `workflow_id` also raises. Host apps should catch that. Registry and AWE do.

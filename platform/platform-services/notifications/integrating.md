---
description: >-
  How a new application sends a notification from its backend and shows
  the inbox in its UI. Both sides use the same subscriber id.
---

# Integrating a new service


A new application uses both libraries in [OpenG2P/notifications](https://github.com/OpenG2P/notifications). The backend sends. The UI shows the inbox. They do not import each other.

The subscriber id must be the same on both sides. Staff is the Keycloak username (`preferred_username`). A registrant is `person:{internal_record_id}`. See [Identity](architecture.md#identity).

| Side | Library | What it does |
| --- | --- | --- |
| Backend | [`connector/`](https://github.com/OpenG2P/notifications/tree/develop/connector) | Sends an event after the business change commits |
| UI | [`client/`](https://github.com/OpenG2P/notifications/tree/develop/client) | Renders `Inbox` and reads that subscriber's inbox |

Novu install, workflow copy, and email or SMS credentials are in [Novu](notification-provider/novu.md). This page does not repeat them.

## Steps at a glance

Do these in order. Each step names the section that covers it.

| # | Step | Where |
| --- | --- | --- |
| 1 | Pick the event keys and the recipient for each | [Plan the events](#plan-the-events) |
| 2 | Create one workflow per event on the notification provider | [Novu](notification-provider/novu.md#workflows) |
| 3 | Install the connector and map each event key in `NOTIFICATION_WORKFLOWS` | [Backend](#backend) |
| 4 | Call `send` after the business change commits | [Backend](#backend) |
| 5 | Install the client and build the session on the UI server | [User interface](#user-interface) |
| 6 | Render `Inbox` with the same subscriber id | [User interface](#user-interface) |
| 7 | Check that one event reaches the bell | [Verify](#verify) |

## Plan the events

Decide these before you write code:

| Decision | Rule |
| --- | --- |
| Event key | Dotted and lowercase, for example `grievance.assigned`. One key per business moment |
| Recipient | Staff (`preferred_username`) or registrant (`registrant_id(internal_record_id)`). One person per `Recipient`. Use `send_bulk` for many people |
| Channels | Set on the notification provider workflow, not in Python. In-app needs no external provider. Email and SMS need an integration on the provider |
| Payload | Every field the template reads as `{{payload.*}}`. Add ids for links and friendly names for the copy. Send a missing value as empty, not as an absent key |

The existing Registry and AWE events are in [Workflows and payloads](workflows-and-payloads.md). Reuse their field names where the meaning is the same.

## Backend

Install the connector in the service that owns the business change:

```bash
pip install openg2p-notification
```

Images that build from source install it from git. See [Install](connector.md#install).

Set these on the service. The full list and defaults are in [Connector](connector.md#environment).

| Variable | Notes |
| --- | --- |
| `NOTIFICATION_ENABLED` | `false` skips every send |
| `NOTIFICATION_PROVIDER` | `novu` by default |
| `NOTIFICATION_PROVIDER_URL` | In-cluster API URL of the notification provider |
| `NOTIFICATION_PROVIDER_API_KEY` | Secret. Stays on the server |
| `NOTIFICATION_WORKFLOWS` | JSON map of event key to workflow id. An event that is not listed is not sent |

For example:

```bash
NOTIFICATION_WORKFLOWS={"grievance.assigned":"grievance-assigned"}
```

After the business change commits, call `send` with the event key, the entity id, the payload, and a `Recipient`:

```python
import asyncio
import logging

from openg2p_notification import NotificationFactory, Recipient

_logger = logging.getLogger(__name__)

await session.commit()

try:
    await asyncio.to_thread(
        NotificationFactory.get_notifier().send,
        "grievance.assigned",
        grievance_id,
        {"grievance_id": grievance_id, "title": title},
        Recipient(recipient_id=assignee_username, recipient_email=assignee_email),
    )
except Exception:
    _logger.exception("notification send failed for grievance %s", grievance_id)
```

* Do not pass a channel.
* Send after the commit, so a rolled-back change does not notify.
* Log a failed send. Do not fail the business request.
* If the package may be missing in some images, import it inside a `try` and skip the send on `ImportError`, as Registry and AWE do.

`recipient_id` on that `Recipient` is the subscriber id the UI will open. The rules for async code, bulk sends, and notification ids are in [Implementing a send](implementing.md).

## User interface

Install the client in the UI app:

```bash
npm install https://github.com/OpenG2P/notifications/raw/refs/heads/develop/client/openg2p-notification-0.1.0.tgz
```

The React page renders `Inbox`. The server builds the session. Props and packaging are in [Client](client.md).

Give the UI server these settings. The names below are the ones the registry staff UI uses. Another app can use its own names, as long as the values reach `Inbox`.

| Setting | Public to the browser | Meaning |
| --- | --- | --- |
| `NOTIFICATION_PROVIDER` | Yes | Client adapter name. `novu` by default |
| `NOTIFICATION_APPLICATION_IDENTIFIER` | Yes | Application identifier from the notification provider environment |
| `NOTIFICATION_BACKEND_URL` | Yes | Public API URL of the notification provider |
| `NOTIFICATION_WEBSOCKET_URL` | Yes | Public WebSocket URL of the notification provider |
| `NOTIFICATION_SECRET_KEY` | **No** | Server-only HMAC secret |

On the server, after login:

1. Read `preferred_username` from the access token. That is `subscriberId`. For a registrant portal, use `person:{internal_record_id}` instead.
2. When `NOTIFICATION_SECRET_KEY` is set, compute `HMAC-SHA256` of that id as hex. That is `subscriberHash`.
3. Pass the public values with it: `NOTIFICATION_PROVIDER`, `NOTIFICATION_APPLICATION_IDENTIFIER`, `NOTIFICATION_BACKEND_URL`, and `NOTIFICATION_WEBSOCKET_URL`.

```ts
import { createHmac } from "crypto";

export function subscriberHash(subscriberId: string, secret: string): string {
  return createHmac("sha256", secret).update(subscriberId).digest("hex");
}
```

Then render the inbox in a client component. Do not render it until `provider`, `applicationIdentifier`, and `subscriberId` are set. The full component, the theme, and the localization props are in [Render the inbox](client.md#render-the-inbox).

The browser then talks to the notification provider for the list and the live socket. The UI server does not proxy those calls.

The registry staff UI is one example of this split: [`getNotificationHmac`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/app/api/_lib/notification-hmac.ts) on the server, [`NotificationInbox`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/components/layout/NotificationInbox.tsx) in the page.

## Common mistakes

| Mistake | Effect | Fix |
| --- | --- | --- |
| Different subscriber id on the backend and in the UI (for example an email, or a Keycloak `sub`) | The send succeeds. The bell stays empty | Use `preferred_username` for staff and `person:{id}` for registrants on both sides |
| `NOTIFICATION_SECRET_KEY` sent to the browser | Anyone can forge a `subscriberHash` and read another inbox | Keep it on the server. Send only the hash |
| `NOTIFICATION_SECRET_KEY` used as `NOTIFICATION_PROVIDER_API_KEY`, or the reverse | Sends fail, or the inbox is rejected | They are two different secrets. See [Secret](notification-provider/novu.md#secret) |
| In-cluster URL (`http://commons-novu-api:3000`) passed as `backendUrl` | The browser cannot reach it | Use the public `https://` API and WebSocket hosts |
| Event key missing from `NOTIFICATION_WORKFLOWS` | The connector returns `skipped` and nothing is sent | Add the key. See [Connector](connector.md#environment) |
| Workflow id with a dot | The provider cannot find the workflow | Replace `.` and `_` with `-`, for example `grievance-assigned` |
| Payload field the template reads is not sent | The copy renders with a blank | Send every field the template uses, empty if there is no value |
| Link in the payload with no host | The button opens a broken URL | Put the public UI origin in the payload, as `staff_portal_base_url` does for Registry and AWE. See [Deployment](deployment.md) |

## Verify

1. Set `NOTIFICATION_ENABLED=true` and map one event.
2. Trigger the business action as a user whose inbox you can open.
3. Check the service log for `Sending event ... workflow ... to recipient_id=...`. A line that says `Skipping event` means the switch is off or the key is not mapped.
4. Open the UI as that user. The bell shows the unread count, and the new notification arrives without a reload.
5. For email and SMS, check the delivery log in the notification provider dashboard.

If one event stays silent, walk the checklist in [When a send does not happen](architecture.md#when-a-send-does-not-happen).

## Next

* Add Helm values and secrets for your chart: [Deployment](deployment.md).
* Replace the notification provider: [Switch provider](connector.md#switch-provider) for the backend and [Switch provider](client.md#switch-provider) for the UI.

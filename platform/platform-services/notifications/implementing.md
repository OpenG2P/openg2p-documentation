---
description: >-
  How a product service sends. After commit, with an allow-listed event
  key, a payload, and a recipient.
---

# Implementing a send

The [connector](connector.md) is the only send API. This page is how a service uses it. The events Registry and AWE already send are listed in [Workflows and payloads](workflows-and-payloads.md).

## Rules

1. Commit the business change first. A rolled-back request must not notify.
2. Put the event key in `NOTIFICATION_WORKFLOWS`. A key that is not in the map is skipped.
3. Pass `event`, `entity_id`, `payload`, and a `Recipient`. Do not pass a channel.
4. Call `send` or `send_bulk` from a thread if you are in an async service (`asyncio.to_thread`).
5. Log failures. Do not fail the business request because the notification provider is down or the package is missing.
6. Keep `send_bulk` at 100 events or fewer. Split a longer list.

Staff `recipient_id` is the Keycloak username (`preferred_username`). Registrant `recipient_id` is `registrant_id(internal_record_id)`, which returns `person:{id}`.

`notification_id` defaults to `{event}:{entity_id}`. Pass your own when one entity must produce more than one notification, for example one per recipient. Registry uses `{event}:{entity_id}:{recipient_id}`. AWE uses `{event}:{request_id}:{ref}:{recipient_id}`.

## Minimal call

```python
import asyncio

from openg2p_notification import NotificationFactory, Recipient, registrant_id

await asyncio.to_thread(
    NotificationFactory.get_notifier().send,
    "change_request.created",
    change_request_id,
    {"record_name": record_name, "change_request_id": change_request_id},
    Recipient(
        recipient_id=registrant_id(internal_record_id),
        recipient_email=email,
        recipient_phone=phone,
        recipient_name=name,
    ),
)
```

Wrap that call in `try` / `except`. If `openg2p_notification` cannot be imported, skip the send.

## Registry pattern

Registry does not call `send` at each business method. [`NotificationHelper`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/helpers/notification.py) builds the payload, resolves the recipient, and sends after commit.

| Helper | Recipient |
| --- | --- |
| `dispatch_change_request_notification` | Registrant, via `resolve_contact` on the register domain service |
| `dispatch_intake_form_notification` | Registrant. If the domain service has no channel, intake falls back to contact fields on the submission sections |
| `dispatch_register_export_notification` | Staff username in `requested_by` |

`dispatch_notification_registrant` returns without sending when the contact is missing or `has_channel()` is false (no email and no phone). `dispatch_notification_staff` uses `preferred_username` as `recipient_id`.

A failed lookup of register, section, or record display is logged and leaves those payload fields empty. The send still goes out.

## AWE pattern

AWE must not notify for a transaction that later rolls back, and it must not do HTTP inside the engine transaction.

| Function | When |
| --- | --- |
| `collect()` | Inside the transaction, from `emit_event()`. Stashes intents on `session.info`. No HTTP. Never raises |
| `flush()` | After commit. One Keycloak lookup per username, then `send_bulk` per event. Failures are logged |
| `discard()` | After rollback. Drops the intents |

`collect()` ignores engine events that are not in its map: `request_created` (a `stage_started` follows), `stage_skipped`, a plain `stage_completed`, and observers. It also returns immediately when the event is not in `NOTIFICATION_WORKFLOWS`.

Source: [`awe/src/awe/services/notification.py`](https://github.com/OpenG2P/awe/blob/develop/src/awe/services/notification.py).

## Add an event

1. Choose a dotted event key. On the default notification provider the workflow id is that key with `.` and `_` replaced by `-`.
2. Add the workflow on the notification provider (channels, copy, `{{payload.*}}`). See [Novu](notification-provider/novu.md).
3. Add the key to `NOTIFICATION_WORKFLOWS` on the deployment that should send it.
4. After commit, call `send` with a payload that includes every field the template reads.

Removing the key from `NOTIFICATION_WORKFLOWS` turns the event off without a code change.

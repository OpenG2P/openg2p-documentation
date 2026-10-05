---
description: >-
  The openg2p-notification Python package. send and send_bulk, environment
  variables, and how to replace the Novu provider.
---

# Connector

[`openg2p-notification`](https://github.com/OpenG2P/notifications/tree/develop/connector) is a library, not an HTTP service. Registry and AWE import it and call `send` or `send_bulk` in process.

The package does not talk to the staff inbox. Session, list, and mark-read stay in the [staff UI](inbox.md).

## Install

```bash
pip install openg2p-notification
```

From the notifications repository:

```bash
pip install -e connector/
```

Images install it from git. The subdirectory is `connector`:

```text
git+https://github.com/openg2p/notifications@develop#subdirectory=connector
```

`pip install` only puts the library on the path. The process still needs the environment variables below, and a host app constructs the initializer once at startup:

```python
from openg2p_notification.app import Initializer as NotificationInitializer

NotificationInitializer()
```

You can skip that call. `NotificationFactory.get_notifier()` builds the provider from settings on first use.

If the import fails, Registry and AWE skip every send. A missing package does not fail the business request.

## Environment

Settings use the prefix `NOTIFICATION_`. Source: [`config.py`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/config.py).

| Variable | Default | Meaning |
| --- | --- | --- |
| `NOTIFICATION_ENABLED` | `true` | Master switch. `false` skips every send |
| `NOTIFICATION_PROVIDER` | `novu` | Provider module name under `providers/` |
| `NOTIFICATION_PROVIDER_URL` | `http://localhost:3000` | Provider API base URL |
| `NOTIFICATION_PROVIDER_API_KEY` | empty | Secret key. For Novu this is the API secret, not `NOVU_SECRET_KEY` |
| `NOTIFICATION_PROVIDER_TIMEOUT_MS` | `20000` | HTTP timeout |
| `NOTIFICATION_WORKFLOWS` | `{}` | JSON map of event key to provider workflow id. `{}` sends nothing |

`NOTIFICATION_STAFF_PORTAL_BASE_URL` is not a connector setting. Registry and AWE read it themselves and put the value in the payload. See [Deployment](deployment.md).

Create the workflow in the provider first. Then list only the events this environment should send:

```bash
NOTIFICATION_WORKFLOWS={"change_request.created":"change-request-created"}
```

The catalog of event keys lives in the host app, not in this package. A missing key, a blank mapped value, or an empty map means that event is not sent. Novu workflow ids cannot contain dots, so `change_request.created` maps to `change-request-created`.

## Send

```python
from openg2p_notification import NotificationFactory, Recipient, registrant_id

NotificationFactory.get_notifier().send(
    event="change_request.created",
    entity_id=cr_id,
    payload={"change_request_id": cr_id, "record_name": record_name},
    recipient=Recipient(
        recipient_id=registrant_id(internal_record_id),
        recipient_email=person_email,
        recipient_phone=person_phone,
        recipient_name=person_name,
    ),
)
```

| Argument | Meaning |
| --- | --- |
| `event` | Dotted event key. Looked up in `NOTIFICATION_WORKFLOWS` |
| `entity_id` | Stable id of the business row. Used in the notification id |
| `payload` | Dict the workflow template reads as `{{payload.*}}` |
| `recipient` | `recipient_id` is required. Email, phone, and name are channel addresses |
| `notification_id` | Optional. Default is `{event}:{entity_id}`. Novu stores this as `transaction_id` |

From an async service, call `await asyncio.to_thread(...)`. Call it after commit. Catch and log. A failed send must not fail the business request.

`ids(event, entity_id)` returns `(workflow_id, notification_id)`. `workflow_id` is `None` when the event is not in the allow-list. `workflow_enabled(event)` is true only when notifications are on and the event is mapped.

`send()` already calls `ids()`. Host apps normally pass `event` and `entity_id` only.

Bulk accepts at most 100 requests. A larger list raises `ValueError`. Split the list, as AWE does.

```python
from openg2p_notification import NotificationRequest

notifier.send_bulk(
    [
        NotificationRequest(
            event="change_request.created",
            entity_id="1",
            recipient=Recipient(
                recipient_id="person:rec-1",
                recipient_email="ada@example.com",
            ),
            payload={"change_request_id": "1"},
        ),
    ]
)
```

The Novu provider maps `Recipient` onto the trigger body: `subscriber_id`, and `email`, `phone`, and `first_name` when those fields are set. Source: [`novu.py`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/providers/novu.py) and [`interface.py`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/core/interface.py).

A skipped send (disabled, or event not in the map) returns status `SUCCESS` with response `skipped`. A Novu result whose status is not `processed` returns `FAILURE`. An empty API key raises `ValueError` before the HTTP call. A missing `recipient_id` or `workflow_id` also raises. Host apps should catch that. Registry and AWE do.

### What Novu receives

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

### Allow-list helpers

| Function | Returns |
| --- | --- |
| `resolve_workflow_id(event)` | Mapped workflow id, or `None` |
| `workflow_enabled(event)` | `False` when disabled, when the event is blank, or when the key is not mapped |
| `notification_id(event, entity_id)` | `{event}:{entity_id}` |
| `ids(event, entity_id, nid=None)` | `(workflow_id, notification_id)`. A passed `nid` replaces the default id |
| `registrant_id(internal_record_id)` | `person:{internal_record_id}` |

`workflow_enabled` is the check host apps should make before they do expensive payload work. AWE `collect()` does this. Registry `NotificationHelper._send` does this after the payload is built.

## Switch provider

Host apps do not import Novu. [`NotificationFactory`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/core/factory.py) loads `openg2p_notification.providers.{NOTIFICATION_PROVIDER}`. That module must call `NotificationFactory.register(name, cls)` at import. The Novu module registers `"novu"`.

To leave Novu:

1. Implement `NotificationInterface.send` and `send_bulk`. Call `ids(event, entity_id)` for the workflow id and the notification id.
2. Register the class under a short name (`^[a-z][a-z0-9_]*$`).
3. Set `NOTIFICATION_PROVIDER` to that name.
4. Point `NOTIFICATION_PROVIDER_URL` and `NOTIFICATION_PROVIDER_API_KEY` at the new system.

Registry and AWE call sites stay the same. They still pass an event key, an entity id, a payload, and a `Recipient`.

A provider that lives outside this package can register before the first `get_notifier()`:

```python
from openg2p_notification.core.factory import NotificationFactory
from openg2p_notification.core.interface import NotificationInterface
from openg2p_notification.core.models import NotificationResponse, Recipient
from openg2p_notification.utils.events import ids


class AcmeNotifier(NotificationInterface):
    def send(self, event, entity_id, payload, recipient: Recipient, notification_id=None) -> NotificationResponse:
        workflow_id, nid = ids(event, entity_id, notification_id)
        ...


NotificationFactory.register("acme", AcmeNotifier)
```

Then set `NOTIFICATION_PROVIDER=acme`. If the name is not registered and `openg2p_notification.providers.acme` cannot be imported, `get_notifier()` raises `ValueError`.

A provider module inside the package registers itself on import. Put the class in `src/openg2p_notification/providers/acme.py` and end the module with `NotificationFactory.register("acme", AcmeNotifier)`. The factory imports `openg2p_notification.providers.acme` when `NOTIFICATION_PROVIDER=acme` and the name is not registered yet.

Implement `send_bulk` yourself when the new system has a bulk API. The interface default loops and calls `send` once per item. That default is correct. It is slower, and it does not share the Novu limit of 100. If you keep the default, still document the limit your API enforces and split in the host app.

The provider must keep the same skip rules the Novu class uses, or host apps will notify when the allow-list says not to:

* `NOTIFICATION_ENABLED=false` returns `skipped` and does not call the remote API.
* `ids()` returns `workflow_id is None` when the event is not mapped. Return `skipped` for that item. In a bulk call, skip that item and still send the others.
* Do not read channel flags from the host. The workflow id selects the template. The template selects channels.

Registry and AWE never import the provider class. They call `NotificationFactory.get_notifier()`. A Helm change of `global.notificationProvider` is enough after the image contains the new module. See [Deployment](deployment.md).

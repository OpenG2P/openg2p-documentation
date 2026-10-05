---
description: >-
  The openg2p-notification Python package. send and send_bulk, environment
  variables, and how to replace the provider.
---

# Connector

[`openg2p-notification`](https://github.com/OpenG2P/notifications/tree/develop/connector) is a library, not an HTTP service. Registry and AWE import it and call `send` or `send_bulk` in process. The call is the same for every notification provider.

The package does not talk to the inbox. Session, list, and mark-read stay in the [client](client.md). The default notification provider's trigger body, workflow ids, and dashboard are in [Novu](notification-provider/novu.md).

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
| `NOTIFICATION_PROVIDER_API_KEY` | empty | Secret key for the provider API. On Novu this is the API secret, not `NOVU_SECRET_KEY` |
| `NOTIFICATION_PROVIDER_TIMEOUT_MS` | `20000` | HTTP timeout |
| `NOTIFICATION_WORKFLOWS` | `{}` | JSON map of event key to provider workflow id. `{}` sends nothing |

`NOTIFICATION_STAFF_PORTAL_BASE_URL` is not a connector setting. Registry and AWE read it themselves and put the value in the payload. See [Deployment](deployment.md).

Create the workflow in the notification provider first. Then list only the events this environment should send:

```bash
NOTIFICATION_WORKFLOWS={"change_request.created":"change-request-created"}
```

The catalog of event keys lives in the host app, not in this package. A missing key, a blank mapped value, or an empty map means that event is not sent. On the default notification provider, workflow ids cannot contain dots, so `change_request.created` maps to `change-request-created`. See [Workflows](notification-provider/novu.md#workflows).

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
| `notification_id` | Optional. Default is `{event}:{entity_id}`. The default notification provider stores this as `transaction_id` |

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

`Recipient` is provider-neutral: `recipient_id` plus optional email, phone, and name. The built-in `novu` module maps those fields onto the trigger body. That JSON, and how Novu treats `transaction_id`, is in [What the connector sends](notification-provider/novu.md#what-the-connector-sends). Source of the shared types: [`interface.py`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/core/interface.py).

A skipped send (disabled, or event not in the map) returns status `SUCCESS` with response `skipped`. An empty API key raises `ValueError` before the HTTP call. A missing `recipient_id` or `workflow_id` also raises. Host apps should catch that. Registry and AWE do. A provider-specific failure status is documented with that provider.

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

Host apps do not import a provider SDK. [`NotificationFactory`](https://github.com/OpenG2P/notifications/blob/develop/connector/src/openg2p_notification/core/factory.py) loads `openg2p_notification.providers.{NOTIFICATION_PROVIDER}`. That module must call `NotificationFactory.register(name, cls)` at import. The built-in module registers `"novu"`.

To leave the default provider:

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

Implement `send_bulk` yourself when the new system has a bulk API. The interface default loops and calls `send` once per item. That default is correct. It is slower, and it does not share the built-in limit of 100. If you keep the default, still document the limit your API enforces and split in the host app.

The provider must keep the same skip rules the built-in class uses, or host apps will notify when the allow-list says not to:

* `NOTIFICATION_ENABLED=false` returns `skipped` and does not call the remote API.
* `ids()` returns `workflow_id is None` when the event is not mapped. Return `skipped` for that item. In a bulk call, skip that item and still send the others.
* Do not read channel flags from the host. The workflow id selects the template. The template selects channels.

Registry and AWE never import the provider class. They call `NotificationFactory.get_notifier()`. A Helm change of `global.notificationProvider` is enough after the image contains the new module. See [Deployment](deployment.md).

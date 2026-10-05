---
description: >-
  Who sends, who delivers, and which identifier the notification provider uses
  for a staff member and for a registrant.
---

# Architecture

A product service defines what happened. The [connector](connector.md) triggers a notification provider workflow. The notification provider decides the channel, the copy, and the inbox. The [client](client.md) reads that inbox. It does not send.

Novu is the default notification provider. Its install is in [Novu](notification-provider/novu.md). This page is the hop and the identity rules every notification provider has to keep.

## Hops

```mermaid
flowchart TB
  subgraph backend["OpenG2P Product Services"]
    Services["Registry / AWE / Other Services"]
  end

  Connector["OpenG2P Notification Connector"]

  subgraph provider["Novu — Notification Provider"]
    Workflows["Notification Workflows"]
    Channels["Channel Orchestration"]
    Inbox["In-App Inbox"]
    Email["Email"]
    SMS["SMS"]
  end

  subgraph frontend["OpenG2P User Interfaces"]
    Client["OpenG2P Client Package"]
    UI["Staff UI / Other Portals"]
  end

  Services -->|"Business events"| Connector
  Connector -->|"Notification events"| Workflows
  Workflows --> Channels
  Workflows --> Inbox
  Channels --> Email
  Channels --> SMS
  UI --> Client
  Client -->|"Consume inbox state"| Inbox
```

| Hop | What moves |
| --- | --- |
| Product service to connector | Event key, entity id, payload, recipient. In process. No HTTP from the product code itself |
| Connector to notification provider | Secret API key on trigger or bulk trigger. The trigger `to` object carries the subscriber id and any email, phone, and name |
| Client to notification provider | Public application identifier, subscriber id, inbox REST, and the WebSocket |

Python does not list the inbox, mark a notification read, or open a WebSocket. It also does not pass `channel=` on send. Channel steps live on the notification provider workflow.

## Send after commit

```mermaid
sequenceDiagram
  participant App as Product service
  participant DB as Database
  participant Connector as Connector
  participant Provider as Notification provider
  App->>DB: commit business change
  App->>Connector: send or send_bulk
  Connector->>Provider: trigger workflow
  Note over App: a failed send is logged and does not roll back the business change
```

AWE collects intents inside the transaction and sends them only in `flush()`, after commit. `discard()` drops them if the transaction rolls back. Registry helpers run after `session.commit()`. See [Implementing a send](implementing.md).

### Registry

```mermaid
sequenceDiagram
  participant API as Staff API or Celery
  participant DB as Database
  participant Helper as NotificationHelper
  participant Domain as Domain service
  participant Provider as Notification provider
  API->>DB: commit
  API->>Helper: dispatch after commit
  Helper->>Domain: resolve_contact
  Helper->>Provider: send
```

The helper builds the payload first. Display lookups that fail leave fields empty and still send. A registrant with no email and no phone does not send. Staff export sends to `requested_by` and does not call `resolve_contact`.

### AWE

```mermaid
sequenceDiagram
  participant Engine as Approval engine
  participant DB as Database
  participant Note as notification service
  participant KC as Keycloak
  participant Provider as Notification provider
  Engine->>Note: collect inside the transaction
  Engine->>DB: commit
  Engine->>Note: flush
  Note->>KC: email and name by username
  Note->>Provider: send_bulk
```

`collect()` does not call the notification provider. A Keycloak miss still sends. The in-app step can land without an email address.

## When a send does not happen

Check these in order. The business action still succeeds in every row.

| Check | Result |
| --- | --- |
| `openg2p-notification` is not installed | Registry and AWE return before any HTTP call |
| `NOTIFICATION_ENABLED` is false | Connector returns `skipped` |
| Event key is missing or blank in `NOTIFICATION_WORKFLOWS` | Connector returns `skipped` |
| Registrant contact is missing, or has no email and no phone | Registry returns before `send` |
| Export row has no `requested_by` | Registry returns before `send` |
| AWE engine event is not in the notify map | `collect()` stores nothing |
| AWE requester id equals `source_service` | Terminal events have no recipient |
| AWE webhook was already applied | Registry returns before the notify helpers |
| Notification provider rejects the trigger | Logged `FAILURE` or an exception. The row stays committed |

The connector does not retry. The notification provider retries its own channel steps after it accepts the trigger.

## Identity

| Person | Subscriber id | Email and name |
| --- | --- | --- |
| Staff | Keycloak username (`preferred_username`) | AWE looks the user up in Keycloak at flush time. A missing profile still sends, so the in-app step can land |
| Registrant | `person:{internal_record_id}` from `registrant_id()` | Email and phone come from the register domain service. No email and no phone skips the send |

Do not use an email address as the subscriber id. The same username on a later login is the same staff inbox. The [client](client.md) must pass that same id when it opens the inbox.

Registry export uses `requested_by` as that staff username. Change-request and intake-form events go to the registrant, not to the staff member who created the record.

## Responsibilities

| Responsibility | Owner |
| --- | --- |
| Business event and payload | Registry or AWE |
| Allow-list (`NOTIFICATION_WORKFLOWS`) | Deployment configuration |
| Trigger call | Same product service, through the connector |
| Workflow, template, channel, retry, inbox state | Notification provider |
| Email and SMS credentials | Channel integrations on the notification provider. See [Email and SMS](notification-provider/novu.md#email-and-sms) |
| Inbox list, unread count, mark read, live bell | Client, mounted by the staff UI |

Replacing the notification provider does not change Registry or AWE call sites. Only the implementation behind the connector, and the adapter behind the client, change. See [Switch provider](connector.md#switch-provider).

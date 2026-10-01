# Notification Architecture

OpenG2P applications emit business events. A **notification layer** handles orchestration and delivery — templates, workflows, channels, retries, and the in-app Inbox. Applications never call a notification-layer API directly.

`openg2p-notification-connector` is a single library, not a standalone HTTP service. Backend and UI live as **two folders in the same repo**:

| Folder | Layer | Role |
| --- | --- | --- |
| `notification-backend-lib` | Backend | Event trigger (`send`) from product services, using the notification-layer secret key |
| `notification-ui-lib` | UI | Inbox UI, notification-layer REST APIs, and the WebSocket connection to the notification layer |

> OpenG2P applications define **what** happened. The connector provides a stable backend and UI contract. The notification layer decides **how, when, and on which channel** the notification is delivered.

***

## 1. Notification Layer as the Orchestration Layer

Instead of implementing notification infrastructure separately within each OpenG2P application, a **notification layer acts as the notification orchestration and infrastructure layer**.

Without a dedicated layer, each application would need to implement and maintain:

* Notification templates
* Notification workflows
* Multi-channel orchestration
* Channel integrations
* Notification preferences
* Scheduling and delays
* Retry and failure handling
* Fallback logic
* Delivery status and tracking
* In-app notification / Inbox management

With a notification layer in place, OpenG2P applications focus on generating the relevant business events, while the layer handles notification orchestration and delivery.

#### High-Level Architecture

```mermaid
flowchart TB
    Backend["OpenG2P Backend Service"]
    UI["OpenG2P UI"]

    subgraph Connector["openg2p-notification-connector"]
        BackendLib["notification-backend-lib/"]
        UILib["notification-ui-lib/"]
    end

    Layer["Notification Layer"]

    Backend -->|"business event"| BackendLib
    BackendLib -->|"send"| Layer

    UI --> UILib
    UILib -->|"REST + WebSocket"| Layer

    Layer --> Email
    Layer --> SMS
    Layer --> Push
    Layer --> InApp["In-app Inbox"]
```

OpenG2P Backend Service and OpenG2P UI do not need to know which underlying email, SMS, or push channel is being used, nor which notification layer sits behind the connector.

***

## 2. Notification Abstraction Layer

OpenG2P defines a **stable notification contract** so that applications do not directly depend on any specific notification layer.

The abstraction exists at **both** the backend and UI layers.

```mermaid
flowchart TB
    Contract["OpenG2P Notification Contract"]

    Contract --> BackendIface["Backend Interface"]
    Contract --> UIIface["UI Interface"]

    BackendIface --> BackendLib["notification-backend-lib"]
    UIIface --> UILib["notification-ui-lib"]

    BackendLib --> BackendLayer["Notification Layer"]
    UILib --> UILayer["Notification Layer"]
```

The notification-layer implementation can later be replaced without requiring changes to application business logic or UI code.

***

## 3. Backend — Event Trigger

OpenG2P Backend services (for example Registry, PBMS, IAM, AWE) trigger notification events. That logic lives in `openg2p-notification-connector/notification-backend-lib`.

There is **no standalone notification HTTP service**. The product service that owns the business event imports the backend lib and calls `send()` in-process.

The application should not directly call any notification-layer API.

```mermaid
flowchart TB
    Apps["OpenG2P Backend service<br/>(Registry, PBMS, IAM, AWE, …)"]
    Lib["notification-backend-lib"]
    Adapter["Notification Layer Adapter"]
    Layer["Notification Layer"]

    Apps -->|"in-process send()"| Lib --> Adapter --> Layer
```

The secret API key stays in the product backend. Channel selection (in-app, email, SMS, push) is a workflow step in the notification layer, not a `channel=` argument on `send()`.

If that subscriber's browser is connected, the notification layer pushes on **their** socket. The product service does not forward the event over a WebSocket.

***

## 4. UI — REST and WebSocket to the Notification Layer

OpenG2P UI consumes the notification layer's REST APIs and opens the WebSocket connection **to the notification layer**. That code lives in `openg2p-notification-connector/notification-ui-lib`.

OpenG2P backends do **not** proxy Inbox REST or WebSocket traffic, and they do not open a second WebSocket to the UI.

```mermaid
flowchart TB
    UI["OpenG2P UI"]
    Package["notification-ui-lib"]
    Adapter["Notification Layer Adapter"]
    SDK["Notification Layer UI SDK"]
    Layer["Notification Layer"]

    UI --> Package --> Adapter --> SDK
    SDK -->|"REST"| Layer
    SDK -->|"WebSocket"| Layer
```

Application UI does **not** import the notification layer's package. The OpenG2P notification package internally handles the notification layer's SDK.

```mermaid
flowchart TB
    Package["notification-ui-lib"]
    Adapter["Notification Layer Adapter"]
    SDK["Notification Layer UI SDK"]
    Layer["Notification Layer"]

    Package --> Adapter --> SDK --> Layer
```

The chosen notification layer is an implementation detail of `notification-ui-lib`.

***

## 5. Separation of Responsibilities

```mermaid
flowchart TB
    subgraph App["OpenG2P Backend service"]
        Apps["OpenG2P Backend service<br/>(Registry, PBMS, IAM, AWE, …)"]
        BackendLib["notification-backend-lib"]
        Apps -->|"Business Event"| BackendLib
    end

    Layer["Notification Layer"]
    BackendLib --> Layer

    Layer --- Workflow
    Layer --- Template
    Layer --- Preferences
    Layer --- Scheduling
    Layer --- Retry
    Layer --- Selection["Channel Selection"]
    Layer --- InboxState["Inbox State"]

    InboxState --> UILib["notification-ui-lib"]
    UILib -->|"REST + WebSocket"| Layer
    UILib --> UI["OpenG2P UI"]
```

| Responsibility | Owner |
| --- | --- |
| Business events | OpenG2P Backend service (Registry, PBMS, IAM, AWE, …) |
| Event trigger (`send`) | Same product service, via `notification-backend-lib` |
| Notification orchestration | Notification Layer |
| Workflows, templates, email/SMS/push | Notification Layer |
| Inbox state | Notification Layer |
| Inbox REST APIs | `notification-ui-lib` → Notification Layer |
| Inbox realtime connection | `notification-ui-lib` → Notification Layer |
| Backend notification-layer abstraction | `notification-backend-lib` |
| UI notification components | `notification-ui-lib` |

***

## 6. Layer Independence

The abstraction exists so that the notification layer can be replaced without affecting OpenG2P application code.

#### Backend

```mermaid
flowchart TB
    App["OpenG2P Backend service"]
    Lib["notification-backend-lib"]

    App --> Lib

    Lib --> AdapterA["Layer Adapter"]
    Lib --> AdapterB["Another Layer Adapter"]
```

#### UI

```mermaid
flowchart TB
    UI["OpenG2P UI"]
    Package["notification-ui-lib"]

    UI --> Package

    Package --> AdapterA["Layer Adapter"]
    Package --> AdapterB["Another Layer Adapter"]
```

The OpenG2P application interacts only with the abstraction, regardless of which notification layer is used underneath.

***

## 7. Core Principle

> **OpenG2P applications define WHAT happened; `notification-backend-lib` provides a stable backend trigger interface; the notification layer determines HOW, WHEN, and THROUGH WHICH CHANNEL the notification is delivered; and `notification-ui-lib` provides a stable UI abstraction over the notification layer's Inbox REST APIs and WebSocket.**

```mermaid
flowchart TB
    Contract["OpenG2P Contract"]
    Adapter["Notification Layer Adapter"]
    Layer["Notification Layer"]

    Contract --> Adapter --> Layer
```

Therefore, **the UI and OpenG2P applications should never depend directly on any notification-layer-specific API**.

***

## 8. Possible Notification Layers

The architecture above is independent of any one product. The notification layer behind the connector adapters can be any of:

* **Novu**
* **SuprSend**
* **Custom layer** — an in-house implementation of the same contract

OpenG2P applications and UI continue to use `notification-backend-lib` and `notification-ui-lib`. Only the adapter behind those libraries changes.

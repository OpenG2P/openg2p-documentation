# Notification

OpenG2P uses a **notification layer** for templates, workflows, multi-channel delivery, and the in-app Inbox. Product services emit business events; they do not implement notification infrastructure themselves.

The integration is one library, `openg2p-notification-connector`, with two folders:

* **`notification-backend-lib`** — OpenG2P Backend services (for example Registry, PBMS, IAM, AWE) call `send()` in-process to trigger events.
* **`notification-ui-lib`** — OpenG2P UI consumes the notification layer's REST APIs and WebSocket for the Inbox. Application screens do not import a notification-layer SDK.

The architecture is independent of any one product. The layer behind the connector can be Novu, SuprSend, or a custom implementation.

See [Notification Architecture](notification-architecture.md) for the contract, package boundaries, and layer abstraction.

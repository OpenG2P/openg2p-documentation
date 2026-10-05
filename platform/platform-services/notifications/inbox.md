---
description: >-
  The staff UI inbox client. It talks to Novu from the browser. It does
  not send notifications.
---

# Inbox

The inbox client lives in the registry staff UI. There is no second package in the [notifications](https://github.com/OpenG2P/notifications) repository.

Screens use [`useNovuNotifications`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/features/notification/utils/useNovuNotifications.ts), which constructs `@novu/js` `Novu`. The hook:

* counts unread notifications
* lists a page (`limit` and `offset`)
* marks one notification read
* subscribes to `notifications.notification_received` and prepends it to the list

[`NotificationContext`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/context/NotificationContext.tsx) is what the shell renders. It passes three values into the hook.

| Client variable | Meaning |
| --- | --- |
| `NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER` | Novu environment application identifier. Public. Safe in the browser |
| `NEXT_PUBLIC_NOVU_BACKEND_URL` | Public Novu API URL |
| `NEXT_PUBLIC_NOVU_SOCKET_URL` | Public Novu WebSocket URL |

The subscriber id in that context is the string `"123"`. It is not the signed-in staff username. Until that is replaced, the bell does not follow the Keycloak user that the [connector](connector.md) notifies.

The staff UI Helm chart sets different names on the pod: `NOTIFICATION_APPLICATION_IDENTIFIER`, `NOTIFICATION_BACKEND_URL`, and `NOTIFICATION_WEBSOCKET_URL`. Those are the public hosts (`https://` plus `global.notificationApiHostname` and `global.notificationWsHostname`), not the in-cluster `NOTIFICATION_PROVIDER_URL`. The React code does not read the Helm names. An implementer wiring the bell must map them onto the `NEXT_PUBLIC_NOVU_*` variables the client reads. See [Deployment](deployment.md).

## Session

There is no FastAPI inbox route. The connector never mints a session.

The target, not wired in the staff UI today, is a Next.js route `GET /api/notifications/session`:

1. Read the Keycloak access token from the cookie. Take the staff username from that token. Do not take a subscriber id from the query string.
2. Compute `HMAC-SHA256` of that username with the server-only Novu secret.
3. Return the subscriber id, the public application identifier, the hash, and the public API and socket URLs.

The browser then gives that ticket to `@novu/js`. The hash is not an `Authorization` header on later calls. Novu exchanges it once for a subscriber JWT. List, read, and the socket use that JWT.

Helm already mounts the HMAC material on the staff UI pod as `NOTIFICATION_SECRET_KEY`, from the commons Novu secret key `novu-secret-key`. The current client does not use it. When in-app HMAC is enabled in Novu and the hash is missing, the inbox does not load. Novu's own steps are in [Prepare for production](https://docs.novu.co/platform/inbox/prepare-for-production).

The subscriber id on that session must be the same Keycloak username the connector uses as `recipient_id`. See [Architecture](architecture.md#identity).

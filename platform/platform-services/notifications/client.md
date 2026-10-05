---
description: >-
  The @openg2p/notification npm package. It renders the inbox, talks to
  the notification provider from the browser, and is what the staff UI installs.
---

# Client

[`@openg2p/notification`](https://github.com/OpenG2P/notifications/tree/develop/client) is the inbox library. A host app renders `Inbox` and passes a connection config. The package talks to the notification provider through an adapter, so application UI does not import the provider SDK.

The package does not send. Sending stays in the [connector](connector.md). Novu is the built-in adapter. Other adapters register on `NotificationFactory`. The Novu install, and where email and SMS providers are documented, is in [Novu](notification-provider/novu.md).

## What the package does

* Bell with unread badge and dropdown inbox
* All, Unread, Read, and Archived filters
* Mark as read, mark all as read, archive, and unarchive
* Live updates over the notification provider WebSocket
* Pages of 20
* Localization overrides
* `useInboxSession` for custom UI inside `Inbox`

```text
Host app
   │
   ▼
Inbox / Bell / useInboxSession
   │
   ▼
NotificationFactory.create(provider, connection)
   │
   ▼
NotificationService adapter
   │
   ▼
Notification provider API and WebSocket
```

The browser connects to the notification provider. OpenG2P backends do not proxy inbox REST or WebSocket traffic.

| Layer | Role |
| --- | --- |
| `Inbox` | Bell, panel, and session wiring |
| `NotificationFactory` | Looks up a provider by name |
| `NotificationService` | Provider-neutral inbox contract: list, counts, read, archive, live events |
| `NovuNotificationService` | Built-in adapter. Registered as `"novu"` |

Do not render `Inbox` until `provider`, `applicationIdentifier`, and `subscriber.subscriberId` are all set. The subscriber id is the same value the connector uses as `recipient_id`. See [Identity](architecture.md#identity).

## Package and install

The package name is `@openg2p/notification`, version `0.1.0`, license MPL-2.0. Published files are `dist` only: CommonJS (`dist/index.js`), ESM (`dist/index.mjs`), and types (`dist/index.d.ts`).

Peer dependencies: `react`, `react-dom`, and `lucide-react`. The built-in adapter depends on `@novu/js`. Host apps still import `Inbox` from `@openg2p/notification`.

The registry staff UI installs the packed tarball from GitHub:

```bash
npm install https://github.com/OpenG2P/notifications/raw/refs/heads/develop/client/openg2p-notification-0.1.0.tgz
```

That is the dependency in [`registry-platform/ui/staff-ui/package.json`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/package.json). Any other UI uses the same command.

To point a local app at a tarball you just built:

```bash
npm install /path/to/openg2p-notification-0.1.0.tgz
```

### Build the tarball

From `notifications/client`:

```bash
npm install
npm run build
npm test
npm pack
```

| Command | What it does |
| --- | --- |
| `npm install` | Install dependencies |
| `npm run build` | Compile `src` to `dist` with tsup (CJS, ESM, and types). The banner is `"use client"` |
| `npm test` | Run the Vitest suite once |
| `npm run test:watch` | Re-run tests on file changes |
| `npm pack` | Write `openg2p-notification-0.1.0.tgz` from `dist` |

Build before `npm pack`. Optional: `npm run lint`, `npm run lint:fix`, `npm run clean`.

Commit or publish that tarball when the staff UI (or another app) should pick up a new client. The staff UI URL above tracks `develop`, so a new tarball at that path is what `npm install` fetches.

## Render the inbox

```tsx
"use client";

import { Inbox } from "@openg2p/notification";

<Inbox
  config={{
    provider: "novu",
    subscriberHash,
    applicationIdentifier,
    backendUrl,
    socketUrl,
    subscriber: {
      subscriberId,
      email,
      firstName,
    },
  }}
  localization={{
    notifications: t("notifications"),
    empty: t("no_notifications"),
  }}
/>
```

`provider` is the adapter name. `applicationIdentifier`, `backendUrl`, and `socketUrl` are public. `subscriberHash` is the HMAC of `subscriberId` when the provider requires it. `email` and `firstName` are optional profile fields on the subscriber.

### Theme

Pass `theme` so the inbox follows the host. When omitted, the package uses the registry palette (`#EABB13`, `#ED7C22`, `#F3F1F4`, `#E1E1E1`, `#A1A1A1`, `#000000`, `#FFFFFF`).

```tsx
import type { NotificationTheme } from "@openg2p/notification";

const inboxTheme: NotificationTheme = {
  accent: "#EABB13",
  accentHover: "#ED7C22",
  surface: "#FFFFFF",
  surfaceMuted: "#F3F1F4",
  text: "#000000",
  textMuted: "#A1A1A1",
  border: "#E1E1E1",
  onAccent: "#FFFFFF",
};

<Inbox config={config} theme={inboxTheme} />
```

`accentSoft` is computed from `accent` and `surface` when you omit it. CSS variables are accepted, which is what the staff UI does.

## Switch provider

`Inbox` never imports a provider SDK. It calls `NotificationFactory.create(config.provider, connection)` and talks to the `NotificationService` that comes back. To leave Novu, write an adapter for the new system and register it under a name. The `Inbox` props, the theme, and the localization stay the same.

The package registers `"novu"` itself, from [`register.ts`](https://github.com/OpenG2P/notifications/blob/develop/client/src/providers/register.ts). Any other name has to be registered before `Inbox` mounts. If the name is not registered, `create` throws `Unknown provider "name"` and the inbox shows a connection error instead of the list.

The client and the [connector](connector.md#switch-provider) are switched separately. Both must point at the same system and use the same subscriber id. See [Both sides](#both-sides).

### The adapter contract

A provider is a class whose constructor takes a `NotificationConnection` and that implements `NotificationService`. Both types, `NotificationFactory`, and `NotificationProvider` are exported from `@openg2p/notification`.

The constructor receives the connection fields from `config`:

| Field | Meaning |
| --- | --- |
| `subscriber` | `subscriberId`, plus optional `email` and `firstName`. The id is the connector's `recipient_id` |
| `applicationIdentifier` | The provider's application or tenant id. Novu requires it. Another adapter can ignore it |
| `subscriberHash` | HMAC of `subscriberId`. Use it, or an equivalent token, to authenticate the browser |
| `backendUrl` | Public API URL |
| `socketUrl` | Public WebSocket URL |
| `context`, `contextHash` | Optional scoping values. Novu passes them through |

Throw from the constructor when a field your adapter needs is missing. The Novu adapter does this for `subscriberId` and `applicationIdentifier`.

The methods are:

| Method | What it must do |
| --- | --- |
| `list({ limit, after, filter })` | Return `{ notifications, hasMore }`. `after` is the `id` of the last item already shown. `filter` is `all`, `unread`, `read`, or `archived`. Only `archived` returns archived items. The other three exclude them |
| `unreadCount()` | Count of items that are not read and not archived |
| `readCount()` | Count of items that are read and not archived |
| `archivedCount()` | Count of archived items |
| `markRead(id)`, `readAll()` | Mark one item, or all items, read |
| `markSeen(ids)` | Mark items seen. The session batches these calls |
| `archive(id)`, `unarchive(id)` | Move an item into or out of the archive |
| `onReceived(handler)` | Call `handler` with each new notification pushed over the socket. Return a function that unsubscribes |
| `onUnreadCount(handler)` | Call `handler` with the new unread count when it changes. Return a function that unsubscribes |
| `disconnect()` | Close the socket. The inbox calls it on unmount and when the connection changes |

Every async method rejects with an `Error` on failure. The inbox shows that message and offers a retry.

Map the provider's records onto the package's `Notification` type. `id`, `title`, `body`, `read`, and `createdAt` are required. Buttons go in `primaryAction` and `secondaryAction`, each with a `label` and an optional `redirect.url`. A notification-level `redirect` makes the row open that URL. The Novu mapping is `toNotification` in [`providers/novu.ts`](https://github.com/OpenG2P/notifications/blob/develop/client/src/providers/novu.ts).

The inbox builds a new service when `provider` or any connection field changes, and it calls `disconnect()` on the old one. Keep the constructor cheap and put all socket cleanup in `disconnect()`.

### Register an adapter outside the package

Register at module scope in a client file that the page imports, so it runs in the browser before `Inbox` mounts:

```tsx
"use client";

import {
  NotificationFactory,
  type NotificationConnection,
  type NotificationListOptions,
  type NotificationListResult,
  type NotificationService,
} from "@openg2p/notification";

class AcmeNotificationService implements NotificationService {
  constructor(connection: NotificationConnection) {
    if (!connection.subscriber?.subscriberId) {
      throw new Error("Acme requires subscriberId.");
    }
    // Open the API client and the socket here.
  }

  async list(options: NotificationListOptions = {}): Promise<NotificationListResult> {
    // Map each record to the package's Notification type.
    return { notifications: [], hasMore: false };
  }

  // unreadCount, readCount, archivedCount, markRead, readAll, markSeen,
  // archive, unarchive, onReceived, onUnreadCount, and disconnect
  // follow the table above.
}

NotificationFactory.register("acme", AcmeNotificationService);
```

Then set `config.provider` to `"acme"`. In the staff UI that value comes from `NOTIFICATION_PROVIDER`.

### Add an adapter inside the package

Use this when the adapter should ship to every UI.

1. Add `src/providers/acme.ts` with the class.
2. Register it in `src/providers/register.ts`: `NotificationFactory.register("acme", AcmeNotificationService)`. That file is the only one `package.json` lists under `sideEffects`, so registration there survives bundling.
3. Export the class from `src/providers/index.ts`.
4. Add `src/providers/acme.test.ts`. Use [`novu.test.ts`](https://github.com/OpenG2P/notifications/blob/develop/client/src/providers/novu.test.ts) as the model.
5. Run `npm run build`, `npm test`, and `npm pack` as in [Build the tarball](#build-the-tarball). Commit the new tarball so the UI installs it.

### Both sides

| Step | Connector | Client |
| --- | --- | --- |
| Name | `NOTIFICATION_PROVIDER=acme` | `config.provider = "acme"` |
| Code | Provider module in the Python image. See [Switch provider](connector.md#switch-provider) | Adapter registered in the UI bundle |
| Address | `NOTIFICATION_PROVIDER_URL`, `NOTIFICATION_PROVIDER_API_KEY` | `backendUrl`, `socketUrl`, and the session values the adapter reads |
| Identity | `recipient_id` | `subscriber.subscriberId`, the same value. See [Identity](architecture.md#identity) |

In Registry, one Helm value, `global.notificationProvider`, feeds `NOTIFICATION_PROVIDER` on the staff API, the Celery worker, and the staff UI. Changing it is enough only when the Python image has the new provider module and the UI bundle has the new adapter. See [Deployment](deployment.md).

Before you switch:

* Create the matching workflows on the new system. The event keys and payload fields in [Workflows and payloads](workflows-and-payloads.md) do not change.
* Move the staff UI guard if it requires `NOTIFICATION_APPLICATION_IDENTIFIER`. [`NotificationInbox`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/components/layout/NotificationInbox.tsx) renders nothing without it, even if the new adapter does not use it.
* Notifications already stored in the old provider do not move. The inbox shows only what the new provider holds.

## Staff UI

The registry staff UI is the reference host. Source: [`ui/staff-ui`](https://github.com/OpenG2P/registry-platform/tree/develop/ui/staff-ui).

[`NotificationInbox`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/components/layout/NotificationInbox.tsx) renders `Inbox` in the header. It returns nothing until `notificationProvider`, `notificationApplicationIdentifier`, and `subscriberId` are set. Theme tokens are the staff UI CSS variables (`--color-primary-first` and the rest). Copy comes from `next-intl` (`notifications`, `no_notifications`).

The browser does not read `NEXT_PUBLIC_*` Novu variables. The server reads `NOTIFICATION_*` and passes a runtime config into the layout.

| Server variable | Passed to `Inbox` as | Meaning |
| --- | --- | --- |
| `NOTIFICATION_PROVIDER` | `config.provider` | Adapter name. `novu` in current deploys |
| `NOTIFICATION_APPLICATION_IDENTIFIER` | `applicationIdentifier` | Provider environment application identifier. Public |
| `NOTIFICATION_BACKEND_URL` | `backendUrl` | Public provider API URL |
| `NOTIFICATION_WEBSOCKET_URL` | `socketUrl` | Public provider WebSocket URL |
| `NOTIFICATION_SECRET_KEY` | used only to compute `subscriberHash` | Server-only. Never sent to the browser |

Local names are in [`ui/staff-ui/.env.example`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/.env.example). Helm maps the same pod env from `global.notificationApplicationIdentifier`, `global.notificationBackendUrl`, `global.notificationWebsocketUrl`, and `global.notificationHmacSecretKey`. See [Deployment](deployment.md#staff-ui-values).

`backendUrl` and `socketUrl` are the public hosts (`https://` plus the provider API and WebSocket hostnames). They are not the in-cluster connector URL.

### Session

There is no separate inbox route and the connector does not mint a session. [`getNotificationHmac`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/app/api/_lib/notification-hmac.ts) runs when the layout loads runtime config:

1. Read the Keycloak access token from the cookie.
2. Take `preferred_username` as `subscriberId`, plus `email` and `given_name` when the token has them. The subscriber id is not taken from the query string.
3. When `NOTIFICATION_SECRET_KEY` is set, compute `HMAC-SHA256` of that username and return it as `subscriberHash`.

[`clientSafeConfig.getAll()`](https://github.com/OpenG2P/registry-platform/blob/develop/ui/staff-ui/src/app/api/_lib/client-safe-config.ts) puts those fields on the runtime config. `Inbox` gives the hash to the provider adapter. Later list, read, and socket calls use the subscriber token the provider issues from that hash. The hash is not an `Authorization` header on those calls.

The subscriber id must be the same Keycloak username the connector uses as `recipient_id`. When in-app HMAC is enabled on the provider and the hash is missing, the inbox does not load. A missing secret still returns the subscriber id, so the bell can render, and the provider then rejects the session if HMAC is required.

The staff UI does not configure email or SMS delivery. Those credentials are added on the provider. See [Email and SMS](notification-provider/novu.md#email-and-sms).

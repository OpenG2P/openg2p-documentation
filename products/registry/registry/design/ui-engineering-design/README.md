---
description: Engineering design of the OpenG2P Registry staff portal UI and schema-driven widget system.
---

# UI engineering / design

OpenG2P Registry presents a single, config-driven staff portal UI. Domain registries such as Farmer Registry and National Social Registry do not ship separate frontend applications. They share one Staff Portal binary and customize behaviour through register metadata, UI schemas, themes, languages, and environment configuration.

The UI is implemented in the `registry-platform` repository under `ui/`:

| Component | Path | Package / image |
| --- | --- | --- |
| Staff Portal | `ui/staff-ui` | `openg2p-registry-staff-ui` (Docker) |
| Widget library | `ui/ui-widgets` | `@openg2p/registry-widgets` (npm) |

This page describes the overall UI engineering design. Widget-library internals and per-widget behaviour are covered in the child pages:

{% content-ref url="registry-ui-widget-library.md" %}
[registry-ui-widget-library.md](registry-ui-widget-library.md)
{% endcontent-ref %}

{% content-ref url="widget-reference.md" %}
[widget-reference.md](widget-reference.md)
{% endcontent-ref %}

Related design topics: [Dynamic UI rendering](../../features/dynamic-ui-rendering.md), [Registry themes](../registry-themes.md), [Dynamic languages](../dynamic-languages.md), [Change management](../change-management.md), [Registrant Auth — OIDC](../registrant-authentication-oidc-widget/), [Intake forms](../intake-forms/).

## Design goals

| Goal | How the UI achieves it |
| --- | --- |
| **Domain-agnostic core** | One Staff Portal image serves all registries; screens are driven by metadata and UI schemas |
| **Change-request-centric editing** | Section saves produce change-request payloads; live master data is never silently patched from the UI |
| **Schema-driven forms** | JSON UI schemas (`Section` → `Panel` → `Widget`) render register detail, intake, and CR review screens |
| **Secure by default** | Browser calls Next.js route handlers (BFF); tokens stay in HTTP-only cookies; RBAC gates actions in the UI |
| **Runtime customization** | Themes, languages, and feature behaviour come from backend config without rebuilding the UI image |
| **Extensible widgets** | New field types register into `@openg2p/registry-widgets` without forking the portal |

## High-level architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (Staff Portal)                       │
│  Next.js App Router  ·  React 19  ·  Tailwind CSS  ·  next-intl  │
│                                                                  │
│  Shell (auth, RBAC, nav, theming, i18n)                          │
│       │                                                          │
│       ▼                                                          │
│  @openg2p/registry-widgets                                       │
│  WidgetProvider · SectionRenderer · widgetRegistry               │
└──────────────────────────────┬──────────────────────────────────┘
                               │ relative /api/* (cookies)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Next.js BFF (Route Handlers)                         │
│  proxyToBackend · requireAuth · CSP · client-safe config         │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
     Staff Portal API                  Masterdata API
     (BACKEND_API_URL)            (MASTERDATA_BACKEND_API_URL)
                │
                ▼
         OpenG2P IAM / Keycloak
```

**Responsibilities**

* **Staff Portal** — application shell: routing, authentication, permissions, configuration screens, register list/detail chrome, BFF proxies, branding, and i18n.
* **Widget library** — reusable schema renderer: binds widgets to data paths, validates input, evaluates conditions, loads data sources, and packages section-level changes for change requests.
* **Backend APIs** — source of truth for register metadata, section UI schemas, record data, permissions, themes, and languages.

Farmer Registry, Social Registry, and other domain deployments differ by configuration and data — not by a different React application.

## Technology stack

| Layer | Choice |
| --- | --- |
| Framework | Next.js 16 (App Router), `output: "standalone"` |
| UI library | React 19 |
| Styling | Tailwind CSS 4 + CSS variables for brand tokens |
| Widget state | Redux Toolkit (scoped to the widget subsystem) |
| App state | React Context (`Auth`, `Rbac`, `Register`, runtime config, notifications) |
| Validation | Built-in widget rules + Zod |
| i18n | next-intl (portal); widgets accept a host `t` function via `WidgetProvider` |
| Icons / motion | lucide-react, react-icons, Framer Motion |
| Notifications | Novu (`@novu/js`), react-toastify |
| Credentials / VCs | Inji SDK, SD-JWT helpers |

There is no third-party component kit such as MUI or Ant Design. Portal chrome and widgets use custom components styled with Tailwind and theme CSS variables.

## Repository layout

```text
registry-platform/
├── apis/                          # FastAPI services (staff portal, partner, …)
├── core/                          # Shared domain / persistence
├── celery/                        # Async workers
└── ui/
    ├── staff-ui/                  # Next.js Staff Portal
    │   ├── src/app/[locale]/…     # Routes (thin pages)
    │   ├── src/app/api/…          # BFF route handlers
    │   ├── src/features/…         # Feature modules
    │   ├── src/context/…          # Auth, RBAC, register, runtime config
    │   ├── src/shared/widgets/    # RegistryWidgetProvider, branding → WidgetTheme
    │   ├── src/i18n/…             # next-intl routing and message loading
    │   ├── sample-locale/         # Example core + domain translation packs
    │   └── Dockerfile
    └── ui-widgets/                # @openg2p/registry-widgets
        ├── src/components/        # WidgetProvider, Section/Panel renderers, Section Builder
        ├── src/widgets/           # Built-in widget components
        ├── src/registry/          # widgetRegistry + defaultWidgets
        ├── src/hooks/             # useBaseWidget and helpers
        ├── src/store/             # Redux widget slice
        └── src/theme/             # Default OpenG2P theme tokens
```

Feature code lives under `src/features/*` (register, change-request, intake-form, configuration, filter, messages, notification, verifiable-credentials, approval, export). App Router pages stay thin and compose feature components.

## Schema-driven UI model

Register screens are not hard-coded field layouts. The backend returns a **UI schema** per section (`section_ui_schema`), typically via register APIs such as get-sections. The widget library turns that schema into React UI.

### Hierarchy

1. **Section** — top-level unit (`section-id`, title, editable flag, panels). Editing and save are section-scoped and feed the change-request workflow.
2. **Panel** — layout container (`panel-orientation`: horizontal or vertical; nested panels or widgets).
3. **Widget** — leaf field or composite control (`widget` type key, `widget-id`, `widget-data-path`, validation, format, data-source, conditions).

This is the same model described under [Dynamic UI rendering](../../features/dynamic-ui-rendering.md).

### Render modes

`SectionsContainer` in the widget library supports three host modes:

| Mode | Purpose |
| --- | --- |
| **RegistryView** | Live register record view; section-level edit/save → change request |
| **CRView** | Change-request review (read-only; NEW/OLD comparison) |
| **IntakeForm** | Multi-section registration / intake accordion flow |

The Staff Portal wires the same library into register detail, change-request screens, and intake forms through `RegistryWidgetProvider` (host `t`, `dataSourceRequestHandler`, branding theme, and optional `hostContext`).

### Data binding and data sources

* Widgets bind to record data through `widget-data-path` (single path or multi-path maps).
* Option lists come from **static** schema options, **API** data sources, or **schema** reference data.
* Widgets do not call backend services directly. The host supplies a `dataSourceRequestHandler` that maps `(service, endpoint, method, params)` to authenticated BFF routes such as `/api/{service}/{endpoint}`.
* Optional `hostContext` on `WidgetProvider` injects host values (for example register / record ids) into lookup widgets such as `parent-lookup`.

### Change packaging

When a user edits a section and saves, the library computes `SectionChanges` (old vs new `records`, plus optional `section_files` for uploads) for the host. The portal turns those changes into a change request rather than writing the master record immediately. This keeps the UI aligned with [Change management](../change-management.md).

## Staff Portal engineering

### Routing and navigation

Routes use the Next.js App Router with a `[locale]` segment and next-intl middleware.

| Area | Typical path |
| --- | --- |
| Home / dashboard | `/[locale]/` |
| Register list / detail | `/[locale]/register/[type]`, `.../[id]` |
| Version history | `.../[id]/version-history` |
| Change requests | `/[locale]/change-request`, nested under register / `tasks` |
| Intake forms | `/[locale]/intake-form/[type]/...`, task-scoped variants |
| Configuration | `/[locale]/configuration/{registers,intake-forms,registry,data-models,ingest,outgest,...}` |
| Messages | `/[locale]/incoming-messages`, `/outgoing-messages` |
| Profile / errors | `/myprofile`, `/record-access-denied` |

Navigation helpers (`Link`, `useRouter`) come from the locale-aware `@/i18n/navigation` module so links stay under the active locale.

### BFF and API integration

Browser code calls **relative** `/api/...` routes. Each route handler authenticates the session and proxies to a backend:

* `proxyToBackend` — attaches `Authorization: Bearer` from cookies, wraps OpenG2P request/response envelopes, and targets either the default Staff Portal API or the masterdata backend.
* `requireAuth` — gates protected API routes.
* Client data fetching uses a shared `useFetch` hook (not React Query / SWR). HTTP 401 triggers re-login.

Runtime env is read at request time (not baked into the client bundle for secrets). Important variables include `BACKEND_API_URL`, `MASTERDATA_BACKEND_API_URL`, `IAM_URL`, `KEYCLOAK_LOGOUT_URL`, `APPLICATION_MNEMONIC`, `COOKIE_DOMAIN`, CSP fragments, and verification / VP settings. See `ui/staff-ui/.env.example` and the [Staff Portal install guide](../../developer-zone/developer-install/openg2p-registry-staff-portal-ui.md).

### Authentication

1. `/api/login` starts an IAM authentication transaction and redirects to the IdP (Keycloak OIDC behind OpenG2P IAM).
2. Access and ID tokens are stored in cookies (`X-Access-Token`, `X-ID-Token`).
3. `/api/me` hydrates the signed-in user into `AuthProvider`.
4. `/api/logout` clears the session and redirects through Keycloak logout.

Registrant-facing foundational-ID authentication (for example during intake) is a separate OIDC widget flow — see [Registrant Auth — OIDC](../registrant-authentication-oidc-widget/).

### Authorization (RBAC)

Permissions are loaded from `/api/permissions` (IAM `get_application_permissions_for_user` for `APPLICATION_MNEMONIC`, typically `registry-staff-portal`).

* Action strings follow a `feature:action` pattern (for example `changeRequest:view`, `changeRequest:create`, `changeRequest:approve`).
* `useRbac()` exposes `can` / `canAny` / `canAll`.
* `<RequireAction action="...">` gates routes and UI blocks; imperative `can(...)` hides controls such as section edit when the user cannot create change requests.

UI checks are a convenience layer. Backend APIs remain authoritative for enforcement.

### Theming and branding

Brand colours and related tokens are applied at runtime from registry configuration (`/registry-config/get_registry_configuration`) as CSS variables on the app shell, for example:

* `--color-primary-first` / `--color-primary-second`
* `--color-secondary-first` / `--color-secondary-second` / `--color-secondary-third`
* `--color-neutral-first` / `--color-neutral-second`
* toast colour tokens

Tailwind maps these variables into utility classes. Admins manage themes under Configuration → Registry → Themes. Design details of theme persistence are in [Registry themes](../registry-themes.md).

The widget library also supports a dynamic theme: the portal maps the same branding into a `WidgetTheme` (via `brandingToWidgetTheme`) and passes it to `WidgetProvider` through `RegistryWidgetProvider`, so section/widget chrome follows the active registry theme as well.

### Internationalization

* **Portal**: next-intl with locale routing. Message catalogues are loaded primarily from backend language configuration, with bundled English (and sample packs under `sample-locale/`) as fallback.
* **Widgets**: accept a host `t` function via `WidgetProvider` (Staff Portal passes next-intl translations), and can translate schema labels through `translateUISchema`.
* Admins manage languages under Configuration → Registry → Languages. See [Dynamic languages](../dynamic-languages.md).

### Content Security Policy

In non-development environments, middleware builds a CSP header from env-configured source lists (`CSP_SRC_*`). This keeps script, style, image, connect, and frame policies deployable without code changes.

## Widget library engineering

`@openg2p/registry-widgets` is the schema renderer used by the Staff Portal. Importing the package registers the default widget set.

### Composition stack

| Piece | Role |
| --- | --- |
| `RegistryWidgetProvider` (Staff Portal) | Host wrapper: branding → `WidgetTheme`, next-intl `t`, shared data-source handler |
| `WidgetProvider` | Redux store, theme CSS variables, data-source handler, translate, `hostContext`, event bus |
| `SectionsContainer` | Multi-section orchestration and mode selection |
| `SectionRenderer` / `PanelRenderer` | Layout, edit/save, change extraction |
| `WidgetRenderer` | Resolves `config.widget` through `widgetRegistry` |
| `useBaseWidget` | Shared value binding, validation, visibility, data sources, formatting |
| `WidgetEventBus` | Cross-widget events (`change`, `blur`, `focus`, `reload`, `clear`) |

### Default widgets

Built-in keys (22): `text`, `textarea`, `number`, `boolean`, `date`, `datetime`, `select`, `multi-select`, `radio`, `checkbox`, `file`, `phone`, `display`, `profile`, `table`, `dialog-table`, `header-section`, `scores-display`, `id-authentication`, `register-lookup`, `parent-lookup`, `geo-hierarchy`.

### Extension

```ts
widgetRegistry.register({
  widget: 'my-widget',
  component: MyWidget,
});
```

Custom widgets should call `useBaseWidget({ config })` so they participate in the same binding, validation, and conditional-logic pipeline.

### Section Builder

The package includes a Section Builder (visual + JSONC) for authoring `section_ui_schema` without hand-writing every schema by hand. Sample schemas live under `ui/ui-widgets/example-ui-schema/` in `registry-platform`.

For architecture depth, unique registry features (CR view, multi-path binding, conditions), and the layered data flow, see [Widget Library](registry-ui-widget-library.md). For practical per-widget configuration, see [Widget Reference](widget-reference.md).

## Application state model

| Concern | Mechanism |
| --- | --- |
| Widget values, errors, touched, loading, data-source options | Redux Toolkit widget store |
| Signed-in user | `AuthProvider` |
| Permissions | `RbacProvider` |
| Register list / current register / tabs / record identity | Register-related contexts |
| Branding and client-safe feature flags | `RuntimeConfigProvider` |
| In-app notifications | Notification context + Novu |

Redux is intentionally scoped to the widget subsystem. The application shell prefers React Context and feature hooks.

## Customization model (domain registries)

| Mechanism | What it changes | Code required? |
| --- | --- | --- |
| Register / tab / section metadata + `section_ui_schema` | Fields, layout, widgets per register | No |
| Section Builder / configuration APIs | Author and update UI schemas | No |
| Themes | Colours, branding | No |
| Language packs (core + domain) | Labels and copy | No |
| Environment variables | Backend URLs, IAM, CSP, VP/verify, page size | No (ops) |
| `widgetRegistry.register` | New widget types | Yes (library or portal extension) |

Domain registers still share the same hierarchical tab navigation, verification panels, version history, pending-change alerts, and deduplication screens. That shared chrome is what [Dynamic UI rendering](../../features/dynamic-ui-rendering.md) refers to when it says customized registers render themselves with the same navigation patterns.

## Build, packaging, and deployment

### Widget library → npm

* Package name: `@openg2p/registry-widgets`
* Build: Rollup (`npm run build`)
* CI publishes from `registry-platform` (develop pushes typically produce prerelease/`next` tags; release workflows publish `latest` and keep the Staff Portal dependency in sync)

### Staff Portal → container

* Dockerfile builds a standalone Next.js image as user `nextjs` on port 3000
* Published as `openg2p/openg2p-registry-staff-ui:<tag>`
* At runtime the container needs backend and IAM URLs, cookie domain, application mnemonic, and CSP settings (see `.env.example`)

Local development typically runs the Next app against deployed or local Staff Portal / masterdata APIs. Production deployments place the UI behind nginx (or equivalent) with the env-driven BFF configuration described in the developer install guide.

## Engineering patterns (summary)

1. **Config-driven UI** — backend schemas drive forms; domain apps are data and metadata, not forks.
2. **Plugin widget registry** — string type keys map to React components.
3. **`useBaseWidget` facade** — shared binding, validation, conditions, and data sources for all inputs.
4. **Host-owned data-source adapter** — widgets stay portable; auth and CORS stay in the BFF.
5. **Change-request-centric saves** — section edits become reviewable change payloads (`records` + `section_files`).
6. **Dual/triple render modes** — RegistryView, CRView, and IntakeForm share one library.
7. **BFF + cookie session** — browser never needs to hold bearer tokens in application JS for normal API calls.
8. **Action-string RBAC** — `feature:action` constants with declarative and imperative checks.
9. **Runtime branding and languages** — CSS variables and message catalogues from backend config; dynamic `WidgetTheme` for the widget library as well.
10. **Section Builder** — dual visual/JSON authoring for implementers.
11. **Event bus and geo cascade helpers** — loosely coupled widget communication for dependent fields.
12. **React Compiler** — enabled in the Next.js config for the Staff Portal build.

## Key source locations

**Staff Portal (`ui/staff-ui`)**

* `src/app/[locale]/layout.tsx` — providers, branding CSS variables
* `src/proxy.ts` — next-intl + CSP middleware
* `src/app/api/_lib/backend-proxy.ts` — BFF proxy
* `src/app/api/_lib/env-config.ts` / `client-safe-config.ts` — runtime configuration
* `src/context/` — auth, RBAC, register, runtime config
* `src/shared/widgets/` — `RegistryWidgetProvider`, `brandingToWidgetTheme`
* `src/features/register/` — register list/detail and section save
* `src/components/shared/RequireAction.tsx` — declarative RBAC gate
* `sample-locale/` — example translation pack shape

**Widget library (`ui/ui-widgets`)**

* `src/index.ts` — public exports; registers default widgets on import
* `src/registry/defaultWidgets.ts` — built-in widget map
* `src/hooks/useBaseWidget.ts` — shared widget behaviour
* `src/components/WidgetProvider.tsx`, `SectionRenderer.tsx`, `SectionsContainer.tsx`
* `src/components/SectionBuilder/` — schema authoring UI
* `src/theme/` — default theme tokens
* `example-ui-schema/` — sample section and widget configs

## Further reading

{% content-ref url="registry-ui-widget-library.md" %}
[Widget Library](registry-ui-widget-library.md)
{% endcontent-ref %}

{% content-ref url="widget-reference.md" %}
[Widget Reference](widget-reference.md)
{% endcontent-ref %}

{% content-ref url="../registrant-authentication-oidc-widget/" %}
[Registrant Auth — OIDC](../registrant-authentication-oidc-widget/)
{% endcontent-ref %}

{% content-ref url="../registry-themes.md" %}
[Registry themes](../registry-themes.md)
{% endcontent-ref %}

{% content-ref url="../dynamic-languages.md" %}
[Dynamic languages](../dynamic-languages.md)
{% endcontent-ref %}

{% content-ref url="../change-management.md" %}
[Change management](../change-management.md)
{% endcontent-ref %}

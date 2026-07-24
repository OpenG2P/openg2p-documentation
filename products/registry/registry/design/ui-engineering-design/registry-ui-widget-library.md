# Widget Library

## What is registry UI widget?

The **Registry UI Widget Library** (`@openg2p/registry-widgets`) is a comprehensive, extensible React component system designed specifically for building dynamic, data-driven forms and user interfaces in the OpenG2P registry ecosystem. It provides a declarative, schema-based approach to creating complex forms with advanced features like conditional logic, multi-path data binding, validation, internationalization, and more.

At its core, the library transforms JSON-based UI schemas into fully functional React components, enabling developers to build sophisticated registry interfaces without writing repetitive form code. The library is built with TypeScript, Redux for state management, and follows a plugin-based architecture that allows for easy extension and customization.

The library is built with **TypeScript**, **React 19**, and **Redux Toolkit**. It uses a plugin-based widget registry, schema-driven layout (Section → Panel → Widget), and host-provided API handlers so registry apps stay in control of auth, CORS, and backend services.

## Purpose

The library is the UI foundation for OpenG2P registry applications. It powers staff-portal flows where forms are driven by JSON schemas instead of one-off UI code—especially for registers, intake, change requests, and program-specific beneficiary data.

## Use cases

{% stepper %}
{% step %}
**Register form (`RegistryView`)**

* Schema-driven section → panel → widget layouts for register records
* Read-only registry views with optional section-level edit and save
* Multi-path binding for identity, geo hierarchy, documents, and linked records
* Header, profile, scores, and display widgets for record context
{% endstep %}

{% step %}
**Change request (`CRView`)**

* Review proposed registry changes before approval
* Audit trail metadata (`createdBy`, `createdDate`, `approvedBy`, `approvedDate`)
* Side-by-side or section-based comparison of old and new values
* Read-only CR review aligned with staff-portal change-request and approval flows
{% endstep %}

{% step %}
**Intake form (`IntakeForm`)**

* Multi-section accordion intake for new registrant / user registration
* Draft vs locked editing, validation, and structured submit payloads
* Conditional fields, multi-select attributes, geo hierarchy, and document uploads
* Used for intake submissions before records land in the register
{% endstep %}

{% step %}
**Beneficiary form**

* Program-specific schemas (attributes, tabs, and sections configured per register or program)
* Capture beneficiary data required by a program without rewriting form UI
* Tables and dialog-tables for repeating household/member-style records
* Register lookup and ID authentication for cross-register and foundational ID flows
{% endstep %}
{% endstepper %}

## Unique features for OpenG2P Registry

### Section-based architecture with three render modes

Layouts follow **Section → Panel → Widget**:

* **Sections**: Independently editable containers; optional supporting documents; column span; per-section hide-edit
* **Panels**: Horizontal or vertical nesting with column span
* **Widgets**: Registered React components bound to data paths

`SectionsContainer` / `SectionRenderer` support three modes:

| Mode | Role |
| --- | --- |
| `RegistryView` | View registry data; edit one section at a time; save produces old/new change sets |
| `CRView` | Review a change request; audit footer (`createdBy`, `createdDate`, `approvedBy`, `approvedDate`) |
| `IntakeForm` | Accordion multi-section intake; draft vs locked; form handle for validate / get data |

CSS grid alignment, responsive stacking, and `section-column-span` / `widget-column-span` support multi-column registry layouts.

### Multi-path data binding

`widget-data-path` accepts either a single dot-notation path (most input widgets) or a map of **logical keys → store paths** for widgets that compose several fields into one UI block.

Single path:

```json
{
  "widget": "text",
  "widget-id": "full_name",
  "widget-data-path": "register-id.full_name"
}
```

Multi-path — the widget defines which logical keys it understands, and the schema maps each to a store path. The `profile` widget composes an identity card from three fields:

```json
{
  "widget": "profile",
  "widget-id": "user_profile",
  "widget-data-path": {
    "image": "register-id.photo",
    "name": "register-id.display_name",
    "id": "register-id.national_id"
  }
}
```

The `geo-hierarchy` widget uses multi-path to separate what it **writes** from what it **reads**: only the deepest selected level id is persisted to `value`, while `hierarchy` is a read path used to hydrate the cascading selects in view/edit mode:

```json
{
  "widget": "geo-hierarchy",
  "widget-id": "individual_geo_hierarchy",
  "widget-data-path": {
    "value": "register-id.geo_lowest_level_value_id",
    "hierarchy": "register-id.geo_code_hierarchy_json"
  }
}
```

Other multi-path widgets follow the same pattern:

* **`header-section`** — maps record summary fields (`name`, `functionalId`, `status`, `completionScore`, `createdBy`, `lastApprovedAt`, …) to record columns
* **`id-authentication`** — maps auth fields (`foundationalId`, `lastAuthenticatedOn`, `lastAuthenticationStatus`, `expiryDate`, …) used for both display and API calls

### Host-driven data sources and API access

Option widgets load data from:

* **Static** options in the schema
* **API** sources via `service` + `endpoint` (or legacy `url`), resolved by the host’s `dataSourceRequestHandler`
* **Schema** references inside `schemaData`

Dependent loading uses `dependsOn` and/or **`widget-cascade`** (event bus: clear/reload child options when a parent changes). Geo hierarchy uses a dedicated API shape (`levelsEndpoint` + `valuesEndpoint`).

### Internationalization (i18n)

Translation is host-owned. Pass a `t` function to `WidgetProvider` (for example from `react-i18next`). Use `translateUISchema` / `translateWidgetConfig` / `translatePanelConfig` to resolve label, placeholder, help text, tooltip, and static option keys before render. Missing keys fall back to the original string.

### Advanced conditional logic

`widget-data-options` supports `show`, `hide`, `enable`, `disable`, and **`require`**, either as a single rule or an `actions` array. Operators: `equals`, `notEquals`, `notEmpty`, `empty`, `greaterThan`, `lessThan`, `contains`, `notContains`. Conditions use dot-notation field paths and re-evaluate as values change. Dialog-table columns can condition on sibling row fields.

### Comprehensive widget registry (22 default widgets)

| Category | Widgets |
| --- | --- |
| Input | `text`, `textarea`, `number`, `phone`, `date`, `datetime`, `file`, `select`, `multi-select`, `radio`, `checkbox`, `boolean`, `geo-hierarchy`, `docs` |
| Selection / lookup | `register-lookup` |
| Display / identity | `display`, `profile`, `header-section`, `scores-display` |
| Tables | `table`, `dialog-table` |
| Domain | `id-authentication` |

Custom widgets register through `widgetRegistry` without changing core code.

### Validation and formatting

* Built-in rules: required, pattern, min/max length, min/max value
* `validationType`: `email`, `phone`, `url`
* Zod schemas via `widget-data-validation.zodSchema`
* Real-time validation on change/blur with touched-state error display
* Formatting for dates, datetime, phone, numbers, and text (case, charset, mask, char counter)

### File and document handling

* **`file`**: single/multiple upload, preview, serialization for storage
* **`docs`**: fixed upload slots in a three-column layout, per-slot accept/max-size/required
* **Section supporting documents**: section-level document config rendered alongside panels

### Change request design and CRView

* Section save callbacks receive structured old/new values
* Dirty tracking and cancel/revert of in-progress edits
* CRView audit trail and read-only review
* Integration points for backend CR create/approve workflows

### Registry-specific widgets

* **`header-section`**: Record image, name, functional ID, status, scores, audit stamps
* **`scores-display`**: Sorted list of computed scores (type, value, time, triggering CR)
* **`id-authentication`**: Initiate OIDC/provider auth; show status, expiry, foundational ID
* **`register-lookup`**: Paginated search of another register; store linked record id
* **`geo-hierarchy`**: Cascading geo levels with optional multi-column layout

### Section builder tooling

`SectionBuilder`, `VisualBuilderPanel`, `JSONEditorPanel`, `SectionTree`, and `PropertyEditor` help author and edit UI schemas visually or as JSON during development.

### Redux state, events, and theming

* Centralized values, errors, touched, loading, and data-source options
* `WidgetEventBus` + `useWidgetCascade` for cross-widget reload/clear
* Optional `theme` on `WidgetProvider` (CSS variables for colors, section, panel, button, widget chrome)
* Tailwind-friendly class hooks; host controls overall look

### TypeScript-first design

Full types for configs, data sources, section modes, theme, and store. Zod peer dependency for schema validation.

## Architecture Overview

{% embed url="https://miro.com/app/board/uXjVGPIon0M=/?share_link_id=859507579636" %}

**Application layer** — Host apps pass UI schemas into `SectionsContainer` / `SectionRenderer` / `WidgetRenderer`, choose mode (`RegistryView` | `CRView` | `IntakeForm`), and supply `dataSourceRequestHandler`, `schemaData`, `onSectionSave`, and optional `t` / `theme`.

**Widget registry layer** — Maps widget names to React components. Defaults register on import; apps can add custom widgets.

**Widget components layer** — Twenty-two built-in widgets plus any registered customs.

**Core hooks layer** — `useBaseWidget` (state, validation, conditions, data sources, formatting), `useWidgetCascade`, `useWidgetEventBus`, `useWidgetTheme`, and specialized hooks (for example `useGeoHierarchy`).

**State management layer** — Redux store / widget slice as the single source of truth for form values and UI state.

**Utility layer** — Path utilities, validation, formatting, conditions, data-source helpers, file serialization/preview, schema translation, section validate/revert/snapshot.

#### Data flow

1. **Top-down (render):** UISchema → registry lookup → components + hooks → Redux + utilities
2. **Bottom-up (update):** User input → hook `onChange` → Redux → cascade/events → re-render
3. **Section save:** Snapshot old/new → host `onSectionSave` → optional CR pipeline

## Benefits for OpenG2P Registry

* **Rapid development** — JSON schemas instead of one-off form code
* **Consistency** — Shared widgets and section behaviors across portals
* **Governance** — Change-request–oriented edit/save and CRView audit
* **Extensibility** — Registry plugins, cascade, and host API handler
* **Type safety** — TypeScript + Zod
* **i18n-ready** — Host `t` + schema translation utilities
* **Domain fit** — Geo hierarchy, docs, register lookup, ID auth, scores, header

## Conclusion

`@openg2p/registry-widgets` is a purpose-built foundation for OpenG2P registry UIs. Section modes, multi-path binding, host-driven APIs, conditional logic, and a registry-focused widget set (including geo hierarchy, documents, lookup, and authentication) cover registration, intake, viewing, and change-request review without sacrificing extensibility.

Use it when you need schema-driven forms that stay aligned with registry governance: section-level edits, auditable change sets, and production-ready widgets for identity, location, documents, and linked records.

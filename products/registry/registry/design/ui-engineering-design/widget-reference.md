# Widget Reference

A practical, widget-by-widget reference for `@openg2p/registry-widgets`. It covers JSON widget configuration, data binding via `widget-data-path`, validation and formatting, conditional show/hide/enable/disable/require logic, static and API data sources, section/panel rendering in `RegistryView` / `CRView` / `IntakeForm` modes, theming and i18n, cascade events, and how to register custom widgets.

## Table of contents

1. [Introduction](#introduction)
2. [Installation and setup](#installation-and-setup)
3. [Core concepts](#core-concepts)
   * [Widget configuration](#widget-configuration)
   * [useBaseWidget hook](#usebasewidget-hook)
   * [Widget registry](#widget-registry)
4. [Basic usage](#basic-usage)
   * [Rendering a single widget](#rendering-a-single-widget)
   * [Using sections and panels](#using-sections-and-panels)
5. [Widget configuration](#widget-configuration-1)
   * [Basic configuration properties](#basic-configuration-properties)
   * [Example: complete text input configuration](#example-complete-text-input-configuration)
6. [Data binding](#data-binding)
   * [Single path binding](#single-path-binding)
   * [Multi-path binding](#multi-path-binding)
   * [Accessing data](#accessing-data)
   * [Getting other field values](#getting-other-field-values)
7. [Validation](#validation)
   * [Built-in validation rules](#built-in-validation-rules)
   * [Predefined validation types](#predefined-validation-types)
   * [Zod schema validation](#zod-schema-validation)
   * [Manual validation](#manual-validation)
8. [Conditional logic](#conditional-logic)
   * [Single rule](#single-rule)
   * [Multiple actions](#multiple-actions)
   * [Operators](#operators)
9. [Data sources](#data-sources)
   * [Static](#static)
   * [API](#api)
   * [Dependent API (`dependsOn`)](#dependent-api-dependson)
   * [Schema reference](#schema-reference)
   * [Geo hierarchy data source](#geo-hierarchy-data-source)
10. [Formatting](#formatting)
    * [Date / datetime](#date--datetime)
    * [Number](#number)
    * [Text](#text)
    * [Phone](#phone)
    * [Boolean](#boolean)
11. [Widget cascade](#widget-cascade)
12. [Section modes](#section-modes)
13. [Widget reference](#widget-reference)
    * [Default widget catalog (22)](#default-widget-catalog-22)
    * [Text Input Widget (`text`)](#text-input-widget-text)
    * [Text Area Widget (`textarea`)](#text-area-widget-textarea)
    * [Number Input Widget (`number`)](#number-input-widget-number)
    * [Phone Input Widget (`phone`)](#phone-input-widget-phone)
    * [Date Input Widget (`date`)](#date-input-widget-date)
    * [DateTime Input Widget (`datetime`)](#datetime-input-widget-datetime)
    * [File Input Widget (`file`)](#file-input-widget-file)
    * [Select Widget (`select`)](#select-widget-select)
    * [Multi Select Widget (`multi-select`)](#multi-select-widget-multi-select)
    * [Radio Widget (`radio`)](#radio-widget-radio)
    * [Checkbox Widget (`checkbox`)](#checkbox-widget-checkbox)
    * [Boolean Widget (`boolean`)](#boolean-widget-boolean)
    * [Geo Hierarchy Widget (`geo-hierarchy`)](#geo-hierarchy-widget-geo-hierarchy)
    * [Docs Widget (`docs`)](#docs-widget-docs)
    * [Display Widget (`display`)](#display-widget-display)
    * [Profile Widget (`profile`)](#profile-widget-profile)
    * [Header Section Widget (`header-section`)](#header-section-widget-header-section)
    * [Scores Display Widget (`scores-display`)](#scores-display-widget-scores-display)
    * [ID Authentication Widget (`id-authentication`)](#id-authentication-widget-id-authentication)
    * [Register Lookup Widget (`register-lookup`)](#register-lookup-widget-register-lookup)
    * [Table Widget (`table`)](#table-widget-table)
    * [Dialog Table Widget (`dialog-table`)](#dialog-table-widget-dialog-table)
    * [Widget configuration summary](#widget-configuration-summary)
14. [Creating custom widgets](#creating-custom-widgets)
15. [Advanced patterns](#advanced-patterns)
    * [Intake form with form handle](#intake-form-with-form-handle)
    * [Dynamic form generation](#dynamic-form-generation)
    * [Section-level change tracking](#section-level-change-tracking)
    * [Section builder](#section-builder)
16. [Internationalization](#internationalization)
    * [Pass `t` to WidgetProvider](#pass-t-to-widgetprovider)
    * [Translate schemas programmatically](#translate-schemas-programmatically)
17. [Theming](#theming)
18. [Best practices](#best-practices)
    * [Widget IDs](#widget-ids)
    * [Data paths](#data-paths)
    * [Validation](#validation-1)
    * [Conditional logic](#conditional-logic-1)
    * [Data sources](#data-sources-1)
    * [Performance](#performance)
    * [Type safety](#type-safety)
19. [Troubleshooting](#troubleshooting)
    * [Widget not rendering](#widget-not-rendering)
    * [Validation not working](#validation-not-working)
    * [API data source not loading](#api-data-source-not-loading)
    * [Conditional logic not working](#conditional-logic-not-working)
    * [Geo hierarchy empty](#geo-hierarchy-empty)
    * [TypeScript errors](#typescript-errors)
20. [Conclusion](#conclusion)

## Introduction

The OpenG2P Registry UI Widgets library builds dynamic forms from JSON configurations. Current capabilities include:

* **22 pre-built widgets** (inputs, tables, display/identity, geo hierarchy, docs, lookup, ID auth)
* **Redux-based state management** for values, errors, touched, loading, and data sources
* **Flexible data binding** with single-path and multi-path maps
* **Validation** with built-in rules and Zod schemas
* **Conditional logic** including dynamic `require`
* **Host-driven API data sources** via `dataSourceRequestHandler`
* **i18n** via host `t` function and schema translation helpers
* **Theme** tokens applied as CSS variables on `WidgetProvider`
* **Extensible registry** for custom widgets
* **SectionBuilder** tooling for authoring schemas

Package version context: `@openg2p/registry-widgets` (see package for current version). Peer stack: **React 19**, **Redux Toolkit**, **Zod 4**.

## Installation and setup

{% stepper %}
{% step %}
**Install the package**

```bash
npm install @openg2p/registry-widgets
```
{% endstep %}

{% step %}
**Install peer dependencies**

```bash
npm install react react-dom @reduxjs/toolkit react-redux zod
```

Optional (host i18n): `i18next` and `react-i18next` if you pass their `t` into `WidgetProvider`.
{% endstep %}

{% step %}
**Basic setup**

```tsx
import React from 'react';
import { WidgetProvider, createWidgetStore } from '@openg2p/registry-widgets';

const store = createWidgetStore();

const dataSourceRequestHandler = async (
  service: string,
  endpoint: string,
  method: string,
  params: Record<string, any>,
  options?: { headers?: Record<string, string> }
) => {
  // Host implements API calls, auth, and response shaping
  const res = await fetch(`/api/${service}/${endpoint}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
    body: method === 'GET' ? undefined : JSON.stringify(params),
  });
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
};

function App() {
  return (
    <WidgetProvider store={store} dataSourceRequestHandler={dataSourceRequestHandler}>
      {/* Your application */}
    </WidgetProvider>
  );
}

export default App;
```

Default widgets register automatically when the package is imported.
{% endstep %}

{% step %}
**Optional: translation and theme**

```tsx
import { useTranslation } from 'react-i18next';
import { WidgetProvider, createWidgetStore, defaultTheme } from '@openg2p/registry-widgets';

function App() {
  const { t } = useTranslation();
  const store = createWidgetStore();

  return (
    <WidgetProvider store={store} t={t} theme={defaultTheme}>
      {/* … */}
    </WidgetProvider>
  );
}
```
{% endstep %}
{% endstepper %}

## Core concepts

### Widget configuration

Every widget config follows `BaseWidgetConfig`. Required fields:

* `widget` — registered name (e.g. `"text"`, `"select"`, `"geo-hierarchy"`)
* `widget-id` — unique id in the form

Common optional fields: `widget-type`, `widget-label`, `widget-data-path`, `widget-required`, `widget-readonly`, validation, format, data source, options, cascade, column span.

### useBaseWidget hook

Foundation for most widgets:

```tsx
const {
  widgetId,
  value,
  formattedValue,
  error,
  touched,
  loading,
  isVisible,
  isEnabled,
  isRequired,
  onChange,
  onBlur,
  setError,
  getFieldValue,
  dataSourceOptions,
  config,
} = useBaseWidget({ config });
```

### Widget registry

```tsx
import { widgetRegistry } from '@openg2p/registry-widgets';
import { MyCustomWidget } from './MyCustomWidget';

widgetRegistry.register({
  widget: 'my-custom-widget',
  component: MyCustomWidget,
});
```

## Basic usage

### Rendering a single widget

```tsx
import { WidgetRenderer } from '@openg2p/registry-widgets';

const config = {
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'name',
  'widget-label': 'Full Name',
  'widget-data-path': 'person.name',
  'widget-required': true,
};

function MyForm() {
  return <WidgetRenderer config={config} />;
}
```

### Using sections and panels

```tsx
import { SectionsContainer } from '@openg2p/registry-widgets';

const sections = [
  {
    'section-id': 'personal-info',
    'section-title': 'Personal Information',
    'section-editable': true,
    panels: [
      {
        'panel-id': 'name-panel',
        'panel-orientation': 'horizontal',
        widgets: [
          {
            widget: 'text',
            'widget-type': 'input',
            'widget-id': 'firstName',
            'widget-label': 'First Name',
            'widget-data-path': 'person.firstName',
          },
          {
            widget: 'text',
            'widget-type': 'input',
            'widget-id': 'lastName',
            'widget-label': 'Last Name',
            'widget-data-path': 'person.lastName',
          },
        ],
      },
    ],
  },
];

function MyForm() {
  return (
    <SectionsContainer
      sections={sections}
      mode="RegistryView"
      onSectionSave={async (changes) => {
        // Persist section change request / draft
      }}
    />
  );
}
```

## Widget configuration

### Basic configuration properties

```json
{
  "widget": "text",
  "widget-type": "input",
  "widget-id": "uniqueId",
  "widget-label": "Label",
  "widget-data-path": "path.to.value",
  "widget-data-default": "",
  "widget-required": false,
  "widget-readonly": false,
  "widget-data-placeholder": "",
  "widget-data-helptext": "",
  "widget-data-tooltip": "",
  "widget-column-span": 1,
  "widget-data-validation": {},
  "widget-data-format": {},
  "widget-data-source": {},
  "widget-data-options": {},
  "widget-cascade": {}
}
```

### Example: complete text input configuration

```tsx
{
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'email',
  'widget-label': 'Email Address',
  'widget-data-path': 'person.email',
  'widget-required': true,
  'widget-data-placeholder': 'name@example.com',
  'widget-data-validation': {
    required: true,
    validationType: 'email',
    maxLength: 255,
  },
  'widget-data-format': {
    inputType: 'email',
    caseControl: 'lowercase',
  },
}
```

## Data binding

### Single path binding

```json
{ "widget-data-path": "person.firstName" }
```

### Multi-path binding

```json
{
  "widget-data-path": {
    "image": "person.photo",
    "name": "person.displayName",
    "id": "person.nationalId"
  }
}
```

### Accessing data

Values live in the Redux widget store under path keys. `WidgetProvider` hydrates from `schemaData` via `setValues`. Widgets read/write through `useBaseWidget` / path utilities.

### Getting other field values

```tsx
const { getFieldValue } = useBaseWidget({ config });
const country = getFieldValue('person.country');
```

## Validation

### Built-in validation rules

```json
{
  "widget-data-validation": {
    "required": true,
    "minLength": 2,
    "maxLength": 100,
    "min": 0,
    "max": 999,
    "pattern": "^[A-Za-z]+$",
    "patternMessage": "Letters only"
  }
}
```

`pattern` takes precedence over `validationType` when both are set.

### Predefined validation types

* `email`
* `phone`
* `url`

### Zod schema validation

```tsx
import { z } from 'zod';

{
  'widget-data-validation': {
    zodSchema: z.string().email().min(5),
  },
}
```

### Manual validation

Use `setError` from `useBaseWidget`, or `SectionsContainer` form handle methods: `validate()`, `validateAndGetData()`, `getFormData()`, `getStructuredData()`.

## Conditional logic

Actions: `show` | `hide` | `enable` | `disable` | `require`.

### Single rule

```tsx
{
  'widget-data-options': {
    action: 'show',
    condition: {
      field: 'person.maritalStatus',
      operator: 'equals',
      value: 'married',
    },
  },
}
```

### Multiple actions

```tsx
{
  'widget-data-options': {
    actions: [
      {
        action: 'show',
        condition: { field: 'has_national_id', operator: 'equals', value: true },
      },
      {
        action: 'require',
        condition: { field: 'has_national_id', operator: 'equals', value: true },
      },
    ],
  },
}
```

### Operators

* `equals`, `notEquals`
* `notEmpty`, `empty`
* `greaterThan`, `lessThan`
* `contains`, `notContains`

## Data sources

Used by `select`, `multi-select`, `radio`, `checkbox`, and related lookups.

### Static

```tsx
{
  'widget-data-source': {
    type: 'static',
    options: [
      { value: 'pmt', label: 'PMT' },
      { value: 'fs', label: 'Food Security' },
    ],
  },
}
```

### API

```tsx
{
  'widget-data-source': {
    type: 'api',
    service: 'attributes',
    endpoint: 'values',
    method: 'POST',
    params: { attribute_id: 'GENDER' },
    valueKey: 'value_code',
    labelKey: 'value_display',
  },
}
```

### Dependent API (`dependsOn`)

```tsx
{
  'widget-data-source': {
    type: 'api',
    service: 'master-data',
    endpoint: 'get_cities',
    method: 'GET',
    dependsOn: 'person.country',
    valueKey: 'id',
    labelKey: 'name',
  },
}
```

Prefer **`widget-cascade`** when you need clear-on-change / reload-on-change with debounce.

### Schema reference

```tsx
{
  'widget-data-source': {
    type: 'schema',
    path: 'countries',
    valueKey: 'code',
    labelKey: 'name',
  },
}
```

### Geo hierarchy data source

`geo-hierarchy` expects an API data source with `levelsEndpoint` and `valuesEndpoint` (not a plain options list):

```json
{
  "widget-data-source": {
    "type": "api",
    "service": "master-data",
    "method": "POST",
    "levelsEndpoint": "geo-levels",
    "valuesEndpoint": "geo-level-values"
  }
}
```

## Formatting

### Date / datetime

```json
{
  "widget-data-format": {
    "dateFormat": "YYYY-MM-DD",
    "inputMethod": "hybrid",
    "dateConstraint": "past-only"
  }
}
```

```json
{
  "widget-data-format": {
    "dateTimeFormat": "YYYY-MM-DD HH:mm",
    "dateTimeConstraint": "any"
  }
}
```

### Number

```json
{
  "widget-data-format": {
    "numericType": "decimal",
    "decimalPlaces": 2,
    "thousandSeparator": ",",
    "decimalSeparator": ".",
    "roundingMode": "round",
    "allowSigned": false,
    "formatOnBlur": true,
    "textAlign": "right"
  }
}
```

### Text

```json
{
  "widget-data-format": {
    "inputType": "text",
    "characterType": "alphanumeric",
    "caseControl": "uppercase",
    "showCharCounter": true,
    "mask": {
      "pattern": "XXX-XXX-XXXX",
      "type": "static",
      "placeholder": "_"
    }
  }
}
```

### Phone

```json
{
  "widget-data-format": {
    "pattern": "phone"
  }
}
```

### Boolean

```json
{
  "widget-data-format": {
    "booleanControlType": "radio",
    "booleanRepresentation": "yes-no",
    "allowUnset": false
  }
}
```

## Widget cascade

Clear and/or reload a child API data source when parent widgets change:

```json
{
  "widget-cascade": {
    "listenTo": ["country"],
    "onEvent": "widget:change",
    "clearOnChange": true,
    "reloadOnChange": true,
    "debounce": 200
  }
}
```

Events: `widget:change`, `widget:blur`, `widget:focus`, `widget:reload`, `widget:clear`.

## Section modes

Pass `mode` to `SectionsContainer`:

| Mode | Behavior |
| --- | --- |
| `RegistryView` (default) | View sections; optional edit/save per section; `hideEditButton` / `section-hide-edit-button` |
| `CRView` | Change-request review; audit footer from schema/store |
| `IntakeForm` | Accordion sections; `isDraft` controls editability; form handle for full-form validate/submit |

Section config extras:

* `section-editable`
* `section-hide-edit-button`
* `section-column-span`
* `section-supporting-documents` (path, type, accept, max size, required, label)

## Widget reference

**Notes:**

* `widget-data-path` may be a string or a map of keys → paths
* Layout widgets `array-widget`, `iterable-accordion`, and `simple-table` are **not** registered in the current library; use `table` / `dialog-table` for repeating structured rows

### Default widget catalog (22)

`text`, `textarea`, `number`, `boolean`, `date`, `datetime`, `select`, `multi-select`, `radio`, `checkbox`, `file`, `phone`, `display`, `profile`, `table`, `dialog-table`, `header-section`, `scores-display`, `id-authentication`, `register-lookup`, `geo-hierarchy`, `docs`

---

### Input widgets

#### Text Input Widget (`text`)

Single-line text input with masking, character filters, and case control.

**Widget name:** `text` · **Type:** `input`

```json
{
  "widget": "text",
  "widget-type": "input",
  "widget-id": "full_name",
  "widget-label": "Full Name",
  "widget-data-path": "register-id.full_name",
  "widget-required": true,
  "widget-data-placeholder": "Enter full name",
  "widget-data-validation": {
    "required": true,
    "minLength": 2,
    "maxLength": 100
  },
  "widget-data-format": {
    "inputType": "text",
    "characterType": "alphabetic",
    "caseControl": "capitalize",
    "showCharCounter": true
  }
}
```

**Features:** HTML input types, charset filters, masks, char counter.

#### Text Area Widget (`textarea`)

Multi-line text.

```json
{
  "widget": "textarea",
  "widget-type": "input",
  "widget-id": "description",
  "widget-label": "Description",
  "widget-data-path": "product.description",
  "widget-data-format": { "rows": 5, "showCharCounter": true }
}
```

#### Number Input Widget (`number`)

Integers/decimals with separators, rounding, alignment, signed values, format-on-blur.

```json
{
  "widget": "number",
  "widget-type": "input",
  "widget-id": "age",
  "widget-label": "Age",
  "widget-data-path": "person.age",
  "widget-data-format": { "numericType": "integer" },
  "widget-data-validation": { "min": 0, "max": 120 }
}
```

#### Phone Input Widget (`phone`)

```json
{
  "widget": "phone",
  "widget-type": "input",
  "widget-id": "phoneNumber",
  "widget-label": "Phone Number",
  "widget-data-path": "contact.phone",
  "widget-data-format": { "pattern": "phone" },
  "widget-data-validation": { "validationType": "phone", "required": true }
}
```

#### Date Input Widget (`date`)

```json
{
  "widget": "date",
  "widget-type": "input",
  "widget-id": "dob",
  "widget-label": "Date of Birth",
  "widget-data-path": "person.dob",
  "widget-data-default": "today",
  "widget-data-format": {
    "dateFormat": "YYYY-MM-DD",
    "inputMethod": "hybrid",
    "dateConstraint": "past-only"
  },
  "widget-data-options": {
    "minDate": "1900-01-01",
    "maxDateField": "person.enrollmentDate"
  }
}
```

Defaults: `"today"` supported for default value.

#### DateTime Input Widget (`datetime`)

```json
{
  "widget": "datetime",
  "widget-type": "input",
  "widget-id": "appointment",
  "widget-label": "Appointment",
  "widget-data-path": "visit.appointment",
  "widget-data-default": "now",
  "widget-data-format": {
    "dateTimeFormat": "YYYY-MM-DD HH:mm",
    "dateTimeConstraint": "future-only"
  }
}
```

#### File Input Widget (`file`)

Upload with preview and serialization for storage.

```json
{
  "widget": "file",
  "widget-type": "input",
  "widget-id": "attachment",
  "widget-label": "Attachment",
  "widget-data-path": "person.document",
  "widget-data-format": {
    "inputType": "file"
  }
}
```

---

### Selection widgets

#### Select Widget (`select`)

```json
{
  "widget": "select",
  "widget-type": "input",
  "widget-id": "gender",
  "widget-label": "Gender",
  "widget-data-path": "person.gender",
  "widget-data-source": {
    "type": "api",
    "method": "POST",
    "service": "attributes",
    "endpoint": "values",
    "params": { "attribute_id": "GENDER" },
    "labelKey": "value_display",
    "valueKey": "value_code"
  }
}
```

#### Multi Select Widget (`multi-select`)

Stores an **array** of selected values. Searchable dropdown with optional sorted options.

```json
{
  "widget": "multi-select",
  "widget-type": "input",
  "widget-id": "programs",
  "widget-label": "Programs",
  "widget-data-path": "register-id.programs",
  "widget-data-default": [],
  "widget-data-source": {
    "type": "static",
    "options": [
      { "value": "pmt", "label": "PMT" },
      { "value": "fs", "label": "Food Security" }
    ]
  },
  "widget-data-format": { "sortOptions": true }
}
```

#### Radio Widget (`radio`)

```json
{
  "widget": "radio",
  "widget-type": "input",
  "widget-id": "preferredContact",
  "widget-label": "Preferred Contact",
  "widget-data-path": "person.preferredContact",
  "widget-data-source": {
    "type": "static",
    "options": [
      { "value": "email", "label": "Email" },
      { "value": "phone", "label": "Phone" }
    ]
  },
  "widget-data-format": { "layout": "horizontal" }
}
```

#### Checkbox Widget (`checkbox`)

Single boolean or multi-value list depending on data source / usage.

#### Boolean Widget (`boolean`)

```json
{
  "widget": "boolean",
  "widget-type": "input",
  "widget-id": "has_national_id",
  "widget-label": "Do you have National ID?",
  "widget-data-path": "has_national_id",
  "widget-data-format": {
    "booleanControlType": "radio",
    "booleanRepresentation": "yes-no"
  }
}
```

Control types: `checkbox` | `radio` | `toggle`. Representations: `true-false` | `yes-no` | `on-off` | `custom`.

---

### Geo and documents

#### Geo Hierarchy Widget (`geo-hierarchy`)

Cascading location selects (e.g. Region → Zone → Woreda). Persists the deepest selected level value; optional hierarchy JSON for hydration.

```json
{
  "widget": "geo-hierarchy",
  "widget-type": "input",
  "widget-id": "individual_geo_hierarchy",
  "widget-label": "Location Hierarchy",
  "widget-required": true,
  "widget-data-path": {
    "value": "register-id.geo_lowest_level_value_id",
    "hierarchy": "register-id.geo_code_hierarchy_json"
  },
  "widget-data-source": {
    "type": "api",
    "service": "master-data",
    "method": "POST",
    "levelsEndpoint": "geo-levels",
    "valuesEndpoint": "geo-level-values"
  },
  "widget-geo-layout": {
    "distribution": "fixed",
    "columns": [3, 3]
  }
}
```

**Layout:** By default levels fill top-to-bottom across up to 3 columns (`columnSpan` / auto from level count). Optional `widget-geo-layout` forces explicit column counts. Prefer a full-width section (`section-column-span: 3`).

#### Docs Widget (`docs`)

Fixed upload slots in a three-column layout.

```json
{
  "widget": "docs",
  "widget-type": "input",
  "widget-id": "individual_docs",
  "widget-label": "Supporting Documents",
  "widget-data-path": "register-id.supporting_documents",
  "widget-total-docs": 4,
  "documents": [
    {
      "document-key": "national_id_front",
      "document-label": "National ID (Front)",
      "document-required": true,
      "document-accept": ".pdf,.jpg,.jpeg,.png",
      "document-max-size": 5242880
    },
    {
      "document-key": "passport",
      "document-label": "Passport",
      "document-accept": ".pdf,.jpg,.jpeg,.png",
      "document-max-size": 5242880
    }
  ]
}
```

Stored value is an object keyed by `document-key` (serialized file or view URL). `document-accept` and `document-max-size` (bytes) are required per slot.

---

### Display and identity widgets

#### Display Widget (`display`)

Read-only formatted value.

```json
{
  "widget": "display",
  "widget-type": "input",
  "widget-id": "fullName",
  "widget-label": "Full Name",
  "widget-data-path": "person.fullName"
}
```

#### Profile Widget (`profile`)

Identity strip: image, name, id via multi-path binding.

```json
{
  "widget": "profile",
  "widget-type": "group",
  "widget-id": "user_profile",
  "widget-data-path": {
    "image": "register-id.photo",
    "name": "register-id.display_name",
    "id": "register-id.national_id"
  },
  "widget-data-format": {
    "imageSize": 80,
    "nameColor": "#F07B1A",
    "showIdLabel": true
  }
}
```

#### Header Section Widget (`header-section`)

Record summary header: image, name, functional ID, status, completion/ideal scores, audit stamps.

```json
{
  "widget": "header-section",
  "widget-type": "group",
  "widget-id": "registry-header",
  "widget-data-path": {
    "image": "register-id.record_image_storage_id",
    "imageUrl": "register-id.record_image_url",
    "name": "register-id.record_name",
    "functionalId": "register-id.functional_record_id",
    "status": "register-id.record_status",
    "statusReason": "register-id.record_status_reason",
    "completionScore": "register-id.completion_score",
    "idealScore": "register-id.ideal_score",
    "createdBy": "register-id.created_by",
    "createdAt": "register-id.created_at",
    "lastApprovedBy": "register-id.last_approved_by",
    "lastApprovedAt": "register-id.last_approved_at"
  },
  "widget-field-config": {
    "status": {
      "data-source": {
        "type": "static",
        "options": [
          { "value": "active", "label": "Active" },
          { "value": "inactive", "label": "Inactive" },
          { "value": "archived", "label": "Archived" }
        ]
      }
    }
  },
  "widget-data-format": {
    "imageSize": 120,
    "nameColor": "#ED7C22",
    "statusColors": {
      "active": "#16A34A",
      "inactive": "#D97706",
      "archived": "#6B7280"
    }
  }
}
```

#### Scores Display Widget (`scores-display`)

Read-only list of computed scores, newest first.

```json
{
  "widget": "scores-display",
  "widget-type": "group",
  "widget-id": "record-scores",
  "widget-readonly": true,
  "widget-data-path": "scores"
}
```

Expected array items:

```json
{
  "score_type": "PMT",
  "computed_score": 38,
  "computed_at": "2026-04-16T10:12:00Z",
  "triggered_by_cr_id": "CR-2026-004821"
}
```

---

### Domain widgets

#### ID Authentication Widget (`id-authentication`)

Shows authentication status fields and starts a provider login (popup or optional iframe). Uses multi-path binding and `widget-auth-config`.

```json
{
  "widget": "id-authentication",
  "widget-type": "group",
  "widget-id": "id-auth",
  "widget-readonly": true,
  "widget-data-path": {
    "internalRecordId": "register-id.internal_record_id",
    "initiatedByStaffId": "register-id.initiated_by_staff_id",
    "foundationalId": "register-id.foundational_id",
    "lastAuthenticatedOn": "register-id.last_authenticated_on",
    "lastAuthenticationStatus": "register-id.last_authentication_status",
    "expiryDate": "register-id.authentication_expiry_date",
    "authenticationToken": "register-id.psut"
  },
  "widget-auth-config": {
    "service": "registry",
    "providerId": "esignet",
    "providerName": "eSignet",
    "registerId": "<register-uuid>",
    "authenticateEndpoint": "authenticate_registrant",
    "authenticateMethod": "POST",
    "useIframeOverlay": false
  }
}
```

Host typically listens for browser events / `postMessage` success (default type `openg2p:oidc:success`). Optional `reloadOnSuccess`.

#### Register Lookup Widget (`register-lookup`)

Search another register and store the selected record id.

```json
{
  "widget": "register-lookup",
  "widget-type": "input",
  "widget-id": "linked_record",
  "widget-label": "Linked Record",
  "widget-data-path": "source-register-id.link_internal_record_id",
  "widget-data-source": {
    "type": "api",
    "method": "POST",
    "service": "register",
    "endpoint": "records",
    "params": { "register_id": "<target_register_id>" }
  },
  "widget-lookup-config": {
    "page_size": 10,
    "action_label": "Click to Search Record",
    "search_placeholder": "Search by name or ID...",
    "select_record_label": "Select Record"
  }
}
```

---

### Table widgets

#### Table Widget (`table`)

Inline editable table with per-column widget configs and add/remove/edit operations.

```json
{
  "widget": "table",
  "widget-type": "table",
  "widget-id": "table_records",
  "widget-label": "Records",
  "widget-column-span": 3,
  "widget-data-path": "register-id.table_records",
  "widget-data-operations": { "add": true, "remove": true, "edit": true },
  "widget-data-columns": [
    {
      "column-key": "degree",
      "widget": "text",
      "widget-type": "input",
      "widget-label": "Degree"
    },
    {
      "column-key": "year",
      "widget": "number",
      "widget-type": "input",
      "widget-label": "Year",
      "widget-data-validation": { "min": 1900, "max": 2100 }
    }
  ]
}
```

Set `widget-readonly: true` for a static table.

#### Dialog Table Widget (`dialog-table`)

Rows are edited in a modal dialog. Supports `column-group` for dialog field grouping and per-column conditional `actions` evaluated against the current row.

```json
{
  "widget": "dialog-table",
  "widget-type": "table",
  "widget-id": "members_table",
  "widget-label": "Household Member Records",
  "widget-data-path": "register-id.records",
  "widget-data-add-label": "Add Member",
  "widget-data-operations": { "add": true, "edit": true, "remove": true },
  "widget-data-columns": [
    {
      "widget": "boolean",
      "widget-type": "input",
      "widget-id": "has_national_id",
      "column-key": "has_national_id",
      "column-group": "identifier",
      "widget-label": "Do you have National ID?",
      "widget-required": true,
      "widget-data-path": "has_national_id",
      "widget-data-format": {
        "booleanControlType": "radio",
        "booleanRepresentation": "yes-no"
      }
    },
    {
      "widget": "text",
      "widget-type": "input",
      "column-key": "foundational_id",
      "column-group": "identifier",
      "widget-label": "Fayda ID",
      "widget-data-path": "foundational_id",
      "widget-data-options": {
        "actions": [
          {
            "action": "show",
            "condition": { "field": "has_national_id", "value": true, "operator": "equals" }
          },
          {
            "action": "require",
            "condition": { "field": "has_national_id", "value": true, "operator": "equals" }
          }
        ]
      }
    }
  ]
}
```

Row change markers (ADD / UPDATE / DELETE) use theme success/warning/error colors for visual review.

---

### Widget configuration summary

Common properties:

* `widget`, `widget-id` (required)
* `widget-type`: `input` | `layout` | `table` | `group`
* `widget-label`, `widget-data-path`, `widget-data-default`
* `widget-required`, `widget-readonly`, `widget-column-span`
* `widget-data-placeholder`, `widget-data-helptext`, `widget-data-tooltip`
* `widget-data-validation`, `widget-data-format`, `widget-data-source`, `widget-data-options`
* `widget-cascade`
* Table: `widget-data-columns`, `widget-data-operations`, `widget-data-add-label`
* Geo: `widget-geo-layout`, `widget-geo-hierarchy-path`
* Docs: `documents`, `widget-total-docs`
* Auth: `widget-auth-config`
* Lookup: `widget-lookup-config`
* Header: `widget-field-config`

## Creating custom widgets

{% stepper %}
{% step %}
**Create the component**

```tsx
import { useBaseWidget } from '@openg2p/registry-widgets';
import type { BaseWidgetConfig } from '@openg2p/registry-widgets';

export function MyCustomWidget({ config }: { config: BaseWidgetConfig }) {
  const { value, error, touched, isEnabled, isVisible, onChange, onBlur } =
    useBaseWidget({ config });

  if (!isVisible) return null;

  return (
    <div>
      <label>{config['widget-label']}</label>
      <input
        value={value ?? ''}
        disabled={!isEnabled}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
      />
      {touched && error?.length > 0 && <span>{error[0]}</span>}
    </div>
  );
}
```
{% endstep %}

{% step %}
**Register it**

```tsx
import { widgetRegistry } from '@openg2p/registry-widgets';
import { MyCustomWidget } from './MyCustomWidget';

widgetRegistry.register({
  widget: 'my-custom-widget',
  component: MyCustomWidget,
});
```
{% endstep %}

{% step %}
**Use it in a schema**

```json
{
  "widget": "my-custom-widget",
  "widget-type": "input",
  "widget-id": "customField",
  "widget-label": "Custom Field",
  "widget-data-path": "person.custom"
}
```
{% endstep %}
{% endstepper %}

Prefer `useBaseWidget` so validation, conditions, data sources, and Redux stay consistent.

## Advanced patterns

### Intake form with form handle

```tsx
<SectionsContainer
  sections={sections}
  mode="IntakeForm"
  isDraft={true}
  onFormReady={(handle) => {
    // handle.validate(), handle.validateAndGetData(), handle.getStructuredData()
  }}
  onSectionSave={async (changes) => { /* save section */ }}
/>
```

### Dynamic form generation

Map a server field list to `BaseWidgetConfig[]` and place them under panels/sections. Keep `widget-id` and `widget-data-path` stable across regenerations.

### Section-level change tracking

`onSectionSave` receives structured `SectionChanges` (old/new values) suitable for change-request payloads.

### Section builder

Use `SectionBuilder` / `VisualBuilderPanel` / `JSONEditorPanel` during development to edit schemas visually and as JSON.

## Internationalization

i18n is **host-provided**. There is no built-in `initI18n` in the current package.

### Pass `t` to WidgetProvider

```tsx
const { t } = useTranslation();

<WidgetProvider store={store} t={t}>
  <SectionsContainer sections={translatedSections} />
</WidgetProvider>
```

### Translate schemas programmatically

```tsx
import { translateUISchema } from '@openg2p/registry-widgets';

const translated = translateUISchema(uiSchema, t);
```

Also available: `translateWidgetConfig`, `translatePanelConfig`. Keys that look like translation keys (contain `.` or `:`) are passed through `t` with fallback to the original string.

Widgets that receive `t` via context use helpers such as `tSchema` for labels and option text at render time.

## Theming

```tsx
import { WidgetProvider, defaultTheme } from '@openg2p/registry-widgets';

<WidgetProvider
  theme={{
    ...defaultTheme,
    colors: { ...defaultTheme.colors, primary: '#0B5FFF' },
  }}
>
  {/* … */}
</WidgetProvider>
```

Theme tokens cover colors, section, panel, button, and widget chrome (including table states). They are applied as CSS variables on the provider root.

## Best practices

### Widget IDs

Use stable, unique ids (`person-first-name`). Avoid regenerating ids on every render.

### Data paths

Prefer clear namespaces (`register-id.full_name`). Align multi-path keys with what each widget documents (`profile`, `header-section`, `geo-hierarchy`, `id-authentication`).

### Validation

Put shared rules in `widget-data-validation`. Use Zod for cross-field or complex rules. Call section/form validate before submit.

### Conditional logic

Prefer `actions` arrays when a field must both show and require. Keep condition `field` paths aligned with store paths.

### Data sources

Always provide `dataSourceRequestHandler` in production. Prefer `service` + `endpoint` over deprecated `url`. Use cascade for parent/child selects.

### Performance

Keep section schemas reasonable in size. Use section-level edit instead of editing the entire registry at once. Avoid unnecessary `schemaData` object identity changes.

### Type safety

Type configs with `BaseWidgetConfig`, `SectionConfig`, `UISchema`, and `SectionMode`.

## Troubleshooting

### Widget not rendering

* Confirm the widget name is registered (`widgetRegistry` / default list)
* Ensure the package import ran (defaults register on import)
* Check `isVisible` / conditional hide rules

### Validation not working

* Set `widget-required` and/or `widget-data-validation.required`
* Ensure blur/change fired (`touched`)
* For Zod, pass a real schema instance (not JSON)

### API data source not loading

* Provide `dataSourceRequestHandler` on `WidgetProvider` or `SectionsContainer`
* Verify `service`, `endpoint`, method, and `valueKey` / `labelKey`
* Check browser network/console for host handler errors

### Conditional logic not working

* Confirm `field` path matches stored values
* Use `actions` when multiple rules are needed
* Remember dialog-table conditions evaluate against the **row** context

### Geo hierarchy empty

* Confirm handler implements `levelsEndpoint` and `valuesEndpoint` responses
* Ensure hierarchy path is present for edit hydration
* Check required flag on the first level

### TypeScript errors

* Import types from `@openg2p/registry-widgets`
* Align Zod peer major version with the package (`zod` ^4)

## Conclusion

`@openg2p/registry-widgets` provides a schema-driven form system tailored to OpenG2P registry workflows: section modes for view/intake/CR review, twenty-two default widgets spanning inputs through geo hierarchy, documents, lookup, and ID authentication, plus host-owned APIs, theming, and translation. Use this reference alongside the overview document for architecture context, and the `example-ui-schema` folder in the package for copy-paste configs.

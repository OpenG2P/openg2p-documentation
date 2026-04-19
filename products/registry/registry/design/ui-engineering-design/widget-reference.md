# Widget Reference

A practical, widget-by-widget reference for `@openg2p/registry-widgets` showing how to build dynamic forms from JSON configs. Covers widget configuration fields, data binding via `widget-data-path`, validation and formatting, conditional show/hide and enable/disable logic, static and API data sources, section/panel layout rendering in `RegistryView`/`CRView`/`IntakeForm` modes, theming and i18n, and how to extend the library by registering custom widgets.

## Table of contents

1. [Introduction](widget-reference.md#introduction)
2. [Installation and setup](widget-reference.md#installation-and-setup)
3. [Core concepts](widget-reference.md#core-concepts)
4. [Basic usage](widget-reference.md#basic-usage)
5. [Widget configuration](widget-reference.md#widget-configuration)
6. [Data binding](widget-reference.md#data-binding)
7. [Validation](widget-reference.md#validation)
8. [Conditional logic](widget-reference.md#conditional-logic)
9. [Data sources](widget-reference.md#data-sources)
10. [Formatting](widget-reference.md#formatting)
11. [Widget reference](widget-reference.md#widget-reference)
12. [Creating custom widgets](widget-reference.md#creating-custom-widgets)
13. [Advanced patterns](widget-reference.md#advanced-patterns)
14. [Internationalization](widget-reference.md#internationalization)
15. [Best practices](widget-reference.md#best-practices)
16. [Troubleshooting](widget-reference.md#troubleshooting)

## Introduction

The OpenG2P Registry UI Widgets library is a powerful, extensible React component library designed for building dynamic forms from JSON configurations. It provides:

* **20 Pre-built Widgets** for common form inputs (including `header-section` and `scores-display`)
* **Redux-based State Management** for centralized form state
* **Flexible Data Binding** with dot-notation paths
* **Comprehensive Validation** with built-in rules and Zod schemas
* **Conditional Logic** for dynamic form behavior
* **Multiple Data Sources** (static, API, schema references)
* **Internationalization** support
* **Extensible Architecture** for custom widgets

## Installation and setup

{% stepper %}
{% step %}
#### Install the package

```bash
npm install @openg2p/registry-widgets
```
{% endstep %}

{% step %}
#### Install peer dependencies

```bash
npm install react react-dom @reduxjs/toolkit react-redux zod i18next react-i18next
```
{% endstep %}

{% step %}
#### Basic setup

Create a Redux store and wrap your application with `WidgetProvider`:

```tsx
import React from 'react';
import { WidgetProvider, createWidgetStore } from '@openg2p/registry-widgets';

// Create the Redux store
const store = createWidgetStore();

function App() {
  return (
    <WidgetProvider store={store}>
      {/* Your application components */}
    </WidgetProvider>
  );
}

export default App;
```
{% endstep %}

{% step %}
#### Initialize i18n (optional but recommended)

```tsx
import { initI18n } from '@openg2p/registry-widgets';

// Initialize i18n with your language resources
await initI18n({
  lng: 'en',
  resources: {
    en: {
      translation: {
        // Your translation keys
      }
    }
  }
});
```
{% endstep %}
{% endstepper %}

## Core concepts

### Widget configuration

Widgets are configured using JSON objects that follow the `BaseWidgetConfig` interface. Every widget requires:

* `widget`: The widget name/type (e.g., `"text"`, `"select"`, `"date"`)
* `widget-id`: A unique identifier for the widget
* `widget-type`: The type category (`"input"`, `"layout"`, `"table"`, `"group"`)

### useBaseWidget Hook

The `useBaseWidget` hook is the foundation of every widget. It provides:

```tsx
const {
  widgetId,           // Widget ID
  value,              // Current value
  formattedValue,     // Formatted value (if format config exists)
  error,              // Array of error messages
  touched,            // Whether field has been touched
  loading,            // Loading state (for API data sources)
  isVisible,          // Whether widget should be visible
  isEnabled,          // Whether widget should be enabled
  onChange,           // Function to update value
  onBlur,             // Function to handle blur
  setError,           // Function to manually set errors
  getFieldValue,      // Helper to get other field values
  dataSourceOptions,  // Options for select/dropdown widgets
  config,             // Full widget config
} = useBaseWidget({ config });
```

### Widget registry

The widget registry is a plugin system that maps widget names to React components. Widgets must be registered before use:

```tsx
import { widgetRegistry } from '@openg2p/registry-widgets';
import { MyCustomWidget } from './MyCustomWidget';

widgetRegistry.register({
  widget: 'my-custom-widget',
  component: MyCustomWidget,
});
```

The library automatically registers all default widgets when imported.

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

### Rendering multiple widgets with layout

```tsx
const formConfig = {
  widget: 'vertical-layout',
  'widget-type': 'layout',
  widgets: [
    {
      widget: 'text',
      'widget-type': 'input',
      'widget-id': 'firstName',
      'widget-label': 'First Name',
      'widget-data-path': 'person.firstName',
      'widget-required': true,
    },
    {
      widget: 'text',
      'widget-type': 'input',
      'widget-id': 'lastName',
      'widget-label': 'Last Name',
      'widget-data-path': 'person.lastName',
      'widget-required': true,
    },
    {
      widget: 'email',
      'widget-type': 'input',
      'widget-id': 'email',
      'widget-label': 'Email Address',
      'widget-data-path': 'person.email',
      'widget-required': true,
    },
  ],
};

function MyForm() {
  return <WidgetRenderer config={formConfig} />;
}
```

### Using sections and panels

For complex forms, use the sections-based structure:

```tsx
import { SectionsContainer } from '@openg2p/registry-widgets';

const uiSchema = {
  sections: [
    {
      'section-id': 'personal-info',
      'section-title': 'Personal Information',
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
  ],
};

function MyForm() {
  // Note: in this codebase, `SectionsContainer` expects `sections` (array), not `schema`.
  return <SectionsContainer sections={uiSchema.sections} />;
}
```

## Widget Configuration

### Basic configuration properties

```json
{
  "widget": "text",                    // Widget name/type (required)
  "widget-type": "input",              // Optional: "input" | "layout" | "table" | "group"
  "widget-id": "fieldId",              // Unique identifier (required)
  "widget-label": "Field Label",        // Optional: Display label
  "widget-data-path": "person.name",   // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",           // Optional: Default value (type depends on widget)
  "widget-required": false,            // Optional: Required field
  "widget-readonly": false,            // Optional: Read-only field
  "widget-data-placeholder": "",       // Optional: Placeholder text
  "widget-data-helptext": "",          // Optional: Help text
  "widget-data-tooltip": ""            // Optional: Tooltip text
}
```

**Data path examples:**

* Single path: `"widget-data-path": "person.name"`
* Multi-path: `"widget-data-path": { "firstName": "person.fname", "lastName": "person.lname" }`

### Example: complete text input configuration

```tsx
const textInputConfig = {
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'username',
  'widget-label': 'Username',
  'widget-data-path': 'user.username',
  'widget-data-default': '',
  'widget-required': true,
  'widget-readonly': false,
  'widget-data-placeholder': 'Enter your username',
  'widget-data-helptext': 'Username must be 3-20 characters',
  'widget-data-tooltip': 'This will be your login username',
  'widget-data-validation': {
    required: true,
    minLength: 3,
    maxLength: 20,
    pattern: '^[a-zA-Z0-9_]+$',
    patternMessage: 'Only letters, numbers, and underscores allowed',
  },
  'widget-data-format': {
    inputType: 'text',
    characterType: 'alphanumeric',
    caseControl: 'lowercase',
    showCharCounter: true,
  },
};
```

## Data binding

### Single path binding

Bind a widget to a single data path:

```tsx
{
  'widget-data-path': 'person.name'
}
```

This binds the widget to `data.person.name`.

### Multi-path binding

Bind a widget to multiple data paths (useful for complex widgets):

```tsx
{
  'widget-data-path': {
    firstName: 'person.firstName',
    lastName: 'person.lastName',
    email: 'person.email'
  }
}
```

The widget receives an object with these properties.

### Accessing data

The `useBaseWidget` hook automatically handles data binding. The `value` property contains the bound data:

```tsx
const { value } = useBaseWidget({ config });

// For single path: value is the direct value
// For multi-path: value is an object with the specified keys
```

### Getting other field values

Use `getFieldValue` to access other widget values:

```tsx
const { getFieldValue } = useBaseWidget({ config });

const email = getFieldValue('person.email');
const age = getFieldValue('person.age');
```

## Validation

### Built-in validation rules

```tsx
{
  'widget-data-validation': {
    required: true,              // Field is required
    minLength: 5,               // Minimum length
    maxLength: 100,             // Maximum length
    min: 0,                     // Minimum value (for numbers)
    max: 100,                   // Maximum value (for numbers)
    pattern: '^[a-z0-9]+$',     // Regex pattern
    patternMessage: 'Custom error message',
  }
}
```

### Predefined validation types

```tsx
{
  'widget-data-validation': {
    validationType: 'email',  // 'email', 'phone', or 'url'
  }
}
```

### Custom regex patterns

```tsx
{
  'widget-data-validation': {
    pattern: '^[A-Z]{2}[0-9]{6}$',  // Example: Country code + ID
    patternMessage: 'Must be 2 letters followed by 6 digits',
  }
}
```

### Zod schema validation

For complex validation logic, use Zod schemas:

```tsx
import { z } from 'zod';

const emailSchema = z.string().email().min(5).max(100);

{
  'widget-data-validation': {
    zodSchema: emailSchema,
  }
}
```

### Validation example: email with custom rules

```tsx
import { z } from 'zod';

const emailValidation = z
  .string()
  .email('Invalid email format')
  .min(5, 'Email must be at least 5 characters')
  .max(100, 'Email must be less than 100 characters')
  .refine(
    (email) => email.endsWith('@company.com'),
    'Email must be from company.com domain'
  );

const config = {
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'email',
  'widget-label': 'Email',
  'widget-data-path': 'user.email',
  'widget-data-validation': {
    zodSchema: emailValidation,
  },
};
```

### Manual validation

You can manually set errors:

```tsx
const { setError, value } = useBaseWidget({ config });

const validateCustom = () => {
  if (value && value.length < 5) {
    setError(['Value must be at least 5 characters']);
  } else {
    setError([]);
  }
};
```

## Conditional Logic

### Show/hide widgets

Show or hide widgets based on other field values:

```tsx
{
  'widget-data-options': {
    action: 'show',  // or 'hide'
    condition: {
      field: 'person.maritalStatus',
      operator: 'equals',
      value: 'married'
    }
  }
}
```

### Enable/disable widgets

Enable or disable widgets based on conditions:

```tsx
{
  'widget-data-options': {
    action: 'enable',  // or 'disable'
    condition: {
      field: 'person.age',
      operator: 'greaterThan',
      value: 18
    }
  }
}
```

### Available operators

* `equals` - Field equals value
* `notEquals` - Field does not equal value
* `notEmpty` - Field is not empty
* `empty` - Field is empty
* `greaterThan` - Field is greater than value
* `lessThan` - Field is less than value
* `contains` - Field contains value (for strings/arrays)
* `notContains` - Field does not contain value

### Complex conditional example

```tsx
// Show spouse name field only if marital status is "married"
const spouseNameConfig = {
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'spouseName',
  'widget-label': 'Spouse Name',
  'widget-data-path': 'person.spouseName',
  'widget-data-options': {
    action: 'show',
    condition: {
      field: 'person.maritalStatus',
      operator: 'equals',
      value: 'married'
    }
  }
};

// Enable submit button only if all required fields are filled
const submitButtonConfig = {
  widget: 'button',
  'widget-type': 'input',
  'widget-id': 'submit',
  'widget-label': 'Submit',
  'widget-data-options': {
    action: 'enable',
    condition: {
      field: 'person.email',
      operator: 'notEmpty'
    }
  }
};
```

## Data sources

Data sources provide options for select, radio, and checkbox widgets.

### Static data source

Pre-defined option arrays:

```tsx
{
  'widget-data-source': {
    type: 'static',
    options: [
      { value: 'us', label: 'United States' },
      { value: 'uk', label: 'United Kingdom' },
      { value: 'ca', label: 'Canada' },
    ]
  }
}
```

### API Data Source

Load options from a REST API:

```tsx
{
  'widget-data-source': {
    type: 'api',
    service: 'master-data',
    endpoint: 'get_countries',
    method: 'GET',
    valueKey: 'id',      // Key for value in response
    labelKey: 'name',    // Key for label in response
    params: {
      // Optional static params merged into the request
    },
    headers: {
      'Authorization': 'Bearer token'
    }
  }
}
```

### Dependent API data source

Load options based on another field's value:

```tsx
{
  'widget-data-source': {
    type: 'api',
    service: 'master-data',
    endpoint: 'get_cities',
    method: 'GET',
    dependsOn: 'person.country',  // Reload when this field changes (data-path or widget-id)
    valueKey: 'id',
    labelKey: 'name',
  }
}
```

### Schema reference data source

Reference data from your schema:

```tsx
// In WidgetProvider
<WidgetProvider schemaData={{ countries: [...] }}>

// In widget config
{
  'widget-data-source': {
    type: 'schema',
    path: 'countries',
    valueKey: 'code',
    labelKey: 'name',
  }
}
```

### API handler setup (host integration)

Provide a `dataSourceRequestHandler` for API data sources. Widgets call this handler with `(service, endpoint, method, params, options)` and expect the host to return response data.

```tsx
const dataSourceRequestHandler = async (
  service: string,
  endpoint: string,
  method: string,
  params: Record<string, any>,
  options?: { headers?: Record<string, string> }
) => {
  // Host decides how "service" maps to a base URL / client
  // and how "endpoint" maps to a path or operation.
  const response = await fetch(`/api/${service}/${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    body: method === 'GET' ? undefined : JSON.stringify(params),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
};

<WidgetProvider store={store} dataSourceRequestHandler={dataSourceRequestHandler}>
  {/* Your app */}
</WidgetProvider>
```

## Formatting

### Date formatting

```tsx
{
  'widget-data-format': {
    dateFormat: 'YYYY-MM-DD',
    inputMethod: 'picker',  // 'picker', 'manual', or 'hybrid'
    dateConstraint: 'past-only',  // 'any', 'past-only', or 'future-only'
  }
}
```

### Currency formatting

```tsx
{
  'widget-data-format': {
    currency: 'USD',
    locale: 'en-US',
    decimals: 2,
  }
}
```

### Number formatting

```tsx
{
  'widget-data-format': {
    numericType: 'decimal',      // 'integer' or 'decimal'
    decimalPlaces: 2,
    roundingMode: 'round',       // 'round' or 'truncate'
    thousandSeparator: ',',
    decimalSeparator: '.',
    textAlign: 'right',
    allowSigned: true,
    formatOnBlur: true,
  }
}
```

### Text formatting

```tsx
{
  'widget-data-format': {
    inputType: 'text',           // 'text', 'email', 'password', etc.
    characterType: 'alphanumeric', // 'any', 'alphabetic', 'alphanumeric', 'numeric', 'numeric-decimal', 'custom'
    caseControl: 'lowercase',     // 'none', 'lowercase', 'uppercase', 'capitalize'
    mask: {
      pattern: 'XXX-XXX-XXXX',
      type: 'static',            // 'static', 'phone', 'national-id', 'custom'
      placeholder: '_',
    },
    showCharCounter: true,
  }
}
```

### Phone number formatting

```tsx
{
  widget: 'phone',
  'widget-type': 'input',
  'widget-id': 'phone',
  'widget-label': 'Phone Number',
  'widget-data-path': 'person.phone',
  'widget-data-format': {
    pattern: 'phone',  // Automatic phone formatting
  }
}
```

## Widget reference

This section provides detailed documentation for each widget available in the library. Each widget includes configuration options, usage examples, and special features.

**Note on Configuration:**

* `widget-data-path` can be:
  * **Single path** (string): `"widget-data-path": "person.name"`
  * **Multi-path** (object): `"widget-data-path": { "firstName": "person.fname", "lastName": "person.lname" }`
* `widget-data-default` accepts different types depending on the widget:
  * Text/TextArea/Phone: string (e.g., `"default value"`)
  * Number/Currency: number (e.g., `0` or `100.50`)
  * Boolean: boolean (e.g., `true` or `false`)
  * Date: string in ISO format (e.g., `"2024-01-15"`) or `"today"`
  * DateTime: string in ISO format (e.g., `"2024-01-15T10:30:00"`) or `"now"`
  * Select/Radio: string or number matching option values (e.g., `"option1"` or `1`)
  * Checkbox (single): boolean (e.g., `false`)
  * Checkbox (multiple): array of strings (e.g., `["sports", "music"]`)
  * Array/Table: array of values (e.g., `[]` or `["item1", "item2"]`)

### Input widgets

#### Text Input Widget (`text`)

A versatile text input widget supporting various input types and advanced formatting options.

**Widget name:** `text`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "text",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Field Label",          // Optional: Display label
  "widget-data-path": "person.name",      // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",              // Optional: Default value (string for text widgets)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "",          // Optional: Placeholder text
  "widget-data-helptext": "",             // Optional: Help text
  "widget-data-tooltip": "",              // Optional: Tooltip text
  "widget-data-validation": {            // Optional: Validation rules
    "required": false,
    "minLength": 0,
    "maxLength": 100,
    "pattern": "^[a-z]+$",
    "patternMessage": "Custom error message",
    "validationType": "email"            // "email" | "phone" | "url"
  },
  "widget-data-format": {                // Optional: Formatting options
    "inputType": "text",                 // "text" | "email" | "password" | "number" | "tel" | "url" | "search" | "file"
    "characterType": "any",              // "any" | "alphabetic" | "alphanumeric" | "numeric" | "numeric-decimal" | "custom"
    "customCharset": "[a-z0-9]",        // Regex pattern for custom character type
    "caseControl": "none",               // "none" | "lowercase" | "uppercase" | "capitalize"
    "mask": {
      "pattern": "XXX-XXX-XXXX",         // Mask pattern
      "type": "static",                  // "static" | "phone" | "national-id" | "custom"
      "placeholder": "_"                 // Placeholder character (default: "_")
    },
    "showCharCounter": false             // Show live character counter
  }
}
```

**Basic example:**

```tsx
{
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'username',
  'widget-label': 'Username',
  'widget-data-path': 'user.username',
  'widget-required': true,
  'widget-data-placeholder': 'Enter your username',
}
```

**Advanced Example with Formatting:**

```tsx
{
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'phone',
  'widget-label': 'Phone Number',
  'widget-data-path': 'contact.phone',
  'widget-data-format': {
    inputType: 'tel',
    mask: {
      pattern: 'XXX-XXX-XXXX',
      type: 'phone',
    },
    characterType: 'numeric',
  },
  'widget-data-validation': {
    validationType: 'phone',
    minLength: 10,
    maxLength: 15,
  },
}
```

**Email input example:**

```tsx
{
  widget: 'text',
  'widget-type': 'input',
  'widget-id': 'email',
  'widget-label': 'Email Address',
  'widget-data-path': 'user.email',
  'widget-data-format': {
    inputType: 'email',
    caseControl: 'lowercase',
  },
  'widget-data-validation': {
    validationType: 'email',
    required: true,
  },
}
```

**Special features:**

* Character type filtering (alphabetic, alphanumeric, numeric, etc.)
* Case transformation (lowercase, uppercase, capitalize)
* Input masking for phone numbers, IDs, etc.
* Live character counter
* Multiple HTML input types

#### Text Area Widget (`textarea`)

Multi-line text input widget for longer text content.

**Widget name:** `textarea`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "textarea",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Description",          // Optional: Display label
  "widget-data-path": "person.description", // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",              // Optional: Default value (string for textarea)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "",          // Optional: Placeholder text
  "widget-data-validation": {            // Optional: Validation rules
    "required": false,
    "minLength": 0,
    "maxLength": 500,
    "pattern": "^[a-z]+$",
    "patternMessage": "Custom error message"
  },
  "widget-data-format": {                // Optional: Formatting options
    "characterType": "any",              // "any" | "alphabetic" | "alphanumeric" | "numeric" | "custom"
    "caseControl": "none",               // "none" | "lowercase" | "uppercase" | "capitalize"
    "showCharCounter": false,            // Show live character counter
    "rows": 2                             // Number of rows (default: 2)
  }
}
```

**Example:**

```tsx
{
  widget: 'textarea',
  'widget-type': 'input',
  'widget-id': 'description',
  'widget-label': 'Description',
  'widget-data-path': 'product.description',
  'widget-data-format': {
    rows: 5,
    showCharCounter: true,
  },
  'widget-data-validation': {
    minLength: 10,
    maxLength: 500,
  },
  'widget-required': true,
}
```

**Special features:**

* Configurable number of rows (default: 2)
* Character counter support
* Same character filtering and case control as text input

#### Number Input Widget (`number`)

Numeric input widget with decimal precision, formatting, and range validation.

**Widget name:** `number`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "number",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Amount",                // Optional: Display label
  "widget-data-path": "transaction.amount", // Optional: Single path (string) or multi-path (object)
  "widget-data-default": 0,               // Optional: Default value (number for number widgets)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "",          // Optional: Placeholder text
  "widget-data-validation": {             // Optional: Validation rules
    "required": false,
    "min": 0,
    "max": 10000,
    "pattern": "^[0-9]+(\\.[0-9]{1,2})?$",
    "patternMessage": "Invalid number format"
  },
  "widget-data-format": {                // Optional: Formatting options
    "numericType": "decimal",            // "integer" | "decimal" (default: "decimal")
    "decimalPlaces": 2,                   // 0-6 (default: 0 for integer, 2 for decimal)
    "roundingMode": "round",              // "round" | "truncate" (default: "round")
    "thousandSeparator": ",",             // Thousand separator (default: ",")
    "decimalSeparator": ".",              // Decimal separator (default: ".")
    "textAlign": "right",                 // "left" | "right" (default: "right")
    "allowSigned": true,                  // Allow negative numbers (default: true)
    "formatOnBlur": true                  // Apply formatting on blur (default: true)
  }
}
```

**Integer example:**

```tsx
{
  widget: 'number',
  'widget-type': 'input',
  'widget-id': 'age',
  'widget-label': 'Age',
  'widget-data-path': 'person.age',
  'widget-data-format': {
    numericType: 'integer',
    allowSigned: false,
  },
  'widget-data-validation': {
    min: 0,
    max: 120,
  },
}
```

**Currency example:**

```tsx
{
  widget: 'number',
  'widget-type': 'input',
  'widget-id': 'price',
  'widget-label': 'Price',
  'widget-data-path': 'product.price',
  'widget-data-format': {
    numericType: 'decimal',
    decimalPlaces: 2,
    thousandSeparator: ',',
    decimalSeparator: '.',
    formatOnBlur: true,
  },
  'widget-data-validation': {
    min: 0,
  },
}
```

**Special features:**

* Integer or decimal number support
* Configurable decimal precision (0-6 places)
* Rounding or truncation modes
* Thousand and decimal separators
* Right-aligned by default (configurable)
* Format on blur option

#### Currency Input Widget (`currency`)

Specialized widget for currency input with automatic formatting.

**Widget name:** `currency`\
**Widget type:** `input`

**Configuration options:**

Similar to Number Input Widget, but optimized for currency values.

**Example:**

```tsx
{
  widget: 'currency',
  'widget-type': 'input',
  'widget-id': 'amount',
  'widget-label': 'Amount',
  'widget-data-path': 'transaction.amount',
  'widget-data-format': {
    currency: 'USD',
    locale: 'en-US',
    decimals: 2,
  },
  'widget-data-validation': {
    min: 0,
  },
}
```

#### Phone Input Widget (`phone`)

Specialized widget for phone number input with automatic formatting.

**Widget name:** `phone`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "phone",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Phone Number",         // Optional: Display label
  "widget-data-path": "contact.phone",    // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",              // Optional: Default value (string for phone widgets)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "",          // Optional: Placeholder text
  "widget-data-validation": {             // Optional: Validation rules
    "required": false,
    "validationType": "phone",
    "pattern": "^[0-9]{10}$",
    "patternMessage": "Invalid phone number"
  },
  "widget-data-format": {                // Optional: Formatting options
    "pattern": "phone"                    // Automatic phone formatting
  }
}
```

**Example:**

```tsx
{
  widget: 'phone',
  'widget-type': 'input',
  'widget-id': 'phoneNumber',
  'widget-label': 'Phone Number',
  'widget-data-path': 'contact.phone',
  'widget-data-format': {
    pattern: 'phone',
  },
  'widget-data-validation': {
    validationType: 'phone',
    required: true,
  },
}
```

#### Date Input Widget (`date`)

Date input widget with picker support and date constraints.

**Widget name:** `date`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "date",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Date of Birth",        // Optional: Display label
  "widget-data-path": "person.dob",       // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "today",          // Optional: ISO date string (e.g., "2024-01-15") or "today"
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "DD/MM/YYYY", // Optional: Placeholder text
  "widget-data-validation": {            // Optional: Validation rules
    "required": false
  },
  "widget-data-format": {                // Optional: Formatting options
    "dateFormat": "YYYY-MM-DD",          // Date format (e.g., "YYYY-MM-DD", "DD/MM/YYYY")
    "inputMethod": "picker",             // "picker" | "manual" | "hybrid" (default: "picker")
    "dateConstraint": "any"               // "any" | "past-only" | "future-only" (default: "any")
  },
  "widget-data-options": {               // Optional: Widget-specific options
    "minDate": "1900-01-01",             // ISO date string or "today"
    "maxDate": "today"                    // ISO date string or "today"
  }
}
```

**Date of birth example:**

```tsx
{
  widget: 'date',
  'widget-type': 'input',
  'widget-id': 'dateOfBirth',
  'widget-label': 'Date of Birth',
  'widget-data-path': 'person.dob',
  'widget-data-format': {
    dateFormat: 'DD/MM/YYYY',
    inputMethod: 'hybrid',
    dateConstraint: 'past-only',
  },
  'widget-data-options': {
    minDate: '1900-01-01',
    maxDate: 'today',
  },
  'widget-required': true,
}
```

**Special features:**

* Multiple date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
* Date picker, manual input, or hybrid mode
* Date constraints (past-only, future-only)
* Min/max date validation
* Default to today option

#### DateTime Input Widget (`datetime`)

Date and time input widget with picker support.

**Widget name:** `datetime`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "datetime",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Appointment Time",     // Optional: Display label
  "widget-data-path": "appointment.time", // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "now",           // Optional: ISO datetime string (e.g., "2024-01-15T10:30:00") or "now"
  "widget-required": false,              // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-placeholder": "",         // Optional: Placeholder text
  "widget-data-format": {                // Optional: Formatting options
    "dateTimeFormat": "YYYY-MM-DDTHH:mm", // DateTime format (default: "YYYY-MM-DDTHH:mm")
    "inputMethod": "picker",             // "picker" | "manual" | "hybrid"
    "dateTimeConstraint": "any"          // "any" | "past-only" | "future-only"
  }
}
```

**Example:**

```tsx
{
  widget: 'datetime',
  'widget-type': 'input',
  'widget-id': 'appointmentTime',
  'widget-label': 'Appointment Time',
  'widget-data-path': 'appointment.time',
  'widget-data-format': {
    dateTimeFormat: 'YYYY-MM-DDTHH:mm',
    inputMethod: 'picker',
    dateTimeConstraint: 'future-only',
  },
  'widget-required': true,
}
```

#### File Input Widget (`file`)

File upload widget with preview support and file validation.

**Widget name:** `file`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "file",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Upload Document",      // Optional: Display label
  "widget-data-path": "form.document",    // Optional: Single path (string) or multi-path (object)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-options": {               // Optional: File upload options
    "accept": ".pdf,.doc,.docx",          // File types (e.g., ".pdf,.doc,.docx" or "image/*")
    "multiple": false,                    // Allow multiple files (default: false)
    "maxSize": 5242880                    // Maximum file size in bytes (e.g., 5242880 = 5MB)
  }
}
```

**Single file example:**

```tsx
{
  widget: 'file',
  'widget-type': 'input',
  'widget-id': 'resume',
  'widget-label': 'Upload Resume',
  'widget-data-path': 'application.resume',
  'widget-data-options': {
    accept: '.pdf,.doc,.docx',
    multiple: false,
    maxSize: 5242880,                    // 5MB
  },
  'widget-required': true,
}
```

**Multiple files example:**

```tsx
{
  widget: 'file',
  'widget-type': 'input',
  'widget-id': 'photos',
  'widget-label': 'Upload Photos',
  'widget-data-path': 'gallery.photos',
  'widget-data-options': {
    accept: 'image/*',
    multiple: true,
    maxSize: 10485760,                   // 10MB per file
  },
}
```

**Special features:**

* Single or multiple file upload
* File type restrictions via accept attribute
* File size validation
* File preview for images and PDFs
* File serialization for Redux store

### Selection widgets

#### Select Widget (`select`)

Dropdown/select widget with data source support.

**Widget name:** `select`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "select",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Country",              // Optional: Display label
  "widget-data-path": "address.country",  // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",               // Optional: Default value (string or number matching option values)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-source": {                 // Required: Data source configuration
    "type": "static",                     // "static" | "api" | "schema"
    "options": [                          // For static type
      { "value": "us", "label": "United States" },
      { "value": "uk", "label": "United Kingdom" }
    ]
    // For API type: "url", "method", "valueKey", "labelKey", etc.
    // For schema type: "path", "valueKey", "labelKey"
  },
  "widget-data-format": {                // Optional: Formatting options
    "sortOptions": false                  // Sort options alphabetically
  }
}
```

**Static options example:**

```tsx
{
  widget: 'select',
  'widget-type': 'input',
  'widget-id': 'country',
  'widget-label': 'Country',
  'widget-data-path': 'address.country',
  'widget-data-source': {
    type: 'static',
    options: [
      { value: 'us', label: 'United States' },
      { value: 'uk', label: 'United Kingdom' },
      { value: 'ca', label: 'Canada' },
    ],
  },
  'widget-required': true,
}
```

**API data source example:**

```tsx
{
  widget: 'select',
  'widget-type': 'input',
  'widget-id': 'city',
  'widget-label': 'City',
  'widget-data-path': 'address.city',
  'widget-data-source': {
    type: 'api',
    service: 'master-data',
    endpoint: 'get_cities',
    method: 'GET',
    dependsOn: 'address.country',
    valueKey: 'id',
    labelKey: 'name',
  },
}
```

**Special features:**

* Static, API, or schema data sources
* Dependent data sources (reload based on other fields)
* Option sorting
* Loading state for API sources

#### Radio Widget (`radio`)

Radio button group widget for single selection.

**Widget name:** `radio`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "radio",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Gender",               // Optional: Display label
  "widget-data-path": "person.gender",     // Optional: Single path (string) or multi-path (object)
  "widget-data-default": "",              // Optional: Default value (string or number matching option values)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-source": {                 // Required: Data source configuration
    "type": "static",                     // "static" | "api" | "schema"
    "options": [                          // For static type
      { "value": "male", "label": "Male" },
      { "value": "female", "label": "Female" }
    ]
  },
  "widget-data-format": {                // Optional: Formatting options
    "layout": "vertical",                 // "vertical" | "horizontal" | "grid" (default: "vertical")
    "sortOptions": false                  // Sort options alphabetically
  }
}
```

**Example:**

```tsx
{
  widget: 'radio',
  'widget-type': 'input',
  'widget-id': 'gender',
  'widget-label': 'Gender',
  'widget-data-path': 'person.gender',
  'widget-data-source': {
    type: 'static',
    options: [
      { value: 'male', label: 'Male' },
      { value: 'female', label: 'Female' },
      { value: 'other', label: 'Other' },
    ],
  },
  'widget-data-format': {
    layout: 'horizontal',
    sortOptions: false,
  },
  'widget-required': true,
}
```

**Special features:**

* Vertical, horizontal, or grid layout
* Same data source support as select widget
* Option sorting

#### Checkbox Widget (`checkbox`)

Checkbox widget for boolean or multiple selections.

**Widget name:** `checkbox`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "checkbox",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Interests",            // Optional: Display label
  "widget-data-path": "person.interests", // Optional: Single path (string) or multi-path (object)
  "widget-data-default": false,           // Optional: boolean for single checkbox, string[] for multiple
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-source": {                 // Optional: For multiple selection
    "type": "static",                     // "static" | "api" | "schema"
    "options": [
      { "value": "sports", "label": "Sports" },
      { "value": "music", "label": "Music" }
    ]
  },
  "widget-data-format": {                // Optional: Formatting options
    "layout": "vertical",                 // "vertical" | "horizontal" | "grid"
    "sortOptions": false                  // Sort options alphabetically
  }
}
```

**Single checkbox (boolean) example:**

```tsx
{
  widget: 'checkbox',
  'widget-type': 'input',
  'widget-id': 'agreeToTerms',
  'widget-label': 'I agree to the terms and conditions',
  'widget-data-path': 'form.agreeToTerms',
  'widget-data-default': false,
  'widget-required': true,
}
```

**Multiple checkboxes example:**

```tsx
{
  widget: 'checkbox',
  'widget-type': 'input',
  'widget-id': 'interests',
  'widget-label': 'Interests',
  'widget-data-path': 'person.interests',
  'widget-data-source': {
    type: 'static',
    options: [
      { value: 'sports', label: 'Sports' },
      { value: 'music', label: 'Music' },
      { value: 'reading', label: 'Reading' },
    ],
  },
  'widget-data-format': {
    layout: 'vertical',
  },
}
```

**Special features:**

* Single checkbox for boolean values
* Multiple checkboxes for array selections
* Same layout options as radio widget

#### Boolean Widget (`boolean`)

Specialized boolean widget with multiple representation options.

**Widget name:** `boolean`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "boolean",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Is Active",            // Optional: Display label
  "widget-data-path": "user.isActive",    // Optional: Single path (string) or multi-path (object)
  "widget-data-default": false,           // Optional: Default value (boolean for boolean widgets)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-data-format": {                // Optional: Formatting options
    "booleanRepresentation": "yes-no",   // "true-false" | "yes-no" | "on-off" | "custom"
    "booleanControlType": "checkbox",      // "checkbox" | "radio" | "toggle"
    "booleanTrueLabel": "Yes",            // For custom representation
    "booleanFalseLabel": "No",            // For custom representation
    "allowUnset": false                   // Allow null/undefined value
  },
  "widget-orientation": "horizontal"      // Optional: "horizontal" | "vertical"
}
```

**Checkbox example:**

```tsx
{
  widget: 'boolean',
  'widget-type': 'input',
  'widget-id': 'isActive',
  'widget-label': 'Active',
  'widget-data-path': 'user.isActive',
  'widget-data-format': {
    booleanRepresentation: 'yes-no',
    booleanControlType: 'checkbox',
  },
}
```

**Radio buttons example:**

```tsx
{
  widget: 'boolean',
  'widget-type': 'input',
  'widget-id': 'newsletter',
  'widget-label': 'Subscribe to Newsletter',
  'widget-data-path': 'user.newsletter',
  'widget-data-format': {
    booleanRepresentation: 'yes-no',
    booleanControlType: 'radio',
  },
  'widget-orientation': 'horizontal',
}
```

**Toggle/switch example:**

```tsx
{
  widget: 'boolean',
  'widget-type': 'input',
  'widget-id': 'notifications',
  'widget-label': 'Enable Notifications',
  'widget-data-path': 'settings.notifications',
  'widget-data-format': {
    booleanControlType: 'toggle',
  },
}
```

**Special features:**

* Multiple representation styles (true/false, yes/no, on/off, custom)
* Multiple control types (checkbox, radio, toggle)
* Optional unset state
* Custom labels support

### Layout widgets

#### Array Widget (`array-widget`)

Widget for repeating simple values in an array.

**Widget name:** `array-widget`\
**Widget type:** `group`

**Configuration options:**

```json
{
  "widget": "array-widget",
  "widget-type": "group",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Skills",               // Optional: Display label
  "widget-data-path": "person.skills",    // Optional: Single path (string) or multi-path (object)
  "widget-required": false,               // Optional: Required field
  "widget-readonly": false,               // Optional: Read-only field
  "widget-item": {                        // Required: Configuration for each array item
    "widget": "text",
    "widget-type": "input",
    "widget-id": "skill",
    "widget-label": "Skill"
  },
  "widget-data-add-label": "Add Skill",   // Optional: Label for add button
  "widget-data-operations": {             // Optional: Operations configuration
    "add": true,                          // Show add button
    "remove": true,                       // Show remove button
    "edit": true                          // Allow editing
  }
}
```

**Example:**

```tsx
{
  widget: 'array-widget',
  'widget-type': 'group',
  'widget-id': 'skills',
  'widget-label': 'Skills',
  'widget-data-path': 'person.skills',
  'widget-item': {
    widget: 'text',
    'widget-type': 'input',
    'widget-label': 'Skill',
    'widget-id': 'skill',
  },
  'widget-data-add-label': 'Add Skill',
  'widget-data-operations': {
    add: true,
    remove: true,
    edit: true,
  },
}
```

**Special features:**

* Dynamic add/remove items
* Configurable item widget
* Array value storage

#### Iterable Accordion Widget (`iterable-accordion`)

Accordion-style widget for repeating complex objects.

**Widget name:** `iterable-accordion`\
**Widget type:** `group`

**Configuration options:**

Similar to Array Widget, but displays items in an accordion format.

**Example:**

```tsx
{
  widget: 'iterable-accordion',
  'widget-type': 'group',
  'widget-id': 'addresses',
  'widget-label': 'Addresses',
  'widget-data-path': 'person.addresses',
  'widget-item': {
    widget: 'vertical-layout',
    'widget-type': 'layout',
    widgets: [
      {
        widget: 'text',
        'widget-type': 'input',
        'widget-id': 'street',
        'widget-label': 'Street',
        'widget-data-path': 'street',
      },
      {
        widget: 'text',
        'widget-type': 'input',
        'widget-id': 'city',
        'widget-label': 'City',
        'widget-data-path': 'city',
      },
    ],
  },
  'widget-data-operations': {
    add: true,
    remove: true,
    edit: true,
  },
}
```

**Special features:**

* Accordion UI for better organization
* Supports complex nested widgets
* Collapsible items

### Display widgets

#### Display Widget (`display`)

Read-only widget for displaying information.

**Widget name:** `display`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "display",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Full Name",            // Optional: Display label
  "widget-data-path": "person.fullName",  // Optional: Single path (string) or multi-path (object)
  "widget-data-format": {                 // Optional: Formatting options for display
    "dateFormat": "YYYY-MM-DD",
    "currency": "USD",
    "locale": "en-US"
  }
}
```

**Example:**

```tsx
{
  widget: 'display',
  'widget-type': 'input',
  'widget-id': 'fullName',
  'widget-label': 'Full Name',
  'widget-data-path': 'person.fullName',
}
```

**Special features:**

* Read-only display
* Supports formatted values
* Can display without label (paragraph text)

#### Profile Widget (`profile`)

Widget for displaying profile information in a card layout.

**Widget name:** `profile`\
**Widget type:** `input`

**Configuration options:**

```json
{
  "widget": "profile",
  "widget-type": "input",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Profile",               // Optional: Display label
  "widget-data-path": "user.profile",      // Optional: Single path (string) or multi-path (object)
  // Profile-specific configuration
}
```

**Example:**

```tsx
{
  widget: 'profile',
  'widget-type': 'input',
  'widget-id': 'userProfile',
  'widget-label': 'Profile',
  'widget-data-path': 'user.profile',
}
```

### Table widgets

#### Table Widget (`table`)

Full-featured table widget with editable cells.

**Widget name:** `table`\
**Widget type:** `table`

**Configuration options:**

```json
{
  "widget": "table",
  "widget-type": "table",
  "widget-id": "fieldId",                 // Required: Unique identifier
  "widget-label": "Products",             // Optional: Display label
  "widget-data-path": "order.products",    // Optional: Single path (string) or multi-path (object)
  "widget-data-columns": [                 // Required: Column configurations
    {
      "column-key": "name",
      "widget-label": "Product Name",
      "widget": "text",                   // Optional: Widget type for column
      "widget-type": "input",
      "widget-data-path": "name",          // Optional: Single path (string) or multi-path (object)
      "widget-data-format": {},           // Optional: Formatting options
      "widget-data-validation": {},        // Optional: Validation rules
      "widget-data-source": {},           // Optional: Data source configuration
      "widget-required": false,           // Optional: Required field
      "widget-readonly": false            // Optional: Read-only field
    }
  ],
  "widget-data-operations": {             // Optional: Operations configuration
    "add": true,                          // Show add button
    "remove": true,                       // Show remove button
    "edit": true                          // Allow editing
  }
}
```

**Example:**

```tsx
{
  widget: 'table',
  'widget-type': 'table',
  'widget-id': 'products',
  'widget-label': 'Products',
  'widget-data-path': 'order.products',
  'widget-data-columns': [
    {
      'column-key': 'name',
      'widget-label': 'Product Name',
      widget: 'text',
      'widget-type': 'input',
      'widget-data-path': 'name',
      'widget-required': true,
    },
    {
      'column-key': 'quantity',
      'widget-label': 'Quantity',
      widget: 'number',
      'widget-type': 'input',
      'widget-data-path': 'quantity',
      'widget-data-format': {
        numericType: 'integer',
      },
    },
    {
      'column-key': 'price',
      'widget-label': 'Price',
      widget: 'currency',
      'widget-type': 'input',
      'widget-data-path': 'price',
    },
  ],
  'widget-data-operations': {
    add: true,
    remove: true,
    edit: true,
  },
}
```

**Special features:**

* Editable cells with widget support
* Add/remove rows
* Column-specific widget types
* Full validation support per column

#### Simple Table Widget (`simple-table`)

Simplified table widget for read-only or simple data display.

**Widget name:** `simple-table`\
**Widget type:** `table`

**Configuration options:**

Similar to Table Widget but optimized for display purposes.

**Example:**

```tsx
{
  widget: 'simple-table',
  'widget-type': 'table',
  'widget-id': 'summary',
  'widget-label': 'Order Summary',
  'widget-data-path': 'order.items',
  'widget-data-columns': [
    {
      'column-key': 'item',
      'widget-label': 'Item',
    },
    {
      'column-key': 'quantity',
      'widget-label': 'Quantity',
    },
  ],
}
```

### Widget configuration summary

All widgets support these common configuration properties:

* `widget`: Widget name/type (required)
* `widget-type`: Widget category - `'input'`, `'layout'`, `'table'`, or `'group'`
* `widget-id`: Unique identifier (required)
* `widget-label`: Display label
* `widget-data-path`: Data binding path
* `widget-data-default`: Default value
* `widget-required`: Required field flag
* `widget-readonly`: Read-only flag
* `widget-data-placeholder`: Placeholder text
* `widget-data-helptext`: Help text
* `widget-data-tooltip`: Tooltip text
* `widget-data-validation`: Validation rules
* `widget-data-format`: Formatting options
* `widget-data-source`: Data source configuration
* `widget-data-options`: Conditional logic and widget-specific options

## Creating custom widgets

{% stepper %}
{% step %}
#### Create the widget component

```tsx
import React from 'react';
import { useBaseWidget, BaseWidgetConfig } from '@openg2p/registry-widgets';

interface MyCustomWidgetProps {
  config: BaseWidgetConfig;
}

export const MyCustomWidget: React.FC<MyCustomWidgetProps> = ({ config }) => {
  const {
    widgetId,
    value,
    error,
    isEnabled,
    isVisible,
    onChange,
    onBlur,
  } = useBaseWidget({ config });

  if (!isVisible) {
    return null;
  }

  return (
    <div className="my-custom-widget">
      <label htmlFor={widgetId}>
        {config['widget-label']}
      </label>
      <input
        id={widgetId}
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        disabled={!isEnabled}
        className={error.length > 0 ? 'error' : ''}
      />
      {error.length > 0 && (
        <div className="error-message">
          {error.map((err, i) => (
            <div key={i}>{err}</div>
          ))}
        </div>
      )}
    </div>
  );
};
```
{% endstep %}

{% step %}
#### Register the widget

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
#### Use the widget

```tsx
const config = {
  widget: 'my-custom-widget',
  'widget-type': 'input',
  'widget-id': 'customField',
  'widget-label': 'Custom Field',
  'widget-data-path': 'form.customField',
};

<WidgetRenderer config={config} />
```
{% endstep %}
{% endstepper %}

### Advanced custom widget example

```tsx
import React, { useState } from 'react';
import { useBaseWidget, BaseWidgetConfig, useWidgetTranslation } from '@openg2p/registry-widgets';

export const ColorPickerWidget: React.FC<{ config: BaseWidgetConfig }> = ({ config }) => {
  const {
    widgetId,
    value,
    error,
    isEnabled,
    isVisible,
    onChange,
    onBlur,
  } = useBaseWidget({ config });
  
  const { t } = useWidgetTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const colors = [
    { value: 'red', label: t('color.red') },
    { value: 'blue', label: t('color.blue') },
    { value: 'green', label: t('color.green') },
  ];

  if (!isVisible) return null;

  return (
    <div className="color-picker-widget">
      <label htmlFor={widgetId}>
        {config['widget-label']}
        {config['widget-required'] && <span className="required">*</span>}
      </label>
      
      <div className="color-picker-container">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={!isEnabled}
          className={`color-picker-button ${error.length > 0 ? 'error' : ''}`}
          style={{ backgroundColor: value || '#fff' }}
        >
          {value || t('selectColor')}
        </button>
        
        {isOpen && (
          <div className="color-picker-dropdown">
            {colors.map((color) => (
              <button
                key={color.value}
                type="button"
                onClick={() => {
                  onChange(color.value);
                  setIsOpen(false);
                  onBlur();
                }}
                className="color-option"
                style={{ backgroundColor: color.value }}
              >
                {color.label}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {error.length > 0 && (
        <div className="error-message">
          {error.map((err, i) => (
            <div key={i}>{err}</div>
          ))}
        </div>
      )}
      
      {config['widget-data-helptext'] && (
        <div className="help-text">{config['widget-data-helptext']}</div>
      )}
    </div>
  );
};
```

## Advanced patterns

### Multi-step forms

```tsx
import { useState } from 'react';
import { SectionsContainer } from '@openg2p/registry-widgets';

function MultiStepForm() {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});

  const steps = [
    {
      'section-id': 'step1',
      'section-title': 'Personal Information',
      panels: [/* ... */],
    },
    {
      'section-id': 'step2',
      'section-title': 'Contact Information',
      panels: [/* ... */],
    },
    {
      'section-id': 'step3',
      'section-title': 'Review',
      panels: [/* ... */],
    },
  ];

  return (
    <div>
      <SectionsContainer
        schema={{ sections: [steps[currentStep]] }}
        initialData={formData}
      />
      <div className="form-navigation">
        {currentStep > 0 && (
          <button onClick={() => setCurrentStep(currentStep - 1)}>
            Previous
          </button>
        )}
        {currentStep < steps.length - 1 && (
          <button onClick={() => setCurrentStep(currentStep + 1)}>
            Next
          </button>
        )}
      </div>
    </div>
  );
}
```

### Dynamic form generation

```tsx
function DynamicForm({ schema }: { schema: UISchema }) {
  const [formData, setFormData] = useState({});

  const handleValueChange = (widgetId: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [widgetId]: value,
    }));
  };

  return (
    <WidgetProvider store={createWidgetStore()} schemaData={formData}>
      <SectionsContainer
        schema={schema}
        onValueChange={handleValueChange}
      />
    </WidgetProvider>
  );
}
```

### Form validation on submit

```tsx
import { useDispatch, useSelector } from 'react-redux';
import { WidgetRootState } from '@openg2p/registry-widgets';

function FormWithValidation() {
  const dispatch = useDispatch();
  const errors = useSelector((state: WidgetRootState) => state.widget.errors);
  const values = useSelector((state: WidgetRootState) => state.widget.values);

  const handleSubmit = () => {
    // Validate all widgets
    const hasErrors = Object.values(errors).some(
      (errorArray) => errorArray.length > 0
    );

    if (hasErrors) {
      alert('Please fix validation errors');
      return;
    }

    // Submit form data
    console.log('Form data:', values);
  };

  return (
    <div>
      {/* Note: `SectionsContainer` expects `sections`, not `schema` */}
      <SectionsContainer sections={schema.sections} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

### Array widgets

```tsx
const arrayWidgetConfig = {
  widget: 'array-widget',
  'widget-type': 'group',
  'widget-id': 'addresses',
  'widget-label': 'Addresses',
  'widget-data-path': 'person.addresses',
  'widget-item': {
    widget: 'text',
    'widget-type': 'input',
    'widget-id': 'address',
    'widget-label': 'Address',
    'widget-data-path': 'address',
  },
  'widget-data-operations': {
    add: true,
    remove: true,
    edit: true,
  },
  'widget-data-add-label': 'Add Address',
};
```

## Internationalization

The widget library supports internationalization (i18n) with automatic translation loading from your host project's locale files. By default, the library will automatically discover and load translations from common `locales/` paths, making it easy to integrate with existing i18n setups.

### Automatic translation loading (default behavior)

**The library automatically loads translations from your host project's locale directory.** You don't need to configure anything - just place your translation files in one of these standard locations (checked in order):

* `/i18/locales/{language}.json`
* `/public/i18/locales/{language}.json`
* `/locales/{language}.json`
* `/public/locales/{language}.json`
* `/locales/{language}/translation.json`
* `/public/locales/{language}/translation.json`

**Example project structure:**

```
your-project/
├── public/
│   └── locales/
│       ├── en.json
│       ├── es.json
│       └── fr.json
└── src/
    └── App.tsx
```

**Translation file format (`public/locales/en.json`):**

```json
{
  "widget.required": "This field is required",
  "widget.invalid": "Invalid value",
  "common.select": "Select",
  "common.loadingOptions": "Loading options...",
  "person.name": "Name",
  "person.email": "Email Address"
}
```

The library will automatically:

1. Detect the current language (defaults to `'en'`)
2. Try to load translations from the standard paths listed above
3. Fall back to default English translations if no files are found
4. Use the loaded translations for all widget labels and messages

**No configuration needed!** Simply use the widgets and they will automatically pick up translations from your project's locale files.

### Override methods

All methods below are **overrides** to the automatic loading behavior. Use them when you need custom translation logic or want to provide translations programmatically.

#### Method 1: Manual initialization with custom resources

If you want to provide translations programmatically instead of using files:

```tsx
import { initI18n } from '@openg2p/registry-widgets';

await initI18n({
  lng: 'en',
  resources: {
    en: {
      translation: {
        'widget.required': 'This field is required',
        'widget.invalid': 'Invalid value',
        // ... more translations
      }
    },
    es: {
      translation: {
        'widget.required': 'Este campo es obligatorio',
        'widget.invalid': 'Valor inválido',
        // ... more translations
      }
    }
  },
  autoLoad: false  // Disable automatic loading
});
```

#### Method 2: Custom load path

If your translation files are in a non-standard location:

```tsx
import { initI18n } from '@openg2p/registry-widgets';

initI18n({
  lng: 'en',
  loadPath: '/custom/path/locales/{{lng}}.json',  // Custom path
  // Or multiple paths:
  // loadPath: ['/path1/{{lng}}.json', '/path2/{{lng}}.json']
});
```

#### Method 3: Using translate prop in WidgetProvider

You can provide a custom translation function that overrides the default behavior:

```tsx
import { WidgetProvider } from '@openg2p/registry-widgets';

const customTranslate = (key: string, options?: any) => {
  // Your custom translation logic
  return myTranslationService.translate(key, options);
};

<WidgetProvider translate={customTranslate}>
  {/* Your widgets */}
</WidgetProvider>
```

#### Method 4: Translating widget labels programmatically

For translating UI schema labels before rendering:

```tsx
import { translateUISchema } from '@openg2p/registry-widgets';

const translatedSchema = translateUISchema(uiSchema, {
  'person.name': 'Nombre',
  'person.email': 'Correo Electrónico',
});
```

### Using translation in custom widgets

```tsx
import { useWidgetTranslation } from '@openg2p/registry-widgets';

export const MyWidget = ({ config }: { config: BaseWidgetConfig }) => {
  const { t } = useWidgetTranslation();
  
  return (
    <div>
      <label>{t(config['widget-label'] || '')}</label>
      {/* ... */}
    </div>
  );
};
```

### Summary

* **Default behavior**: Automatically loads translations from your project's `locales/` or `public/locales/` folder
* **No setup required**: Just place your translation files in standard locations
* **Override methods**: Use manual initialization, custom paths, or translate props when you need custom behavior
* **Fallback**: Falls back to default English translations if no files are found

## Best practices

### Widget IDs

Always use unique, descriptive widget IDs:

```tsx
// ✅ Good
'widget-id': 'user-email-address'

// ❌ Bad
'widget-id': 'field1'
```

### Data paths

Use consistent dot-notation paths:

```tsx
// ✅ Good
'widget-data-path': 'person.contact.email'

// ❌ Bad
'widget-data-path': 'personContactEmail'
```

### Validation

Provide clear, user-friendly error messages:

```tsx
// ✅ Good
{
  'widget-data-validation': {
    pattern: '^[A-Z]{2}[0-9]{6}$',
    patternMessage: 'Must be 2 uppercase letters followed by 6 digits',
  }
}

// ❌ Bad
{
  'widget-data-validation': {
    pattern: '^[A-Z]{2}[0-9]{6}$',
  }
}
```

### Conditional logic

Keep conditions simple and testable:

```tsx
// ✅ Good - Simple condition
{
  'widget-data-options': {
    action: 'show',
    condition: {
      field: 'person.age',
      operator: 'greaterThan',
      value: 18
    }
  }
}

// ❌ Bad - Complex nested logic (not supported)
```

### Data sources

Cache API responses when possible:

```tsx
// Use schema data sources for static or rarely-changing data
{
  'widget-data-source': {
    type: 'schema',
    path: 'countries',  // Loaded once at initialization
  }
}
```

### Performance

* Use `React.memo` for expensive widget components
* Avoid unnecessary re-renders by using stable references
* Use `useMemo` for computed values

```tsx
export const ExpensiveWidget = React.memo(({ config }: { config: BaseWidgetConfig }) => {
  const expensiveValue = useMemo(() => {
    // Expensive computation
  }, [dependencies]);
  
  // ...
});
```

### Type safety

Always use TypeScript types:

```tsx
import { BaseWidgetConfig } from '@openg2p/registry-widgets';

const config: BaseWidgetConfig = {
  // TypeScript will catch errors
};
```

## Troubleshooting

### Widget not rendering

**Problem**: Widget doesn't appear on screen.

**Solutions**:

1. Check if widget is registered:

```tsx
import { widgetRegistry } from '@openg2p/registry-widgets';
console.log(widgetRegistry.has('my-widget')); // Should be true
```

2. Check if widget is hidden by conditional logic:

```tsx
const { isVisible } = useBaseWidget({ config });
console.log('Widget visible:', isVisible);
```

3. Verify widget configuration:

```tsx
console.log('Config:', config);
// Ensure widget, widget-id, and widget-type are set
```

### Validation not working

**Problem**: Validation errors don't appear.

**Solutions**:

1. Ensure `widget-required` or validation rules are set:

```tsx
{
  'widget-required': true,
  'widget-data-validation': {
    required: true,
  }
}
```

2. Check if field has been touched:

```tsx
const { touched, error } = useBaseWidget({ config });
// Errors only show after field is touched
```

3. Manually trigger validation:

```tsx
const { onBlur } = useBaseWidget({ config });
// Call onBlur to mark field as touched
```

### Data not updating

**Problem**: Widget value doesn't update in Redux store.

**Solutions**:

1. Verify data path is correct:

```tsx
'widget-data-path': 'person.name'  // Must match your data structure
```

2. Check Redux store state:

```tsx
import { useSelector } from 'react-redux';
const values = useSelector((state: WidgetRootState) => state.widget.values);
console.log('Store values:', values);
```

3. Ensure onChange is called:

```tsx
const { onChange } = useBaseWidget({ config });
onChange(newValue);  // This should update Redux
```

### API data source not loading

**Problem**: Options from API don't appear.

**Solutions**:

1. Verify `dataSourceRequestHandler` is provided (via `WidgetProvider` or directly on the widget hook/component):

```tsx
<WidgetProvider dataSourceRequestHandler={dataSourceRequestHandler}>
```

2. Check API response format:

```tsx
// Response should be an array or object with array property
// Use valueKey and labelKey to map response
```

3. Check for errors in console:

```tsx
const dataSourceRequestHandler = async (service, endpoint, method, params, options) => {
  try {
    const response = await fetch(`/api/${service}/${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
      body: method === 'GET' ? undefined : JSON.stringify(params),
    });
    return response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
};
```

### Conditional logic not working

**Problem**: Widget doesn't show/hide based on conditions.

**Solutions**:

1. Verify condition field path:

```tsx
condition: {
  field: 'person.maritalStatus',  // Must match actual data path
  operator: 'equals',
  value: 'married'
}
```

2. Check field value:

```tsx
const { getFieldValue } = useBaseWidget({ config });
const maritalStatus = getFieldValue('person.maritalStatus');
console.log('Marital status:', maritalStatus);
```

3. Verify operator:

```tsx
// Use correct operator for data type
// 'equals' for exact match
// 'notEmpty' for checking existence
// etc.
```

### TypeScript Errors

**Problem**: TypeScript compilation errors.

**Solutions**:

1. Ensure all types are imported:

```tsx
import { BaseWidgetConfig, WidgetStore } from '@openg2p/registry-widgets';
```

2. Check widget registry entry:

```tsx
widgetRegistry.register({
  widget: 'my-widget',
  component: MyWidget,  // Must match WidgetRegistryEntry type
});
```

3. Verify config structure:

```tsx
const config: BaseWidgetConfig = {
  widget: 'text',
  'widget-id': 'field1',
  // ... other required fields
};
```

## Conclusion

This tutorial has covered all the essential aspects of the OpenG2P Registry UI Widgets library. You should now be able to:

* Set up and configure the library
* Use pre-built widgets effectively
* Create custom widgets
* Implement validation and conditional logic
* Work with data sources and formatting
* Handle internationalization
* Troubleshoot common issues

For more examples, check the `examples/` directory in the repository. For API reference, see the main `README.md` file.

Happy coding! 🚀

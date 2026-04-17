# Widget Library

## What is registry UI widget?

The **Registry UI Widget Library** (`@openg2p/registry-widgets`) is a comprehensive, extensible React component system designed specifically for building dynamic, data-driven forms and user interfaces in the OpenG2P registry ecosystem. It provides a declarative, schema-based approach to creating complex forms with advanced features like conditional logic, multi-path data binding, validation, internationalization, and more.

At its core, the library transforms JSON-based UI schemas into fully functional React components, enabling developers to build sophisticated registry interfaces without writing repetitive form code. The library is built with TypeScript, Redux for state management, and follows a plugin-based architecture that allows for easy extension and customization.

Change Request-Based Design: The library is fundamentally designed around the change request workflow pattern, which is central to OpenG2P registry operations. This design enables a clear separation between viewing existing registry data and proposing changes, with built-in support for audit trails, approval workflows, and change tracking. This architectural approach ensures data integrity and provides transparency in registry modifications.

## Purpose and use cases

The Registry UI Widget Library serves as the foundation for building user interfaces in OpenG2P registry applications, where complex data entry, validation, and display requirements are common. It is particularly well-suited for:

{% stepper %}
{% step %}
#### Beneficiary registration forms

* Dynamic form generation based on program requirements
* Multi-step registration workflows
* Conditional field visibility based on beneficiary type or status
* Document upload and verification
{% endstep %}

{% step %}
#### Data entry and management

* Structured data entry with validation
* Table-based data editing with inline operations
* Repeating data structures (arrays, accordions)
* Bulk data operations
{% endstep %}

{% step %}
#### Registry viewing and editing with change request workflow

* Read-only registry views with section-based layouts
* Edit-in-place functionality with section-level save operations
* CRView mode with audit trail display
* Change request creation and submission workflows
* Comparison views for data changes
* Approval workflow support with metadata tracking
{% endstep %}
{% endstepper %}

## Unique features for OpenG2P Registry

The Registry UI Widget Library brings several unique and powerful features that distinguish it from generic form libraries and make it particularly valuable for OpenG2P registry implementations. Central to the library's design is the change request-based architecture, which enables proper workflow management for registry data modifications.

### Section-based architecture with flexible layouts

Unlike traditional form libraries, the widget system uses a hierarchical Section → Panel → Widget structure that provides exceptional layout flexibility:

* Sections: Top-level containers that can be independently editable or read-only
* Panels: Nested containers supporting both horizontal and vertical orientations
* CSS Grid Integration: Automatic grid-based layout that ensures proper alignment across sections
* Responsive Design: Adaptive layouts that work across different screen sizes
* Column Spanning: Sections and widgets can span multiple columns for complex layouts

This architecture enables the creation of sophisticated, multi-column registry views that maintain consistent alignment and professional appearance.

### Multi-path data binding

The library supports both single-path and multi-path data binding, allowing widgets to read from and write to multiple data locations simultaneously:

```json
{
  "widget-data-path": {
    "firstName": "person.fname",
    "lastName": "person.lname"
  }
}
```

This feature is particularly useful for:

* Complex data structures where a single widget needs to aggregate multiple fields
* Profile widgets that display identity information from various sources
* Form fields that need to update multiple related data points

### Internationalization (i18n)

The library includes a sophisticated translation system that works seamlessly with UI schemas:

* Translation Key Support: Widget labels, placeholders, help text, and tooltips can use translation keys (e.g., "sections.personalDetails")
* Automatic Translation: The `translateUISchema` utility automatically translates entire schemas
* Auto-Loading: Automatically attempts to load translations from common project directory structures
* Nested Translation: Recursively translates nested widgets, panels, and data source options
* Fallback Support: Graceful fallback to default values when translations are missing

This enables OpenG2P implementations to support multiple languages without code changes, simply by providing translation files.

### Advanced conditional logic

The widget system provides powerful conditional logic capabilities that go beyond simple show/hide:

* Multiple Actions: Show, hide, enable, or disable widgets based on conditions
* Rich Operators: Supports equals, notEquals, notEmpty, empty, greaterThan, lessThan, contains, and notContains
* Cross-Field Dependencies: Conditions can reference any field in the form using dot-notation paths
* Dynamic Behavior: Conditions are evaluated reactively as form values change

This enables the creation of intelligent forms that adapt to user input, reducing errors and improving user experience.

### Multiple data source types

The library supports three types of data sources for dropdowns, selects, and other option-based widgets:

* Static Data: Hardcoded options defined in the schema
* API Data Sources: Dynamic options fetched from REST APIs with support for:
  * Dependency-based loading (e.g., load states when country is selected)
  * Custom headers and request bodies
  * Response transformation (value/label key mapping)
* Schema Reference Data: Options pulled from reference data within the schema itself

This flexibility allows registry forms to work with both static reference data and dynamic, context-aware options.

### Comprehensive widget registry system

The library includes a plugin-based widget registry that enables:

* Extensibility: Easy registration of custom widgets without modifying core library code
* Default Widgets: 19 pre-built widgets covering common use cases
* Widget Discovery: Runtime widget lookup and fallback mechanisms
* Type Safety: Full TypeScript support for widget registration and configuration

Pre-built widgets include:

* Text inputs (with masking, character restrictions, case control)
* Number inputs (with precision, formatting, thousand separators)
* Date and DateTime inputs (with picker/manual/hybrid modes)
* Phone inputs (with country code support)
* Currency inputs (with locale-aware formatting)
* File inputs (with preview and serialization)
* Tables (simple display and editable with record operations)
* Arrays and Accordions (for repeating data structures)
* Profile widgets (for identity display)
* Boolean widgets (checkbox, radio, toggle variants)
* Display widgets (read-only text display)

### Advanced validation system

The validation system supports multiple validation strategies:

* Built-in Validators: Required, pattern (regex), min/max length, min/max values
* Zod Integration: Full support for Zod schemas for complex validation logic
* Validation Types: Pre-configured validators for email, phone, URL
* Custom Validators: Support for custom validation functions
* Real-time Validation: Validation runs on blur and value change
* Error Display: Comprehensive error message display with touch state tracking

### Rich formatting capabilities

The library provides extensive formatting options for different data types:

* Date Formatting: Customizable date formats with locale support
* Currency Formatting: Locale-aware currency formatting with symbol placement
* Phone Formatting: Country-specific phone number formatting
* Number Formatting: Decimal places, thousand separators, rounding modes
* Text Formatting: Case control (uppercase, lowercase, capitalize), character restrictions, input masking
* Format on Blur: Optional formatting that applies when fields lose focus

### File handling with preview

The file input widget includes advanced file management features:

* File Preview: Modal-based preview for images and documents
* File Serialization: Automatic conversion to base64 or other formats for storage
* File Validation: Size limits, type restrictions, and custom validation
* Multiple File Support: Support for single or multiple file uploads
* Supporting Documents: Section-level document management with type-specific handling

### Change request-based design and change request view mode

This is a core architectural feature that sets the Registry UI Widget Library apart from generic form libraries. The entire library is designed around the change request workflow pattern, which is fundamental to OpenG2P registry operations:

* Change Request Workflow Support: Built-in support for creating, viewing, and managing change requests
* CRView Mode: Special viewing mode specifically designed for change requests with:
  * Audit Trail Display: Automatic display of who created and approved records with timestamps
  * Read-Only Mode: Prevents accidental modifications during change request review
  * Metadata Display: Automatic display of `createdBy`, `createdDate`, `approvedBy`, `approvedDate`
  * Flexible Data Sources: Reads audit data from schema data or Redux store
* Change Tracking: Tracks old and new values for each section, enabling comparison views
* Workflow Integration: Designed to integrate with backend change request approval workflows
* Data Integrity: Ensures that registry modifications go through proper approval processes

This change request-based design enables proper governance in registry operations, where all modifications must be reviewed and approved before being applied to the master registry. This is critical for maintaining data quality and audit compliance in government-to-person (G2P) payment systems.

### Section-level editing with save operations

The library supports granular editing at the section level, which aligns with the change request workflow:

* Independent Sections: Each section can be independently editable or read-only
* Section Save Callbacks: Custom save handlers for section-level data persistence
* Change Tracking: Tracks old and new values for each section (essential for change requests)
* Edit Mode Toggle: Sections can switch between view and edit modes
* Batch Operations: Multiple sections can be edited and saved independently
* Change Request Integration: Section-level changes can be packaged as change requests for approval

This is particularly valuable for large registry forms where users may only need to edit specific sections, and where those changes need to be tracked and approved through the change request workflow.

### Table widgets with record operations

Two types of table widgets provide different levels of functionality:

* Simple Table: Display-only tables for showing structured data
* Editable Table: Full CRUD operations (add, remove, edit) at the record level
* Column Configuration: Each column can have its own widget type, validation, and formatting
* Column Spanning: Tables can span multiple columns in the grid layout
* Inline Editing: Edit records directly within the table

### Array and accordion widgets

Specialized widgets for handling repeating data structures:

* Array Widget: Simple list-based repeating data entry
* Iterable Accordion: Accordion-based interface for repeating data with expand/collapse
* Item Templates: Define widget configuration once, apply to all items
* Add/Remove Operations: Dynamic addition and removal of items
* Collapsed State: Optional default collapsed state for accordions

### Profile widget for identity display

A specialized widget for displaying beneficiary or user identity:

* Multi-Field Display: Combines image, name, and ID in a single widget
* Customizable Styling: Configurable image size, colors, and label display
* Multi-Path Binding: Reads from multiple data paths to compose the profile
* Read-Only Display: Optimized for identity verification and display

### Redux-based state management

The library uses Redux for centralized state management:

* Centralized State: All widget values, errors, and touched states in one store
* Path-Based Access: Values accessed using dot-notation paths
* Reactive Updates: Components automatically update when state changes
* Store Integration: Can integrate with existing Redux stores or use isolated widget store
* DevTools Support: Full Redux DevTools support for debugging

### TypeScript-first design

The entire library is built with TypeScript:

* Full Type Definitions: Complete type coverage for all configurations and APIs
* Type Safety: Catch configuration errors at compile time
* IntelliSense Support: Rich autocomplete and documentation in IDEs
* Type Inference: Automatic type inference for widget configurations

### Unstyled base with style flexibility

The library provides unstyled base components:

* No CSS Dependencies: No opinionated styling framework
* Tailwind Ready: Designed to work seamlessly with Tailwind CSS
* Custom Styling: Full control over appearance through className props
* Style Isolation: Widgets don't interfere with application styles

## Architecture Overview

{% embed url="https://miro.com/app/board/uXjVGPIon0M=/?share_link_id=859507579636" %}

**Application Layer** - The top-level entry point where UI schemas (JSON configurations) are parsed and rendered. This layer handles the hierarchical structure of Sections → Panels → Widgets, managing layout, orientation, and section-level operations like editing and saving.

**Widget Registry Layer** - A plugin system that maintains a catalog of available widgets. When a widget is requested by name, the registry looks it up and returns the corresponding React component. This enables dynamic widget loading and easy extensibility - new widgets can be registered without modifying core library code.

**Widget Components Layer** - The actual React components that render UI elements (text inputs, selects, tables, etc.). These are the 19+ pre-built widgets that come with the library. Each widget is a React component that receives configuration and renders the appropriate UI. Custom widgets can be added by registering them in the registry.

**Core Hooks Layer** - React hooks that provide all the business logic for widgets. The `useBaseWidget` hook handles state management, validation, conditional logic, data source loading, and formatting. The `useWidgetTranslation` hook provides internationalization support. Widget components use these hooks to get values, errors, visibility states, and change handlers without directly interacting with Redux or utilities.

**State Management Layer** - Redux store and widget slice that maintain centralized state for all widgets. The Redux Store holds all widget values, errors, touched states, loading states, and data source options. The Widget Slice defines the state structure and provides actions (setValue, setError, setTouched, etc.) to update state. This ensures a single source of truth and enables efficient re-renders.

**Utility Layer** - Pure functions that handle cross-cutting concerns:

* **Validation**: Validates widget values using built-in rules, regex patterns, or Zod schemas
* **Formatting**: Formats values for display (dates, currency, phone numbers, numbers, text)
* **Data Sources**: Loads options for select/dropdown widgets from static data, APIs, or schema references
* **Conditional Logic**: Evaluates conditions to determine widget visibility and enablement
* **Path Utilities**: Handles dot-notation path resolution for reading/writing nested data structures

#### Data Flow <a href="#data-flow" id="data-flow"></a>

1. **Top-Down (Rendering)**: Application receives UISchema → Registry looks up widgets → Components render using hooks → Hooks read from Redux store → Utilities process data
2. **Bottom-Up (Updates)**: User interacts with widget → Component calls hook's onChange → Hook dispatches Redux action → Store updates → Hooks re-evaluate → Components re-render

This layered architecture provides clear separation of concerns, making the library maintainable, testable, and extensible.

## Benefits for OpenG2P Registry

* Rapid Development: Schema-driven development means forms can be created by configuring JSON rather than writing code
* Consistency: Standardized widget behavior ensures consistent user experience across the registry
* Maintainability: Centralized widget logic means bug fixes and improvements benefit all forms
* Internationalization: Built-in i18n support enables multi-language registries without code changes
* Extensibility: Plugin architecture allows custom widgets for domain-specific needs
* Type Safety: TypeScript support reduces runtime errors and improves developer experience
* Performance: Redux-based state management ensures efficient updates and minimal re-renders
* Accessibility: Semantic HTML and proper form structure support accessibility requirements
* Flexibility: Multiple layout options and conditional logic enable complex, adaptive forms
* Developer Experience: Comprehensive documentation, type definitions, and examples accelerate development

## Conclusion

The Registry UI Widget Library is a powerful, purpose-built solution for OpenG2P registry interfaces. Its combination of section-based architecture, multi-path data binding, schema-based internationalization, advanced conditional logic, and comprehensive widget ecosystem makes it an ideal foundation for building complex, maintainable, and user-friendly registry applications.

By providing a declarative, schema-driven approach to form building, the library enables rapid development while maintaining flexibility and extensibility. The change request-based design is central to the library's architecture, ensuring that all registry modifications go through proper workflows with audit trails and approval processes.

The focus on OpenG2P-specific features like change request workflows, section-level editing, and profile widgets ensures that the library addresses real-world registry requirements out of the box. Whether building beneficiary registration forms, change request interfaces, or data viewing tools, the Registry UI Widget Library provides the building blocks needed to create sophisticated, production-ready registry applications that maintain data integrity and governance.

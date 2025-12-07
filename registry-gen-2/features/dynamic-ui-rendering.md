---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Dynamic UI rendering

The Base Registry includes a dynamic form rendering engine that reads the registry’s JSON schema and generates appropriate UI forms at runtime. Instead of building custom screens for each registry, UI components interpret schema definitions, grouping rules, and widget specifications to render entry forms, detail views, and table listings. Custom field types such as lookup widgets can be declared in the schema and automatically linked with lookup APIs that return enumeration values from centralized metadata.

#### Extensible Component Model

UI implementers may define new custom components that the renderer can use inside JSON Schema definitions. The registry frontend exposes reusable interface patterns including hierarchical tab navigation for child registers, audit history views, pending change alerts, and version comparison screens. This ensures a consistent user experience across all registry types while still allowing domain-specific customization.

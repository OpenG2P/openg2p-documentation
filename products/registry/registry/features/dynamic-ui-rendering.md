# Dynamic UI rendering

The Base Registry includes a dynamic form rendering engine that reads the registry’s JSON schema and generates appropriate UI forms at runtime. Instead of building custom screens for each registry, UI components interpret schema definitions, grouping rules, and widget specifications to render entry forms, detail views, and table listings. Custom field types such as lookup widgets can be declared in the schema and automatically linked with lookup APIs that return enumeration values from centralized metadata.

#### Extensible Component Model

UI implementers may define new custom components that the renderer can use inside JSON Schema definitions.&#x20;

Apart from the custom domain models that are presented based on the JSON schema configurations, the domain registers (customized and extended) will render themselves using the same hierarchical tab navigation for child registers, verification panels, version history panels, pending change alerts, and de-duplicate screens. This ensures a consistent user experience across all registry types while still allowing domain-specific customizations.

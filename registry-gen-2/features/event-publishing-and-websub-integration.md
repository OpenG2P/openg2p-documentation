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

# Event Publishing and WebSub Integration

The Base Registry includes event publishing support using a WebSub-compatible mechanism. Whenever a registry changes state, the system generates and publishes a notification to subscribers who have registered interest in that registry type or event type. Topics can be aligned with interoperability standards, enabling external systems to receive updates in standardized payload formats. The registry integrates with subscription APIs defined by partner registries, allowing it to both publish and receive registry events.

#### Standards-based Message Transformation

Outgoing messages are generated using template-driven mapping engines that convert internal registry records into standard payload structures defined by interoperability specifications. The registry can publish the same registry event in multiple formats by using separate topic namespaces, enabling compatibility with different consumers. Template mappings are stored as metadata and can be versioned independently, supporting backward compatibility without changing registry business logic.

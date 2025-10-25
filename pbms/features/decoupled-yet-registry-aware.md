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

# Decoupled yet Registry-Aware

The OpenG2P PBMS is designed to work with registries without assuming ownership of them. Instead of pulling registry data into its own system, PBMS accesses registries in a decoupled manner and generates beneficiary lists by applying rules directly on registry data. This ensures that registries remain the single source of truth while PBMS operates on top of them. To support the definition of eligibility, disbursement, and entitlement rules, PBMS maintains awareness of registry schemas and metadata, enabling accurate interpretation and application of rules.

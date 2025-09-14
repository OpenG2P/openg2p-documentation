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

# Warehouses & Agencies

**Warehouses** in PBMS represent the points from which goods, services, or cash are dispatched. For cash-based programs, sponsor banks holding program funds are treated as warehouses. Allocation of warehouses is determined by association rules based on geography and benefit codes, ensuring that distribution aligns with the geographical spread of beneficiaries. PBMS sends notifications to warehouses with detailed instructions, including the agencies responsible for collecting inventory and distributing it to beneficiaries. Warehouse allocation typically operates at the level of larger geographic entities such as states or districts, though this can be configured to suit specific implementations.

**Agencies** function similarly to warehouses but operate on smaller geographic areas. Allocation of agencies is likewise based on association rules tied to geography and benefit codes, but while warehouses are mapped to large entities like districts or states, agencies are mapped to localities, postcodes, or neighborhoods. Once allocated, PBMS sends notifications to agencies containing details of beneficiaries and their entitlements, ensuring localized execution of benefit delivery.

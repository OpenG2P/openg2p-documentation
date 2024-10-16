---
layout:
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
---

# Deduplication

In Social Registry (SR), the data are received and recorded in several ways. SR is dynamically updated via APIs, Service Provider Portal, ODK, Login-based direct data entry, etc. To maintain the data integrity in SR, a process is a must to ensure the uniqueness and accuracy of the recorded registrants' data. SR has a solution/feature named _**Deduplication**_.&#x20;

## Deduplication

_**Deduplication**_ is the process that identifies and stores the duplicate entries of the recorded registrants' data in SR. It can manage duplicate records within separate groups and individual registries. The user must have an Administrator or Registrator role to access this functionality.

## ID-based deduplication

ID-based deduplication is a method that detects duplicates based on unique identifiers i.e., functional ID or National ID assigned to each recorded registrant belonging to an individual/group. This method ensures each ID is distinct and helps to maintain a single entry for each recorded registrant. In this way, it eliminates redundancies and keeps the database more reliable, clean, and efficient.

To know more about Odoo merge and deduplication, [click here](https://hibou.io/docs/contacts-64/merging-deduplicating-contacts-in-odoo-12-13-331)

## Feature and functionality

| Deduplication method                              | Deduplication process                                                                                                                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Individual Registry Deduplication**             | Individual duplication record identification and management ensures accuracy and granularity in the deduplication process.                                                                                                |
| **Kind based deduplication for Group registrant** | <ul><li>It detects the groups that have the same Kind and removes the duplicate groups based on ID.</li><li>It detects the group member with the same kind and removes the duplicate group member based on ID.</li></ul>  |
| **Separate Registry Groups Deduplication**        | Each registry group's deduplication procedure enables precise duplicate identification and management within discrete categories                                                                                          |
| **Deduplicate Button**                            | With the addition of a _**Deduplicate**_ button to the _**Social Registry**_ screen, users can initiate the deduplication process easily.                                                                                 |
| **Automated Record Identification**               | When users click the _**Deduplicate**_ button, the system identifies the duplicate records and notifies them about the number of duplicate records found. The duplicates are then saved to a separate duplicate registry. |

## **Source code**

[https://github.com/OpenG2P/openg2p-social-registry/tree/17.0-develop/g2p\_registry\_id\_deduplication](https://github.com/OpenG2P/openg2p-social-registry/tree/17.0-develop/g2p\_registry\_id\_deduplication)

## Related user guides

:notebook\_with\_decorative\_cover:[Configure ID Deduplication, Deduplicate, and Save Duplicate Groups/Individual](user-guides/configure-id-deduplication-deduplicate-and-save-duplicate-groups-individuals.md)

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

In Social Registry (SR), the data are received and recorded in several ways. SR is dynamically updated via APIs, Service Provider Portal, ODK, Login-based direct data entry, and so on. In order to maintain the data integrity in SR, a process is a must to ensure the uniqueness and accuracy of the recorded registrants' data. SR has a solution/feature named _**Deduplication**_.&#x20;

_**Deduplication**_ is the process that identifies and removes duplicate entries of the recorded registrants' data in SR.&#x20;

## ID-based deduplication

ID-based deduplication is a method that detects duplicates based on unique identifiers i.e., IDs assigned to each recorded registrant belong to an individual/group. This method ensures each ID is distinct and helps to maintain single entry for each recorded registrant. In this way, it eliminates redundancies and keeps the database more reliable, clean, and efficient.

## Feature and functionality

| Deduplication method                           | Deduplication process                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ID-based deduplication - Individual registrant | It detects and removes the duplicate individual registrants.                                                                                                                                                                                                                                                  |
| In-kind-based deduplication - Group registrant | <ul><li>It detects the groups that have the same <a href="../../../pbms/functionality/disbursement-cycles/in-kind-transfer/">In-kind</a> and removes the duplicate groups based on ID.</li><li>It detects the group member has the same In-kind and removes the duplicate group member based on ID.</li></ul> |

## Related user guides

:notebook\_with\_decorative\_cover:[Configure ID Deduplication](user-guides/configure-id-deduplication.md)

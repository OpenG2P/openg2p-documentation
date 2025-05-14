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

# PBMS (Odoo)

The following entities will be defined in PBMS. PBMS will be an Odoo extension.

<mark style="color:blue;">**Programs**</mark>

* Enrolment Cycles
  * Beneficiary Lists
* Eligibility Rules
* Entitlement Rules
* Disbursement Cycles
  * Disbursement Lists

<mark style="color:blue;">**Benefit Codes**</mark>

<mark style="color:blue;">**Agencies**</mark>

* Geo Codes for Agencies
* Benefit Codes for Agencies

The detailed entities, their attributes and user actions are given below

<mark style="color:blue;">**Program**</mark>

| Attribute                      | Description |
| ------------------------------ | ----------- |
| program\_id                    |             |
| program\_mnemonic              |             |
| program\_description           |             |
| target\_registry               |             |
| enrolment\_frequency           |             |
| disbursement\_cycle\_frequency |             |
| disbursement\_                 |             |

Enrolment Cycle

| Attribute                | Description                                                       |
| ------------------------ | ----------------------------------------------------------------- |
| program\_id              | Non Unique Index. One Program will have several enrolment cycles. |
| enrolment\_cycle\_id     | Unique (Private Key)                                              |
| enrolment\_cycle\_number | Integer. Running Serial, starts at 1.                             |
| enrolment\_start\_date   | Date                                                              |
| enrolment\_end\_date     | Date                                                              |
|                          |                                                                   |


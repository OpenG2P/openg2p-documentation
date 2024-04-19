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

# Beneficiary Registry

The concept of a beneficiary registry (BR) involves maintaining a database or record system that contains information about individuals or entities who are beneficiaries of a particular program, service, or assistance. This registry typically includes details such as the beneficiary's identity number, eligibility criteria, participation in programs, entitlements, and any benefits received.

BR resides in PBMS and contains the following&#x20;

* Beneficiary to Program mapping
* Entitlement of beneficiaries
* Status of disbursement

BR may be queried to know about all the programs that a beneficiary is enrolled into.  Further, information on the amount of assistance (cash, in-kind) along with disbursement status may be queried.

Note that BR is different from [Social Registry ](../../../social-registry/)(SR). The following are the differences:

| Beneficiary Registry                                                                                          | Social Registry                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contains data specific to beneficiaries of programs, entitlements and disbursement status                     | Contains demographic data of individuals and groups not necessarily linked to specific programs. The data may be consumed by several applications |
| Data is accessed and managed by Program Managers                                                              | Data is accessed and managed by Admins responsible for social registry management                                                                 |
| Resides inside [PBMS](../../)                                                                                 | Independent registry with its own storage and control. See [Functional Architecture](../../../#functional-architecture).                          |
| Source code: [https://github.com/OpenG2P/openg2p-registry](https://github.com/OpenG2P/openg2p-registry)       | Source code: [https://github.com/OpenG2P/openg2p-social-registry](https://github.com/OpenG2P/openg2p-social-registry)                             |
| Populated by pulling data from SR                                                                             | Populated by several mechanisms as given [here](../../../social-registry/features/registry-update-mechanisms.md).                                 |
| Does not contain PII data\*. Minimal demographic data (only that is required for eligibility and entitlement) | Contains PII data and other demographic data                                                                                                      |

{% hint style="info" %}
\* It is advised not to populate PII data into the BR. However, the platform does not restrict such a usage.&#x20;
{% endhint %}

## Pulling data from SR into BR

TBD

## Sharing BR data

Beneficiary program data can be shared to external systems via APIs.

## Source code

BR is an Odoo based module. Source is available here: [https://github.com/OpenG2P/openg2p-registry](https://github.com/OpenG2P/openg2p-registry)


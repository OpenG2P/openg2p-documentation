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

Note that BR is different from [Social Registry ](../../social-registry/)(SR). The following are the differences:

<table><thead><tr><th width="159">Aspect</th><th>Beneficiary Registry</th><th>Social Registry</th></tr></thead><tbody><tr><td><strong>Data content</strong></td><td>Contains data specific to beneficiaries of programs, entitlements and disbursement status</td><td>Contains demographic data of individuals and groups not necessarily linked to specific programs. The data may be consumed by several applications</td></tr><tr><td><strong>Data management</strong></td><td>Data is accessed and managed by Program Managers</td><td>Data is accessed and managed by Admins responsible for social registry management</td></tr><tr><td><strong>Location</strong></td><td>Resides inside <a href="../">PBMS</a></td><td>Independent registry with its own storage and control. See <a href="../../#functional-architecture">Functional Architecture</a>.</td></tr><tr><td><strong>Source code</strong></td><td> <a href="https://github.com/OpenG2P/openg2p-registry">https://github.com/OpenG2P/openg2p-registry</a></td><td> <a href="https://github.com/OpenG2P/openg2p-social-registry">https://github.com/OpenG2P/openg2p-social-registry</a></td></tr><tr><td><strong>Data population</strong></td><td>Populated by pulling data from SR</td><td>Populated by several mechanisms as given <a href="../../social-registry/features/registry-update-mechanisms.md">here</a>.</td></tr><tr><td><strong>Personally Identifiable Information (PII)</strong></td><td>Does not contain PII data*. Minimal demographic data (only that is required for eligibility and entitlement)</td><td>Contains PII data and other demographic data</td></tr></tbody></table>

{% hint style="info" %}
\* It is advised not to populate PII data into the BR. However, the platform does not restrict such a usage.&#x20;
{% endhint %}

## Pulling data from SR into BR

TBD

## Sharing BR data

Beneficiary program data can be shared to external systems via APIs.

## Source code

BR is an Odoo based module. Source is available here: [https://github.com/OpenG2P/openg2p-registry](https://github.com/OpenG2P/openg2p-registry)


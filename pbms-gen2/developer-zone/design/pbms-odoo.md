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

## Static definitions / configurations

### <mark style="color:blue;">Benefit Codes</mark>

Configure a list of benefit codes (products) that are disbursed by the various programs. Benefit Codes are broadly classified into the following types

* CASH\_DIGITAL — Cash benefits, distributed digitally using direct credits into beneficiary bank accounts or mobile wallets. It is mandatory for Beneficiary financial addresses to be maintained in SPAR (ID-Account Mapper) in case of CASH\_DIGITAL. The Measurement unit for CASH\_DIGITAL will be restricted to ISO Currency codes.
* CASH\_PHYSICAL - Cash benefits, distributed physically. The platform assumes that there will be an agency (service provider) involved in this chain. The Agency will have agents on the ground (field agents) who will physically distribute cash. The department will transfer the required funds to the Agencies by directly transfers into the Agencies' bank accounts. The Measurement unit for CASH\_DIGITAL will be restricted to ISO Currency codes.
* COMMODITY - All physical goods such as staples, books, grains and fuel will come under this category.
* SERVICE - Applicable when the department provides services such as health screenings to the public.
* COMBINATION - Applicable when a benefit includes both a commodity plus a service bundled. E.g. a vaccine will involve a physical vaccine vial plus the service of administering the vaccine.

### Tables involved

1. g2p\_benefit\_codes

### Screens

### <mark style="color:blue;">Program Definition</mark>

You configure the benefit programs which govern the benefit distribution. The key attributes that you define in a benefit program are as follows

1. Target Registry - This attribute indicates the registry from where the beneficiaries' list will be drawn. Mapping a target registry to a program will allow you to define eligibility, priority and entitlement rules using the attributes of the registry. For this, you have to ensure that the target registry is made available as an "ABSTRACT CLASS" in your PBMS Odoo instance.&#x20;









1. Geographic Administrative Zones - Large
2. Geographic Administrative Zones - Small
3. Agencies
4. Warehouses






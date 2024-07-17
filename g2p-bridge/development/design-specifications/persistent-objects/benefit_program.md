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

# benefit\_program\_configuration

This is a configuration table that stores account details (with sponsor banks) for a benefit program.&#x20;

The design assumes that every benefit program has exactly one financial account with a sponsor bank.&#x20;

The design caters for the following thought process

1. Multiple programs exist and share the same funding account
2. Multiple programs exist with each program using a dedicated funding account in the same FSP (financial service provider / Bank)
3. Multiple programs exist with programs using different funding accounts across different FSPs



| Attribute                        | Description                                                                                                                                                                                                                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| benefit\_program\_mnemonic       | Uniquely identifies a benefit program. Is Primary Key.                                                                                                                                                                                                                                     |
| benefit\_program\_name           | Describes the benefit program                                                                                                                                                                                                                                                              |
| funding\_org\_code               | The Government department or Social Welfare organization that administers this program - Short Code                                                                                                                                                                                        |
| funding\_org\_name               | Name of the Organization corresponding to the short code                                                                                                                                                                                                                                   |
| sponsor\_bank\_code              | Financial Service Provider - Institution - where the account is maintained - The account that funds the program                                                                                                                                                                            |
| sponsor\_bank\_branch\_code      | The branch code - where the funding account is maintained                                                                                                                                                                                                                                  |
| sponsor\_bank\_account\_number   | <p>Complete account number (financial address) with Bank Code,  Branch Code, any other identifier as required<br><br><mark style="color:blue;"><strong>Unique Index</strong></mark><br><br>Every benefit program needs to be funded by a dedicated funding account with a sponsor bank</p> |
| sponsor\_bank\_account\_currency | The currency in which the account (the funding account) is maintained                                                                                                                                                                                                                      |
| id\_mapper\_resolution\_required | <p>TRUE / FALSE<br>Specifies whether Beneficiary ID will travel to Sponsor Bank<br>OR<br>Beneficiary ID will be translated to Account Number (Financial Address) and then travel downstream to Sponsor Bank</p>                                                                            |

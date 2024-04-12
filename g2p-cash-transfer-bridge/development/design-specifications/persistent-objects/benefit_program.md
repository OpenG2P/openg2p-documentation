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

# benefit\_program

This is a configuration table that stores account details (with sponsor banks) for a benefit program.&#x20;

The design assumes that every benefit program has exactly one financial account with a sponsor bank.&#x20;

The design caters for the following thought process multiple programs sharing a single financial account.

1. Multiple programs exist and share the same funding account
2. Multiple programs exist with each program using a dedicated funding account in the same FSP (financial service provider / Bank)
3. Multiple programs exist with programs using different funding accounts across different FSPs



| Attribute                  | Description                                                                                                     |
| -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| benefit\_program\_mnemonic | Uniquely identifies a benefit program. Is Primary Key.                                                          |
| benefit\_program\_name     | Describes the benefit program                                                                                   |
| funding\_org\_code         | The Government department or Social Welfare organization that administers this program - Short Code             |
| funding\_org\_name         | Name of the Organization corresponding to the short code                                                        |
| funding\_sub\_org\_code    | If there are sub departments under the Organization/Department, the short code of the sub org                   |
| funding\_sub\_org\_name    | Name of the Sub Organization corresponding to the sub org short code                                            |
| fsp\_institution\_code     | Financial Service Provider - Institution - where the account is maintained - The account that funds the program |
| fsp\_account\_number       | Complete account number (financial address) with Bank Code,  Branch Code, any other identifier as required      |

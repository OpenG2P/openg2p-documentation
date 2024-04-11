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

The design assumes that every benefit program has exactly one financial account with a sponsor bank. The design also caters for multiple programs sharing a single financial account.



| Attribute                  | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| benefit\_program\_mnemonic | Uniquely identifies a benefit program. Is Primary Key. |
| benefit\_program\_name     | Describes the benefit program                          |
| funding\_org\_code         |                                                        |
| funding\_org\_name         |                                                        |
| funding\_sub\_org\_code    |                                                        |
| funding\_sub\_org\_name    |                                                        |
| fsp\_institution\_code     |                                                        |
| fsp\_branch\_code          |                                                        |
| fsp\_account\_number       |                                                        |

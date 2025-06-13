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

# create\_benefit\_program\_configuration

| API Attributes |                                 |
| -------------- | ------------------------------- |
| Direction      | Inward                          |
| Invoked by     | PBMS                            |
| Mode           | Synchronous                     |
| Tables         | benefit\_program\_configuration |

This API accepts the benefit program configuration and creates a new benefit program configuration by supplying the program details, funding org, sponsor bank details, etc.

## Object design

### benefit\_program\_configuration

| Attribute                        | Datatype                                                                                  |
| -------------------------------- | ----------------------------------------------------------------------------------------- |
| benefit\_program\_mnemonic       | String – Unique code that identifies this benefit program. (Unique Constraint)            |
| benefit\_program\_name           | String – Full name of the benefit program. (Not nullable)                                 |
| funding\_org\_code               | String – Code of the organization providing funding. (Not nullable)                       |
| funding\_org\_name               | String – Full name of the organization providing funding. (Not nullable)                  |
| sponsor\_bank\_code              | String – Bank code of the sponsoring bank. (Not nullable)                                 |
| sponsor\_bank\_account\_number   | String – Account number at the sponsoring bank. (Not nullable)                            |
| sponsor\_bank\_branch\_code      | String – Branch code of the sponsoring bank. (Not nullable)                               |
| sponsor\_bank\_account\_currency | String – Currency of the sponsoring bank account (e.g., USD, EUR). (Not nullable)         |
| id\_mapper\_resolution\_required | Boolean – Flag indicating whether ID‐mapping resolution is required. (Defaults to `True`) |

### Validations & exceptions

1. Configuration must be unique (no existing config for the same mnemonic)
2. All required fields are present and non‐empty
3. Sponsor-bank account currency matches the program’s disbursement currency

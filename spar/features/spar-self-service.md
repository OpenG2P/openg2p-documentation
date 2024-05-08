---
description: Providing Self Service features for the beneficiaries
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# SPAR Self Service

The SPAR Self Service has two components - viz.

1. SPAR Self Service - Microservice - Serving REST APIs
2. SPAR Self Service - UI

The **SPAR Self Service Microservice** offers the following features

* Integration with an OIDC-OAuth2.0 Login Provider
* A Directory of all the financial institutions and their branches - to facilitate a beneficiary to define his/her full financial address
* Strategy definitions (Construct & De-Construct) to construct Financial Address using the various attributes -
  * Bank Name, Bank Code, Branch Code, Branch Name and Account Number in case of Bank Accounts
  * Wallet Provider Code, Wallet Provider Name, Email Address and Phone Number in case of Wallets

The **SPAR Self Service UI** - is a reference UI (based on ReactJS). The government department can use this UI and create an implementation based on its UI strategy.

* The SPAR Self Service UI provides a search functionality for Banks & their Branches, Wallet Providers - to enable a beneficiary&#x20;
* The UI also allows a beneficiary to log in and change his/her destination account (or wallet) any number of times





&#x20;

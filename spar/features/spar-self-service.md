---
description: Providing self-update features for beneficiaries via the Beneficiary Portal API
---

# SPAR Beneficiary Portal

The SPAR Beneficiary Portal lets beneficiaries view and update their own
financial address in the registry. From v2.0 it is delivered as a single
**API-only** component — `openg2p-spar-bene-portal-api` — that replaces the
earlier Self-Service API + ReactJS UI. Implementing organizations build (or
integrate) their own front-end on top of these APIs.

The **Beneficiary Portal API** offers the following features:

* Integration with an OIDC-OAuth2.0 Login Provider (the beneficiary logs in with their National ID).
* A directory of all the financial institutions and their branches - to facilitate a beneficiary to define his/her full financial address.
* Strategy definitions (Construct & De-Construct) to construct a Financial Address using the various attributes -
  * Bank Name, Bank Code, Branch Code, Branch Name and Account Number in case of Bank Accounts
  * Wallet Provider Code, Wallet Provider Name, Email Address and Phone Number in case of Wallets
* Search APIs for Banks & their Branches and Wallet Providers, so a beneficiary can construct their complete financial address.
* APIs that allow a beneficiary to log in and change their destination account (or wallet) any number of times.

The simplified DFSP model behind these APIs uses three entity types: **BANK**,
**BRANCH** and **WALLET-PROVIDER**.

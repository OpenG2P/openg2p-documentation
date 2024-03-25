---
description: Functional features provided by the SPAR subsystem
---

# Features

* **ID-Account Mapper**
  * Mapping of ID to FA.
  * Many-to-one and one-to-one mapping of ID to FA.
  * Multiple IDs may be added for the same user
  * Bulk upload by Admin or FSPs like bank, or Govt Department after authentication
  * [G2P Connect Compliant APIs](https://g2pconnect.cdpi.dev/protocol/interfaces/beneficiary-management/mapper-specs) to query and update Financial Address
  * Signature verification for clients (partners)  via integrations with MOSIOP's Partnermanager & Keymanager (TBD)
* **Self Service Portal**
  * Login via National ID (using [eSignet](https://docs.esignet.io/) or any OIDC / OAuth2.0 compliant authentication provider)
  * Easy to use User Interface - Search for Banks, Search for Branches, Search for Mobile Service Providers to facilitate definition of the complete Financial Address of a Beneficiary

### Concept

#### ID Account Mapper

* Database of ID and FA. The IDs may be tokens like [PSUT in MOSIP](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id-psut-partner-specific-user-token)
* Can host multiple IDs associated with the same account. Eg.

<table><thead><tr><th width="382.5">ID</th><th>Account Number</th></tr></thead><tbody><tr><td>234AFBC@mosip.openg2p</td><td>45678756456@ABC-Bank</td></tr><tr><td>DBCF34A@mosip.socialaccountregistry</td><td>45678756456@ABC-Bank</td></tr></tbody></table>

#### Self Service Portal

Service to enable beneficiaries login into SPAR and update their respective Financial Address (Account Details).

To enable this, the self service portal provides the following features via. its authentication services. Authentication is provided through eSignet or any other OIDC compliant authorization providers. With the Self Service portal, beneficiaries can view and update their Financial Address anytime. Any update to this Financial Address information results in a SMS/SMTP notification to the beneficiary.

---
description: Provides a functional overview of the SPAR subsystem
---

# Functional Overview

The following picture represents how SPAR fits into the overall OpenG2P Project Landscape

<figure><img src="../../.gitbook/assets/Gitbook-SPAR-Landscape.jpg" alt=""><figcaption><p>SPAR in the OpenG2P landscape</p></figcaption></figure>

The Government Department administers its benefit program in the OpenG2P PBMS platform. The PBMS platform manages benefit programs, beneficiaries under the programs, disbursement cycles and entitlements (rules & definitions).

At the end of every disbursement cycle of a given benefit program, the PBMS platform produces a list that contains all the beneficiaries and their individual disbursements. The beneficiaries in that list are identified by a Beneficiary ID. This ID might be a National ID, that uniquely identifies a beneficiary in the country or depending on the National ID implementation in the country can also be a proxy or a token that has been issued by the National ID Registry.

This List has to be presented to the Sponsor Bank, where the Government Department has its Money Account (Financial Account) that contains the funds required to fund these disbursements.

The Sponsor Bank in turn has to present this List to the National Clearing System. The National Clearing List will in turn split this list into multiple lists that will be presented to multiple destination banks in the country.

Somewhere in this G2P Disbursement Chain, the Beneficiary ID needs to be translated to the Beneficiary's Financial Address

1. 1.Beneficiary Account Number + Bank/Branch Address - in case of Bank Accounts
2. 2.Beneficiary Mobile Number + Mobile Service Provider - in case of Wallets

This mapping between the Beneficiary ID and his Financial Address is maintained by SPAR. SPAR provides a lookup referral service by which any participant in the G2P chain can perform a lookup into SPAR and obtain the financial address for a given beneficiary ID. The three blue dotted arrows (1, 2 & 3) in the above picture represents this lookup.

Depending on the implementation, we can decide which layer in the G2P chain performs this lookup and enriches the disbursement list that was originally produced by the PBMS  system.

The following figure provides a Functional Architecture of the SPAR Subsystem.

<figure><img src="../../.gitbook/assets/Gitbook-SPAR-Functional-Architecture.jpg" alt=""><figcaption><p>SPAR Functional Architecture</p></figcaption></figure>

## Functionality and features

* **ID-Account Mapper**
  * Mapping of ID to FA.
  * Many-to-one and one-to-one mapping of ID to FA.
  * Multiple IDs may be added for the same user
  * Bulk upload by Admin or FSPs like bank, or Govt Department after authentication
  * [G2P Connect Compliant APIs](https://g2pconnect.cdpi.dev/protocol/interfaces/beneficiary-management/mapper-specs) to query and update Financial Address
  * Signature verification for clients (partners)  via integrations with MOSIOP's Partnermanager & Keymanager (TBD)
* **Self Service Portal**
  * Login via National ID (using [eSignet](https://docs.esignet.io/))
  * Easy to use User Interface - Search for Banks, Search for Branches, Search for Mobile Service Providers to facilitate definition of the complete Financial Address of a Beneficiary

## Concept

### ID Account Mapper

* Database of ID and FA. The IDs may be tokens like [PSUT in MOSIP](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id-psut-partner-specific-user-token)
* Can host multiple IDs associated with the same account. Eg.

<table><thead><tr><th width="368.5">ID</th><th>Account Number</th></tr></thead><tbody><tr><td>234AFBC@mosip.openg2p</td><td>45678756456@ABC-Bank</td></tr><tr><td>DBCF34A@mosip.socialaccountregistry</td><td>45678756456@ABC-Bank</td></tr></tbody></table>

* If relationships between entries are supported in the DB, then the same can be used to show linkages between different IDs for a user (TBD)

### Self Service Portal

Service to enable beneficiaries login into SPAR and update their respective Financial Address (Account Details).

To enable this, the self service portal provides the following features via. its authentication services. Authentication is provided through eSignet or any other OIDC compliant authorization providers. With the Self Service portal, beneficiaries can view and update their Financial Address anytime. Any update to this Financial Address information results in a SMS/SMTP notification to the beneficiary.

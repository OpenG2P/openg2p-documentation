# Social Account Registry (SAR)

## Architecture

The Social Account Registry (SAR) maintains a mapping of a user ID and Financial Service Provider (FSP) account details like bank, mobile wallet etc. primarily aimed at cash transfers in a social benefit delivery system. The SAR offers a user-facing portal for adding/updating FSP account details after authentication.

<figure><img src="https://raw.githubusercontent.com/OpenG2P/openg2p-documentation/1.1/.gitbook/assets/social-account-registry.png" alt=""><figcaption></figcaption></figure>

\
PSUT: Partner Specific User Token

{% hint style="info" %}
The SAR will be compliant with [G2P Connect interfaces](https://github.com/G2P-Connect/specs/blob/draft/api/g2p-mapper.yaml) and eventually, evolve into [ID Account Mapper](https://g2pconnect.cdpi.dev/protocol/interfaces/beneficiary-management/mapper-architecture) as envisaged by CDPI \

{% endhint %}

## Sunbird Account Mapper

* Account mapper compliant to the G2P Connect interface
* Database of ID and Account Numbers. The IDs may be tokens like [PSUT in MOSIP.](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id-psut-partner-specific-user-token)
* Can host multiple IDs associated with the same account. Eg.&#x20;



| ID                                  | Account Number |
| ----------------------------------- | -------------- |
| 234AFBC@mosip.openg2p               | 45678756456    |
| DBCF34A@mosip.socialaccountregistry | 45678756456    |

* If relationships between entries is supported in Sunbird, then the same can be used to show linkages between different IDs for a user.

## Mapper Service

Service to manage several mapping related tasks and provide APIs for users to connect and update their account numbers.

### Authentication

* Authentication page leading to e-Signet interface.
* Display of current account number of the user.
* Option to add/update the account number and account details.
* Notification to users via email/sms
* Onboarding of authenticators like e-Signet.

### Onboarding&#x20;

Onboarding of consumer apps (like OpenG2P)

### ID linking

* Linking of SAR PSUT with Application PSUT.
* Consent page for users to map token for a time period specifically for an app (like OpenG2P)
* Automatic deletion of records based on expiry set
* Notification to the user via SMS/email
* Maintaining linkage status (reflected on the portal for the user)

### Expiry handling

* TBD&#x20;

### Account validation&#x20;

A suggested way to validate the user account number is to initiate a small cash transfer from the treasury account to the person's account. Upon successful transfer (as communicated by the bank) consider the account mapper entry valid. This could take several minutes to hours as it depending on the response from the bank.&#x20;

Configuration: Treasury account details&#x20;

## Self Service Portal

* Front end service for Web based user interface to carry out above functions





##

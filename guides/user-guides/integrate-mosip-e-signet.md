# Integrate MOSIP e-Signet

## Description

This guide provides steps to integrate [OpenG2P with MOSIP-eSignet](../../integrations/integration-with-mosip/integration-with-e-signet.md). The entire configuration is accomplished by the following actors:

1. MOSIP Partner Admin
2. OpenG2P Admin

## Pre-requisites

* MOSIP IDA is installed
* The e-Signet server is installed and configured to connect to MOSIP IDA
* MOSIP IDA APIs are accessible from the machine running the e-Signet server
* Both Yes/No and KYC APIs are enabled on MOSIP IDA
* e-Signet APIs are accessible from machines running OpenG2P
* Biometric auth devices (already onboarded on MOSIP) are available for authentication
* Email and SMS are enabled on MOSIP IDA for OTP authentication
* MOSIP Partner Management Services (PMS) Portal or APIs must be accessible to both MOSIP Partner Admin and OpenG2P Admin

## Steps

### Configure OpenG2P as a partner on MOSIP

* [Guide](https://docs.mosip.io/1.2.0/modules/partner-management-services/auth-credential-partner) for MOSIP 1.2.0
* Guide for MOSIP 1.1.5 (TBD)

Note down the Partner ID and Policy ID from the above steps.

### Configure OpenG2P as relying party on e-Signet

These steps are executed by MOSIP Partner Admin

1. Create an e-Signet OIDC client using PMS OIDC API:

{% swagger src="../../.gitbook/assets/pms-api-docs.json" path="/oidc/client" method="post" %}
[pms-api-docs.json](../../.gitbook/assets/pms-api-docs.json)
{% endswagger %}

* `authParnterId:` Partner ID in [this](integrate-mosip-e-signet.md#configure-openg2p-as-a-partner-on-mosip) step.&#x20;
* `policyId` : Policy ID in [this](integrate-mosip-e-signet.md#configure-openg2p-as-a-partner-on-mosip) step.
* `publicKey:` Generate [JWK](https://openid.net/specs/draft-jones-json-web-key-03.html).
* `logoUri`: URL of your logo accessible publicly.
* &#x20;`grantTypes` = `["authorization_code"]`
* `clientAuthMethods`= `["private_key_jwt"]`
* `redirectUris`:  URLs of the form `https://<your web portal>/auth_oauth/signin`

Note down the Client ID as an output of the above step.

### Enable e-Signet on OpenG2P

These steps are executed by OpenG2P Admin on the OpenG2P Admin interface.

1. Go to _Settings -> General Settings (Menu) -> General Settings (Panel) -> Integrations (Section) -> Oauth Providers_

<figure><img src="../../.gitbook/assets/settings-admin-oauth.png" alt=""><figcaption></figcaption></figure>

<figure><img src="../../.gitbook/assets/create-esignet-client.png" alt=""><figcaption></figcaption></figure>

2. Create a new OIDC Provider with the following details:

| Parameter                                | Value                                                                                                                                      |                                                                                                                                               |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Client ID                                | _The_ _output_ _of the_ [previous section](integrate-mosip-e-signet.md#configure-openg2p-as-relying-party-on-e-signet).                    |                                                                                                                                               |
| Auth Flow                                | OpenID Connect (authorization code flow)                                                                                                   |                                                                                                                                               |
| Token map                                | sub:user\_id                                                                                                                               |                                                                                                                                               |
| Client Authentication Method             | Private Key JWT                                                                                                                            |                                                                                                                                               |
| Private Key Method                       | _Private key used for JWK creation in the_ [previous section](integrate-mosip-e-signet.md#configure-openg2p-as-relying-party-on-e-signet). |                                                                                                                                               |
| Assertion Type                           | JWT Bearer                                                                                                                                 |                                                                                                                                               |
| Authorization URL                        | e-S_ignet's authorize endpoint._                                                                                                           |  Example: [https://esignet.mec.mosip.net/authorize](https://esignet.mec.mosip.net/authorize)                                                  |
| Userinfo URL                             | e-S_ignet's userinfo API_                                                                                                                  | Example: [https://api.mec.mosip.net/v1/esignet/oidc/userinfo](https://api.mec.mosip.net/v1/esignet/oidc/userinfo)                             |
| Token URL                                | _e-Signet's token API_                                                                                                                     | Example: [https://api.mec.mosip.net/v1/esignet/oauth/token](https://api.mec.mosip.net/v1/esignet/oauth/token)                                 |
| JWKS URL                                 | _e-Signet's JWKS API_                                                                                                                      | Example: [https://api.mec.mosip.net/v1/esignet/oauth/.well-known/jwks.json](https://api.mec.mosip.net/v1/esignet/oauth/.well-known/jwks.json) |
| Use G2P Reg ID                           | True                                                                                                                                       |                                                                                                                                               |
| G2P Registrant ID Type                   | _Pre configured ID Type for MOSIP PSUT on OpenG2P_                                                                                         |                                                                                                                                               |
| Partner Creation Call Validate URL       | True                                                                                                                                       | Specifies whether to call the MOSIP e-KYC API to fetch data into OpenG2P                                                                      |
| Partner Creation Validate Response       | name:name email:email phone:phone\_number birthdate:birthdate gender:gender address:address                                                |                                                                                                                                               |
| Default Group User Creation              | User types / Portal                                                                                                                        | Specifies all users signing up through this OIDC Provider (e-Signet) are only going to be portal users                                        |
| Login Attribute Mapping On User Creation | email                                                                                                                                      | To allow users to sign in with their email and password after initial signup with e-Signet.                                                   |


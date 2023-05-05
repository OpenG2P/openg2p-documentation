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

### Enable e-Signet on OpenG2P

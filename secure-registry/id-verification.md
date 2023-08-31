# ID Verification

## Introduction

OpenG2P registration interfaces can be integrated with OIDC clients and ID authentication systems to authenticate applicants/registrants. OpenG2P employs different ID authentication mechanisms in its registration interfaces. While these are the preferred mechanisms, OpenG2P is not tied to these mechanisms and can integrate with other OIDC-compliant clients and authentication systems like the National ID database.

## Registrant authentication using MTS

OpenG2P integrates with MOSIP Token Seeder (MTS) using MTS Connector to authenticate registrants registered using the ODK Collect App. The Unique ID Number (UIN) and demographic details provided by registrants are verified by calling APIs of the [MOSIP ID Authentication](https://docs.mosip.io/1.2.0/id-authentication) (IDA) system. The MOSIP IDA responds with an Authentication Token upon successful verification. MTS is a standalone service offered by MOSIP. Learn more about MOSIP integration [here](../integrations/integration-with-mosip.md).

MTS Connectors can take inputs from both ODK Central and OpenG2P registry. Since one MTS Connector takes only one type of input, separate MTS connectors are required for ODK Central and OpenG2P registry. Learn more about OpenG2P registry MTS Connectors [here](../integrations/integration-with-mosip/registry-mts-connector.md).

A high-level representation of the interactions between different components during authentication is shown below:

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/a8a98c86cd7b0a186213e588d8642aac12eb64a6/.gitbook/assets/authentication-using-mts.png" alt=""><figcaption></figcaption></figure>

## Applicant authentication using e-Signet&#x20;

OpenG2P's Self-Service Portal can be integrated with an OpenID Connect Client such as e-Signet to build a trustworthy authentication interface. The OIDC Client utilizes an authentication system such as MOSIP or National ID database to authenticate the applicants in the backend.&#x20;

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/e9fdceeedd6e483eb45098b9a72f013a331451cf/.gitbook/assets/authentication-using-esignet.png" alt=""><figcaption></figcaption></figure>

A few key points to note in this process are:

* The challenge could be OTP, biometric, or QR code.
* The applicant shares the UIN, challenge, and consent via the authentication client.
* The Self-Service Portal must get an Authorization Code before requesting the Access Token.
* The Self-Service Portal gets access to the applicant's details after it receives the Access Token from the authentication system.
* &#x20;UIN, challenge, and consent are shared in separate transactions. To view the e-Signet authentication process in detail, click [here](../integrations/integration-with-mosip/integration-with-e-signet.md).

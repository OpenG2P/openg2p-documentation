# ID Verification

## Introduction

OpenG2P registration interfaces can be integrated with OIDC (OpenID Connect) clients and ID authentication systems to authenticate registrants. OpenG2P employs different ID authentication mechanisms in its registration interfaces. While these are the preferred mechanisms, OpenG2P is not tied to these mechanisms and can integrate with other OIDC-compliant clients of authentication systems for foundational/functional ID.

### Authenticate Registrant using OpenID Connect

OpenG2P's Self-Service Portal can be integrated with an OIDC Client such as e-Signet to build a trustworthy authentication interface. The OIDC Client utilizes an authentication system of any foundational or functional ID database to authenticate the registrants in the backend.

\<image to be incorporated>

A few key points to note in this process are:

* The challenge could be OTP, biometric, or QR code.
* The registrant shares the UIN, challenge, and consent via the authentication client.
* The Self-Service Portal must get an Authorization Code before requesting the Access Token.
* The Self-Service Portal gets access to the registrant's details after it receives the Access Token from the authentication system.
* UIN, challenge, and consent are shared in separate transactions. To view the e-Signet authentication process in detail, click [here](broken-reference).

### Authenticate Registrant using ID Authentication

OpenG2P integrates with MOSIP Token Seeder (MTS) using MTS Connector to authenticate registrants registered using the ODK Collect App. The Unique ID Number (UIN) and demographic details provided by registrants are verified by calling APIs of the [MOSIP ID Authentication](https://docs.mosip.io/1.2.0/id-authentication) (IDA) system. The MOSIP IDA responds with an Authentication Token upon successful verification. MTS is a standalone service offered by MOSIP. Learn more about MOSIP integration [here](broken-reference).

\<the link is broken, hyperlink MOSIP integration>

MTS Connectors can take inputs from both ODK Central and OpenG2P registry. Since one MTS Connector takes only one type of input, separate MTS connectors are required for ODK Central and OpenG2P registry. Learn more about OpenG2P registry MTS Connectors [here](broken-reference).

\<the link is broken, hyperlink the MTS connectors>

A high-level representation of the interactions between different components during authentication is shown below:

\<image to be incorporated>

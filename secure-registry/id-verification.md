# ID Verification

## Introduction

At the backend, the ID provided (functional or foundational) during registration is verified by submitting the demographic details and ID number by calling APIs of the corresponding ID system. The response from the ID system could be a _yes/no_ response with optional data like ID tokens and KYC details.

## Authentication using MOSIP ID/National ID

OpenG2P registration systems can be integrated with e-Signet to build a trustworthy authentication interface. The platform utilizes an authentication system like MOSIP or National ID to authenticate the applicants and registrants in the backend.&#x20;

<figure><img src="../.gitbook/assets/id-authentication (1).png" alt=""><figcaption></figcaption></figure>

A few key points to note in this process are:

* The challenge could be OTP, biometric, or QR code.
* Applicant/registrant will share the UIN, challenge, and consent only via the authentication client.
* The registration system has to be authorized via an Authorization Code before it can request the Access Token.
* The registration system will get access to the applicant/registrant details after it receives the Access Token from the authentication system.
* &#x20;UIN, challenge, and consent are shared in separate transactions. To view the e-Signet authentication process in detail, click [here](../integrations/integration-with-mosip/integration-with-e-signet.md).

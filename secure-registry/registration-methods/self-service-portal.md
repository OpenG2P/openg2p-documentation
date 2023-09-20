# Self Service Portal

## Introduction

Self-Service Portal allows a registrant seeking assistance to register from any place and device with internet connectivity. The registrant logs in using a foundational or functional ID and then applies for a program. For self-registration,  an OTP or QR code is typically used in addition to a unique ID number for logging in. For assisted registration, the assisting officer uses a biometric device connected to the machine hosting the Self-Service Portal for biometric authentication.

The Self-Service Portal registration process assumes that an authentication service is available for ID verification. The portal allows an individual to perform the following functions:

* View a list of available programs
* Apply for a new program
* Track the status of the application
* Update demographic information
* Upload supporting documents
* View the programs the registrant is enrolled into&#x20;
* View all the demographic information submitted across programs

Depending on the program implementation, the registrant can also apply for the same program multiple times to seek assistance multiple times. An example of such a case is seeking medical assistance for different treatments. It is assumed that program administrators will apply mechanisms to prevent cases of double-dipping.

## Registration process

A program administrator has to carry out these steps to allow registrants to apply for a program:

* Create a program: To learn the steps, click [here](../../guides/user-guides/create-a-program.md).
* Create a Self-Service Portal form: To learn the steps, click [here](../../guides/user-guides/create-portal-form.md).
* Map Self-Service Portal form: To learn the steps, click [here](../../guides/user-guides/map-self-service-portal-form.md).

Registrant's ID verification takes place during the login. The registrant also provides consent to share demographic details with the Self-Service Portal. Upon successful ID verification, the Self-Service Portal can automatically fill in the registrant's demographic details based on the consent provided during login. The registrant fills in the rest of the details and applies for a program. Learn more about self-registration [here](../../guides/user-guides/self-register-online.md).

## OpenID Connect integration

The Self-Service Portal allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with [e-Signet](https://docs.esignet.io/). To learn more about ID verification using e-Signet, click [here](../id-verification.md#applicant-authentication-using-e-signet).

### OIDC integration

The Self-Service Portal can integrate with any OIDC server to provide user login.

<figure><img src="../../.gitbook/assets/integration-with-oidc (1).png" alt=""><figcaption></figcaption></figure>

## Registration demo

{% embed url="https://www.youtube.com/watch?v=DZweP3qKkn8" %}

## How-To Guides

* [Create Program](../../guides/user-guides/create-a-program.md)
* [Create Self-Service Portal Form](../../guides/user-guides/create-portal-form.md)
* [Map Self-Service Portal Form](../../guides/user-guides/map-self-service-portal-form.md)
* [Self Register Online](../../guides/user-guides/self-register-online.md)

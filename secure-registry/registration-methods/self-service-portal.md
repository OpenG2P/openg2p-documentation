# Self Service Portal

## Introduction

Self-Service Portal allows an applicant seeking assistance to register from any place with internet connectivity. The applicant logs in using a foundational or functional ID and then applies for a program. For self-registration, typically, OTP or QR code is used in addition to a unique ID number for logging in. For assisted registration, typically, the assisting officer uses a biometric device connected to the machine hosting Self-Service Portal for biometric authentication.

The Self-Service Portal registration process assumes that an authentication service is available for ID verification. The portal allows an individual to perform the following functions:

* View a list of available programs
* Apply for a new program
* Track the status of the application
* Update demographic information
* View the programs the applicant is enrolled into&#x20;
* View all the demographic information submitted across programs

## Registration process

A program administrator has to carry out these steps to allow applicants to apply for a program:

* Create a program: To learn the steps, click [here](../../guides/user-guides/create-a-program.md).
* Create a Self-Service Portal form: To learn the steps, click [here](../../guides/user-guides/create-portal-form.md).
* Map Self-Service Portal form: To learn the steps, click [here](../../guides/user-guides/map-self-service-portal-form.md).

Applicant's ID verification takes place during the log-in. The applicant also provides consent to share demographic details with the Self-Service Portal. Upon successful ID verification, the Self-Service Portal can automatically fill in the applicant's demographic details based on the consent provided at the time of log-in. The applicant fills in the rest of the details and applies for a program. Learn more about self-registration [here](../../guides/user-guides/self-register-online.md).

## OpenID Connect integration

Self-Service Portal allows integration with any OpenID Connect (OIDC) client.  The portal has an existing integration with [e-Signet](https://docs.esignet.io/). Learn more about ID verification using e-Signet [here](../id-verification.md#applicant-authentication-using-e-signet).

### MOSIP integration

The Self-Service Portal also integrates with MOSIP to provide user login via MOSIP ID.

<figure><img src="../../.gitbook/assets/ssp-login-page (1).png" alt=""><figcaption></figcaption></figure>

## Registration demo

{% embed url="https://www.youtube.com/watch?v=DZweP3qKkn8" %}

## How-To Guides

* [Create Program](../../guides/user-guides/create-a-program.md)
* [Create Self-Service Portal Form](../../guides/user-guides/create-portal-form.md)
* [Map Self-Service Portal Form](../../guides/user-guides/map-self-service-portal-form.md)
* [Self Register Online](../../guides/user-guides/self-register-online.md)

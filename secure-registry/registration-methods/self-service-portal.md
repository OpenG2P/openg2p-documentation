# Self Service Portal

## Introduction

OpenG2P offers a reference implementation for an applicant-facing interface named Self Service Portal where an applicant can log in using UIN or any similar foundational or functional ID and then apply for a program. In self-service mode, typically, OTP or QR code is used in addition to a unique ID number for logging in. In assisted mode, typically, the assisting officer has biometric devices connected to the machine hosting Self-Service Portal for biometric authentication.

The Self-Service Portal registration process assumes that an authentication service is available for ID verification. The portal allows an individual to perform the following functions:

* View enrolled programs
* View all the demographic information submitted across programs
* Update demographic information
* Apply for a new program
* View a list of all programs offered by the government/ministry/department.

## Registration process

A program administrator has to carry out these steps to allow applicants to apply for a program:

* [Create a program](../../guides/user-guides/create-a-program.md)
* [Create a Self-Service Portal form](../../guides/user-guides/create-portal-form.md)
* [Map Self-Service Portal form](../../guides/user-guides/map-self-service-portal-form.md)

Applicant's ID verification takes place during the log-in. The applicant also provides consent to share demographic details with the Self-Service Portal. Upon successful ID verification, the Self-Service Portal can automatically fill in the applicant's demographic details based on the consent provided at the time of log-in. The applicant fills in the rest of the details and applies for a program. Learn more about self-registration [here](../../guides/user-guides/self-register-online.md).

## OpenID Connect integration

Self-Service Portal allows integration with any OpenID Connect (OIDC) client.  The portal has an existing integration with [e-Signet](https://docs.esignet.io/). Learn more about ID verification using e-Signet [here](../id-verification.md#applicant-authentication-using-e-signet).

### MOSIP integration

The Self-Service Portal also integrates with MOSIP to provide user login via MOSIP ID.

<figure><img src="../../.gitbook/assets/ssp-login-page (1).png" alt=""><figcaption></figcaption></figure>

## Registration demo

{% embed url="https://www.youtube.com/watch?v=DZweP3qKkn8" %}

## References

* [Create a Self-Service Portal form](../../guides/user-guides/create-portal-form.md)
* [Map Self-Service Portal form](../../guides/user-guides/map-self-service-portal-form.md)
* [Self-register online](../../guides/user-guides/self-register-online.md)
* [ID verification using e-Signet](../id-verification.md#applicant-authentication-using-e-signet)

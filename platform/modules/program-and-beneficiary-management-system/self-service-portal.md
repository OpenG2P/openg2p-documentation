# Self Service Portal

## Introduction

Self-Service Portal allows a registrant seeking assistance to register from any place and any device with internet connectivity. The registrant logs in using a foundational or functional ID and then applies for a program. For self-registration, an OTP or QR code is typically used in addition to a unique ID number to log in. For assisted registration, to do biometric authentication, the assisting officer uses a biometric device connected to a machine which has access to Self-Service Portal.

The Self-Service Portal registration process assumes that an authentication service is available for ID verification. The portal allows an individual to perform the following functions:

* View a list of available programs
* Apply for a new program
* Track the status of the application
* Update demographic information
* Upload supporting documents
* View the registrant's enrolled programs
* View all the demographic information submitted across programs

Depending on the program implementation, the registrant can seek assistance to apply for the same program multiple times. For example, a registrant seeks medical assistance for different treatments. It is assumed that Program administrators will apply mechanisms to prevent cases of double-dipping.

## Registration process

A program administrator must do these steps to allow registrants to apply for a program:

* Create a program: To learn the steps, click [here](../../../user-guides/platform-guides/registration/eligibility-and-program-enrollment/program/create-a-program.md).
* Create a Self-Service Portal form: To learn the steps, click [here](../../../user-guides/platform-guides/registration/eligibility-and-program-enrollment/website/create-portal-form.md).
* Map Self-Service Portal form: To learn the steps, click [here](../../../user-guides/platform-guides/registration/eligibility-and-program-enrollment/program/map-self-service-portal-form.md).

Registrant's ID verification takes place during the login. The registrant also provides consent to share demographic details with the Self-Service Portal. Upon successful ID verification, the Self-Service Portal can automatically populates the registrant's demographic details based on the consent provided during login. The registrant fills in the rest of the details and applies for a program. Learn more about self-registration [here](../../../user-guides/platform-guides/registration/self-register-online.md).

## OpenID Connect integration

The Self-Service Portal allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with [eSignet](https://docs.esignet.io/). To learn more about ID verification using e-Signet, click [here](broken-reference).

### OIDC integration

The Self-Service Portal can integrate with any OIDC server to provide user login.

\<image and demo video to be integrated>

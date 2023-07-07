# Self Service Portal

## Introduction

OpenG2P offers the on-demand approach via the Self Service Portal where a person logins via his/her ID and then applies for a program. In self-service mode, typically, OTP would be used for login. In assisted mode, the registering officer may have biometric devices connected to his/her machine, and the registrant can perform biometric authentication in an online manner.&#x20;

Online registration assumes that an ID verification service is available to connect via APIs and perform verification of the identity of a person. In the case of MOSIP, for e.g, the verification can be done using the [e-Signet](https://docs.mosip.io/1.2.0/integrations/e-signet) solution.

OpenG2P offers a _reference implementation_ of a person facing Self Service Portal that lets a person log in to the portal using a national ID or other IDs, and perform the following functions:

* View enrolled programs
* View all the demographic information submitted across programs
* Update demographic information
* Apply for a new program
* View a list of all programs offered by the government/ministry/department.

OpenG2P offers a reference implementation of such a self-service portal.

## OpenID Connect integration

Users can log in via any OpenID Connect (OIDC) Auth provider. Any ID system that implements ODIC specification can be integrated with Self Service Portal for user login.

### Login using MOSIP ID

The Self Service Portal integrates with [e-Signet](https://docs.esignet.io/) to provide user login via MOSIP ID.

<figure><img src="../../.gitbook/assets/ssp-login-page (1).png" alt=""><figcaption></figcaption></figure>

## Registration demo

{% embed url="https://www.youtube.com/watch?v=DZweP3qKkn8" %}

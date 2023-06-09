# Self Registration via Portal

## Introduction

OpenG2P offers a reference implementation of [Self Service Portal ](broken-reference)where a person logins via his/her ID and then applies for a program. In self-service mode, typically, OTP would be used for login. In assisted mode, the registering officer may have biometric devices connected to his/her machine and the registrant can perform biometric authentication in an online manner.&#x20;

Online registration assumes that an ID verification service is available to connect via APIs and perform verification of the identity of a person. In the case of MOSIP, for e.g, the verification can be done using the [e-Signet](https://docs.mosip.io/1.2.0/integrations/e-signet) solution.

## ID Verification

### Introduction  <a href="#introduction" id="introduction"></a>

At the backend, the ID provided (functional or foundational) during registration is verified by submitting the demographic details and ID number by calling APIs of the corresponding ID system. The response from the ID system could be a _yes/no_ response with optional data like ID tokens and KYC details.

### Verification of MOSIP ID <a href="#verification-of-mosip-id" id="verification-of-mosip-id"></a>

## Self-registration demo

{% embed url="https://youtu.be/DZweP3qKkn8" %}


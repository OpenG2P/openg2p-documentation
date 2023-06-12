# Agent/Officer Assisted Registration

## **Introduction**

OpenG2P offers mechanisms to carry out registrations on the field in areas where Internet connectivity may not be available. The person's information is filled in [ODK](https://getodk.org/) forms on Android devices and submitted to the backend for further processing. The ODK application is integrated with a QR code scanning application that enables an automatic population of KYC data of the person in the form along with verification of digital signature establishing the authenticity of the card.

## Registration Process

* Program creation&#x20;
* ODK form template creation&#x20;
* Upload of form to ODK Central
* Assigning forms to agents
* Field registration by the agent using ODK Collect on an Android tablet/phone.
* Submission of form to ODK Central
* Addition of record to the registry&#x20;
* ID verification and KYC

## ODK

ODK is an open-source toolkit that uses offline forms to collect data.  ODK Collect is the client-side app while ODK Central is the server-side app.  Learn more about ODK [here](https://docs.getodk.org/). A high-level view of the agent-assisted registration flow is given below:

<figure><img src="../../../.gitbook/assets/image (3) (1) (1) (1).png" alt=""><figcaption></figcaption></figure>

## ID Verification

### Introduction  <a href="#introduction" id="introduction"></a>

At the backend, the ID provided (functional or foundational) during registration is verified by submitting the demographic details and ID number by calling APIs of the corresponding ID system. The response from the ID system could be a _yes/no_ response with optional data like ID tokens and KYC details.

### Verification of MOSIP ID <a href="#verification-of-mosip-id" id="verification-of-mosip-id"></a>

## Offline registration demo

{% embed url="https://youtu.be/0jjkq4SoONM" %}




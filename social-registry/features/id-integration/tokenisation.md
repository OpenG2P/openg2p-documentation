---
description: WORK IN PROGRESS
---

# ID Validation and Tokenisation

The tokenisation process involves using the ID Authentication system to verify the registrant's data. If the IDs such as registrant's ID (RID), virtual ID (VID), or unique identification number (UIN) are valid, then the IDA system generates a token. The generated token replaces the sensitive data, like RID, VID, or UIN, with non-sensitive data and it is recorded in the database or the individual/group registries of the Social Registry (SR) module.

## Functionality

* Uses an [MTS connector](https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder/mts-odk-importer) to establish a connection to the ID system's APIs in order to valid MOSIP data offline at the backend.
* Validates bulk IDs.
* Tokenises the ID and populates it in SR.

{% hint style="info" %}
Here we use the term "**validation**" (as opposed to "**verification**" or "**authentication")** of the ID and the associated demographic information of the individual with the ID system. This is not the same as verifying an individual's identity using biometrics or OTP.
{% endhint %}

IDA receives requests to generate tokens from the various registration mechanisms, whenever

<table><thead><tr><th width="348"></th><th></th></tr></thead><tbody><tr><td><a href="tokenisation.md#mts-connector"><strong>MTS Connector</strong></a> <strong>(</strong><a href="https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder"><strong>MOSIP Token Seeder</strong></a><strong>)</strong></td><td>A  program administrator creates an <strong>ODK MTS Connector</strong> for individual/group registrants to map the ODK forms available in the ODK Central to the SR. </td></tr><tr><td><a href="tokenisation.md#esignet"><strong>eSignet</strong></a></td><td>Self-registration by a potential beneficiary with their valid RID, VID, or UIN via eSignet.</td></tr><tr><td>Biometric authentication</td><td>WIP</td></tr></tbody></table>

## MTS connector

Social Registry with MTS uses MTS Connector to authenticate registrants, who are registered using the ODK Collect App. The UIN and demographic details provided by registrants are validated by calling APIs of the MOSIP IDA system. The MOSIP IDA responds with an authentication token upon successful validation. MTS is a standalone service offered by MOSIP.&#x20;

MTS Connectors can take inputs from both ODK Central and SR. Since one MTS Connector takes only one type of input, separate MTS connectors are required for ODK Central and SR.

A high-level representation of the interactions between different components during validation is shown below:

<figure><img src="../../../.gitbook/assets/authentication-using-mts (1).png" alt=""><figcaption></figcaption></figure>

## eSignet

Registrant utilises valid credentials to access the Self Service Portal. While logging using eSignet, an OTP or QR code is typically used in addition to a UIN or VID for self-registration.  eSignet makes a call to the connected IDA to the Self Service Portal to verify the authenticity of the registrant's VID or UIN. The IDA generates a token upon successful authentication. The token will be recorded in the relevant registrant SR modules' individual/group registries.

## Bio-metric authentication

WIP

{% hint style="info" %}
**Is ID number by itself considered Personally Identifiable Information (PII**) ?

If ID is random, revokable and tokenized (not used for seeding), it is not PII. But if it is codified, used for seeding everywhere and not changeable, then it can be used to identify the person or know something about them
{% endhint %}

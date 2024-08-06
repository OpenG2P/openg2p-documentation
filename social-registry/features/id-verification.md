---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# MOSIP ID Validation and Tokenization

The Social Registry may contain IDs along with demographic information collected during the intake process. &#x20;

This feature offers the following functionality:

* Validate MOSIP ID information at the backend in an offline manner by connecting to APIs of the ID system (using [MTS connector](https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder/mts-odk-importer)).
* Bulk ID validation.
* Tokenize the ID and populate it in Social Registry.

{% hint style="info" %}
Here we use the term "**validation**" (as opposed to "**verification**" or "**authentication")** of the ID and the associated demographic information of the individual with the ID system. This is not the same as verifying an individual's identity using biometrics or OTP.
{% endhint %}

## Mechanism

Social Registry with [MOSIP Token Seeder (MTS)](https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder) uses MTS Connector to authenticate registrants, who are registered using the ODK Collect App. The Unique ID Number (UIN) and demographic details provided by registrants are validated by calling APIs of the [MOSIP ID Authentication](https://docs.mosip.io/1.2.0/id-authentication) (IDA) system. The MOSIP IDA responds with an Authentication Token upon successful validation. MTS is a standalone service offered by MOSIP.&#x20;

MTS Connectors can take inputs from both ODK Central and Social Registry. Since one MTS Connector takes only one type of input, separate MTS connectors are required for ODK Central and Social Registry.

A high-level representation of the interactions between different components during validation is shown below:

<figure><img src="../../.gitbook/assets/authentication-using-mts.png" alt=""><figcaption></figcaption></figure>



{% hint style="info" %}
**Is ID number by itself considered Personally Identifiable Information (PII**) ?

If ID is random, revokable and tokenized (not used for seeding), it is not PII. But if it is codified, used for seeding everywhere and not changeable, then it can be used to identify the person or know something about them
{% endhint %}


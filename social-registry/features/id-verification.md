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

# ID Verification

* Verify ID information at the backend by connecting to APIs of the ID system (using [MTS connector](https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder/mts-odk-importer))
* Bulk ID verification
* Tokenize the ID and populate it in Social Registry

{% hint style="info" %}
**Is ID number by itself considered Personally Identifiable Information (PII**) ?

If ID is random, revokable and tokenized (not used for seeding), it is not PII. But if it is codified, used for seeding everywhere and not changeable, then it can be used to identify the person or know something about them
{% endhint %}


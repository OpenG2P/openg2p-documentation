# Privacy and Security

Social Registry typically contains rich demographic information of persons. Hence, privacy and security of this data if utmost importance. OpenG2P offers several features related to privacy and security

* Encryption of PII at rest
* Anonymized eligibility and entitlement determination
* Anonymous data for reporting
* Role based access to data
* Multi factor authentication
* Robust secure deployment infrastructure
* HSM based Key Manager for encryption and digital signatures
* [Secure input handling](https://openg2p.gitbook.io/1.2-reorg/Kh7IXykse3jg1KAO6g2b/social-registry/privacy-and-security#secure-input-handling)

## Secure input handling <a href="#secure-input-handling" id="secure-input-handling"></a>

Input security is handled in the following ways:

* Input validation
* Memory safe programming language (Python)
* Type safe programming using Python Pydantic
* ORM capabilities to avoid SQL Injection threats

## Encryption of PII

* Social Registry fields can be encrypted and stored. Or the registry data can be anonymized.
* Social Registry uses [MOSIP Keymanager](https://docs.mosip.io/1.2.0/modules/keymanager) module for cryptography APIs. Keymanager uses HSM to store keys and perform operations like encrypting, signing, etc. so that the real keys are stored in HSM.
* Know more about [Privacy and Security in OpenG2P](../../privacy-and-security/). And about [Keymanager integration](../../privacy-and-security/key-manager.md).
* Link to [Configuration and source code](../../pbms/development/repositories/openg2p-security.md).

<figure><img src="../../.gitbook/assets/Registry Keymanager (1) (1).jpg" alt=""><figcaption></figcaption></figure>

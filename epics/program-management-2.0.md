# Program and Beneficiary Management System 2.0

## Context

The document here presents a collection of thoughts and scribbles on the next-generation Program and beneficiary management architecture of OpenG2P.

## Architecture

The idea is to decouple the current Odoo-based Registry and enhance the Program and Beneficiary Management System (PBMS) module such that PBMS pulls data from any external registry compliant with the [G2P Connect](https://g2pconnect.global/) interface. The PBMS should be able to pull data from multiple registries to create a beneficiary list. The pulled data is expected to have **no** PII or demographic information but just the IDs, type of ID and source of data.

The eligibility definition will contain additional fields to specify the source of data. Something like:

```
monthly_income@TaxRegistry < 5000 AND total_owned_land_area@LandRegistry < 10
```

We have assumed that external registries will have the capability to filter data based on the queries supplied as part of the G2P Connect interface and will be able to return just the IDs of the filtered data. If not, intermediate processing may be required. See [Cache](program-management-2.0.md#cache).



<figure><img src="https://raw.githubusercontent.com/OpenG2P/openg2p-documentation/develop/.gitbook/assets/program-management-2.0.png" alt=""><figcaption><p>PBMS</p></figcaption></figure>

## Registries

Depending on where the registries are housed, or rather ownership of registries, we can classify them as below:

1. External:  Registries that are typically housed outside the OpenG2P environment and allow only reading (consumption) of data.  The data is owned by some other entity or department.
2. Internal:  Registries that are typically part of the OpenG2P installation, where data may be added, deleted, or updated. The data is owned by an entity that has deployed OpenG2P. Multiple instances of these registries may exist. Each registry may be created for a specific purpose. For eg. if a survey is done, or registrants apply via offline or online registrations, all their data may be stored in these registries. Note that these are not "Beneficiary" registries (see below)
3. Beneficiary registry (BR):  This registry contains beneficiary data only. These beneficiaries are created as part of the enrollment process. For simplicity of design, we propose a single instance of the BR containing beneficiary data for all programs. Proposed fields in BR are [program code, beneficiary code, individual's ID, ID type, status](#user-content-fn-1)[^1].

Each registry should have the capability for

1. Sharing data via G2P Connect
2. Providing Verifiable Credentials (VCs) to users

While VCs may not be very useful for Internal registries, they definitely are a must-have for BRs.&#x20;

## Technology

OpenG2P's PM can continue to be built on Odoo. &#x20;

For registries, we must consider [Sunbird RC](https://docs.sunbirdrc.dev/learn/readme) as it provides both the above functions and several others like attestation etc.&#x20;

While each of the Internal registries may be specific to a purpose like a survey, or registrations for a program, the reason we will need multiple registries is that an instance of Sunbird RC registry is specific to a data schema.

The Beneficiary registries will also use Sunbird RC, and thus sharing beneficiary data to other systems will become seamless.

## Cache

What happens to the existing Registry module of OpenG2P?  We believe this module may be used as a cache for intermediate processing.  For instance, if external registries do not have sophisticated filtering capabilities, and so we end up pulling a whole lot of demographic data from them. For further processing, the data needs to be cached. The PII data in the cache must be cleared after processing is complete and the beneficiary list is created. The cache may be used to store computed fields like PMT scores.&#x20;

## Timestamp

Every field that is pulled from other registries or computed within OpenG2P must be timestamped. Subird RC has some timestamp features _(to be studied)._ In the eligibility formula, it should be possible to specify the time period or timestamp of the input parameters for eligibility computation. &#x20;

## Consent

[G2P Connect Registry APIs](https://github.com/G2P-Connect/specs/blob/draft/release/yaml/registry\_core\_api\_v1.0.0.yaml) define a consent object. However, it is more like a placeholder and any consent object may be used here, for example, [DEPA Consent Artefact](https://depa.world/learn/consent-artefact). (Note that X-Road architecture does not define consent). &#x20;

Consent is by and for an individual, it is not bulk. It is not clear how bulk consent can be given for data to be imported from other registries. Perhaps, instead of consent, the 'authorise' object in the G2P Connect Registry APIs may be used, backed up by a user consent (blanket) that is requested from the user during registration of a program and stored in the OpenG2P system. This store house of consent artefacts may also be used for any audit purposes later. The decision to use the consent of registrants is left to the country/program policies. Some suggested workflows:

* Strict:  After the data is pulled from an external registry, all the registrants who have not yet provided consent are discarded (and possibly notified, along with a mechanism for them to apply for the program separately along with consent).&#x20;
* Lenient:  To continue using data of all individuals, while notifying the ones who have yet not given consent along with a mechanism for them to provide consent, say, via self-service portal.

<details>

<summary>In X-Road documentation, I could not see the concept of user consent, consent artefact.  Am I missing something?</summary>

Opinion:

That is the core difference between the two models. How consent is obtained is kept outside in both G2P Connect X-Road.  Further, X-Road doesn’t care what messages are shared like HTTP body.  G2P ConnecX payload header/message can be carried in X-Road instance. In this model, some parts of G2P Connect and X-Road headers may repeat!  As a case study, OpenG2P along with CDPI can take up this integration.



</details>

## Deduplication

While receiving data from disparate sources, it is likely that IDs used in systems may be different. Here, demographic deduplication may be required. It is envisaged that this deduplication system will be a completely different module/service. _To be designed_.

## Compatibility

This version of PBMS will NOT be compatible with 1.x version of PM as substantial changes in the architecture are proposed





[^1]: 

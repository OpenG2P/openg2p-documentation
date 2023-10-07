# Document Sharing Infra

## Context

The thoughts here are inspired by a request from the Philippines AICS team on the ability to share user-uploaded documents across departments without users having to upload the same repeatedly. Moreover, the evidence of document verification by one agency should be accessible to anyone with whom the document is shared. The consumer of the document (a government department, for example) may further verify the same. Such a chain of evidence of verifications must be available to the consumers of the document. In the case of the AICS program, an important point to note is that users will mostly upload scanned PDF copies of their documents, like a medical prescription. These documents will not be available in a digital format until they are gradually converted to digital. This conversion process may occur either at the source or at some point in the chain, either through manual transcription or by utilizing OCR (Optical Character Recognition) technology.

Document sharing is not different from general data sharing. Immediately coming to mind are architectural systems such as [X-ROAD](https://x-road.global/), [Open Banking](https://www.openbanking.org.uk/) and the recently announced [DEPA](https://depa.world/).

Although it may take several years for a country to develop and implement the above mechanisms, the goal here is to create a document-sharing system that can be put into action in the short term. This system should be in accordance with the fundamental principles of data sharing and should seamlessly work alongside established data-sharing standards.

<details>

<summary>What is the relation between G2P Connect APIs and DEPA APIs?  Both define APIs for data sharing.</summary>

Response from Vijay:

Both complement each other. G2P Connect is primarily designed for two systems to search and get data. Multiple beneficiaries' data accessible is made possible. DEPA includes linking, discovery etc., flows and creates a network of entities and is restricted to single user data with consent artefact. The consent artefact is controlled by an independent 3rd entity called the Consent Manager. That is why I mentioned 3 independent operational models are required to cover all use cases for data sharing:

1. User-controlled wallets where the user is empowered with trusted verifiable data/credentials to share.
2. The DEPA-like architecture uses an independent data consent/data fiduciary kind of entity to obtain consent and to facilitate data sharing.
3. G2P / x-road kind architecture where consent is independently acquired by either provider (notify) or consumer (search) without any data fiduciary in the middle to exchange data.

In option #3, consent obtained through a consent manager (i.e. option 2) may also be used to fetch data by data consumer!

</details>

## Architecture

For the immediate use case, we can perhaps go with the following approach:

1. Create a Document Store Service (DSS) as an independent module/service with a data store like MinIO.
2. While registering an individual via a self-service portal or other means acquire consent from the individual to share documents with other departments. This could be a checkbox on the portal.
3. On DSS, create a consent object following a standard like [DEPA Consent Artefact](https://depa.world/learn/consent-artefact), store it and link it to the user registry entry via, say, the user's unique ID.
4. The important point to note about the above consent is that usually, consent will be given by an individual (owner of the data) to the consumer of data to fetch data from the producer. As such, DSS being a producer of data, need not seek and store the above consent artefact. It is assumed that consent artefact will be sent by the consumer to the producer while requesting for data. However, since the consumer side systems may not be evolved enough, we will obtain blanket consent from the individual and use this consent artefact as a proxy.
5. The DSS exposes data-sharing APIs as defined in DEPA.
6. &#x20;The documents may be uploaded via a self-service portal. The uploaded documents are stored with a unique filename in the data store.
7. Do we need to encrypt these documents? Probably overkill. (_TBD_).
8. While sharing data with the consumer, the data must be encrypted. See the section below.

## In-flight data encryption

While sharing data with consumers it is imperative to encrypt the data.  X-Road kind of systems already take care of this in a unified manner. But since such an infra may not be available in countries we can use MOSIP's Partner Management and Key Management module to accomplish the same. The following MOSIP services will be required:

1. **PMS**:  This module provides the capability to on-board partners with their encryption keys.
2. **Key Manager**:  Required for key management, connecting to HSM, key rotation, and encrypting data.
3. **Auth Manager:**  Required for authentication using Keycloak (t_o be understood_)
4. **Keycloak**:  Partner onboarding
5. **Audit Manager**:  Required for all MOSIP services.

## Audit trace

The DSS must save all the transaction history of the data shared for audit purposes. This could be simple table in the DB.


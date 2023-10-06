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

1. While registering a user via self-service portal or other means acquire consent from the user to share information with other departments. This could be a check-box on the portal
2. On the backend create a consent object following some standard (?), store it and link it to the user registry entry.
3. While fetching data from other registries check if consent is available for all the users whose data is being fetched. (this will be tricky as we don't know the result set from other registries).  One way of doing this is to pull the data into OpenG2P and use data of only those individuals whose consent is available and mark the ones that are not. Let it be a configuration/decision of the program manager to include such people with a notification that their data has been picked from other registries and is being used without explicit consent from them. (we have to understand the laws here, if such a thing is in line with existing policies and norms etc.).
4. The [consent artefact](https://depa.world/learn/consent-artefact) from DEPA may be considered.


# Secure Registry

## Introduction

OpenG2P offers a secure registry that stores person details that have been collected across multiple programs. Duplication of person's data is avoided by deduplicating using the unique ID associated with the person (like MOSIP) or by running demographic deduplication heuristics such that the same person is not added multiple times to the same registry. To avoid duplication of fields like age, date of birth, city etc.,  the fields are "codified" with [schemas](schema-for-fields.md).&#x20;

The data in the registry is encrypted at rest. &#x20;

The registry is queried by various programs to create beneficiary list.  See [Program Management](../beneficiary-management.md). The queried data is **anonymised** such that Personally Identifiable Information (PII) is not exposed in a human readable form or provided to downstream systems.&#x20;

Registry supports the following features\*\*:

1. Tokenised registry
2. Deduplicated entries
3. CRUD operations
4. Attestation
5. Evidence
6. Verifiable credentials
7. Anonymous profile
8. Complex queries

{% hint style="info" %}
\*\* Full implementations of these functions will be available in version 1.2.x of OpenG2P.
{% endhint %}

## Individuals and groups

A registry may contain individuals or groups like family, household etc.&#x20;

## FAQ

<details>

<summary>Is the data encrypted and saved in DB?</summary>

Yes, all person data is encrypted with strong cryptographic techniques and saved in the DB. The decryption of this data happens in-memory.

</details>






# Registry

## Introduction

OpenG2P registry is a single repository containing details of the registrants. The registry uses [PostgreSQL](https://www.postgresql.org/) for maintaining the information in a single DB table.

The purpose of the registry is to provide a single source of truth to the program administrators and managers. Program administrators can grant access to other program participants to act on this information.

## Identification of records

Identification of records in the registry is done with configured ID types. ID can be foundational like MOSIP ID or functional like a voter's card, tax number, driving license, etc.

## Individual and groups

Individual registrant information is entered in a single row. Whereas group details are stored in multiple rows in the form of relationships with the head or representative of the group.

## Multiple entries

OpenG2P platform supports multiple entries for a registrant in the registry. The intent is to keep all the entries for a registrant and deduplicate later at the program level if required. Multiple entries allow program administrators the flexibility to build a registry without bothering about duplicate entries, especially during a crisis situation such as a flood, earthquake, tsunami, etc. and work on deduplication later using the [Deduplication Manager](../beneficiary-management/deduplication.md).

## Privacy and security

A registry contains an individual's Personally Identifiable Information (PII) along with very rich demographic data. It is critical that this data is secure and PII is not shared in human-readable form or passed on to other systems without the individual's consent. OpenG2P offers secure and private registries to address this concern.

#### Security

Data at rest is encrypted using strong cryptographic techniques. The data is decrypted in memory while processing the record such that no trace of the unencrypted data is stored anywhere in the system.

#### Privacy

Data is anonymised while being displayed in human-readable form (for example, UI screen). Similarly, any query results from the registry are anonymised such that this information cannot be used to specifically target an individual.

## **Custom registrant information**

More often than not, program administrators require additional information about the registrants. However, each row in the database can have only a fixed number of fields. To provide customization, the OpenG2P registry captures the most commonly used fields such as name, age, gender, address, identity, etc. as a fixed number of individual fields. Any additional information is captured as key-value pairs held together in a blob.

## Records management

#### View

#### Search

#### Merging

#### Archival

#### Delete

#### Export

#### Grant portal access

#### Add to program

## Configuration

#### Group relationships

#### Group types

#### Group membership kind

#### Registrant tags

#### ID types

{% hint style="info" %}
<mark style="color:purple;">**Next generation registry**</mark>

In the roadmap of OpenG2P, an enhanced secure registry with the following features is planned.

1. Tokenised registry
2. Schema base fields
3. REST APIs interface
4. Verification with an ID system
5. Deduplicated entries
6. CRUD operations
7. Complex queries
8. Anonymous profile
9. Data encrypted at rest
10. [Verifiable credentials](../beneficiary-management/verifiable-credentials.md)
11. Evidence
12. Attestation
{% endhint %}

## Developer References

[**API**](../api.md)

[**Code**](../guides/developer-guides/)

## Guides

## FAQs

# Registry

## Introduction

OpenG2P registry is a single repository containing details of the registrants. The registry uses [PostgreSQL](https://www.postgresql.org/) for maintaining the information in a single DB table.

The purpose of the registry is to provide a single source of truth to the program administrators and managers. Program administrators can grant access to other program participants to act on this information.

## Identification of records

Identification of records in the registry is done with configured ID types. ID can be foundational like MOSIP ID or functional like a voter's card, tax number, driver's license, etc.

## Individuals and groups

Individual registrant information is entered in a single row, whereas group details are stored in multiple rows in the form of relationships with the head or representative of the group.

## Multiple entries

OpenG2P platform supports multiple entries for a registrant in the registry. The intent is to keep all the entries for a registrant and deduplicate later at the program level if required. Multiple entries allow program administrators the flexibility to build a registry without bothering about duplicate entries, especially during a crisis such as a flood, earthquake, tsunami, etc., and work on deduplication later using the [Deduplication Manager](../beneficiary-management/deduplication.md).

## Privacy and security

A registry contains an individual's Personally Identifiable Information (PII) and rich demographic data. It is critical that this data is secure and PII is not shared in human-readable form or passed on to other systems without the individual's consent. OpenG2P offers secure and private registries to address this concern.

#### Security

Data at rest is encrypted using robust cryptographic techniques. The data is decrypted in memory while processing the record so that no trace of the unencrypted data is stored anywhere in the system.

#### Privacy

Data is anonymized while displayed in human-readable form (for example, UI screen). Similarly, any query results from the registry are anonymized such that this information cannot be used to target an individual.

## **Custom registrant information**

More often than not, program administrators require additional information about the registrants. However, each row in the database can have only a fixed number of fields. To provide customization, the OpenG2P registry captures the commonly used fields, such as name, age, gender, address, identity, etc., as individual fields. Any additional information is captured as key-value pairs held together in a JSON blob.

## Field value configurations

OpenG2P platform provides configurations to define values (enumerations) for a field. These fields are related to the registrant's identity and association with other registrants. Once defined, these values are available for selection in a dropdown list for that field. This is the list of currently available configurations:

#### ID Types

ID Type is a reference name given by the OpenG2P platform user to refer to a registrant identity such as driver's license, MOSIP ID, Aadhar, etc. Users can define multiple ID Types. Once defined, users can select the ID Type from a dropdown list. Each registrant's ID Type has an ID Number (identifier) associated with it. Therefore, ID Type is also used by the [ID Deduplication Manager](../beneficiary-management/deduplication.md#id-deduplication-manager) to select the ID Type for deduplicating registrants.&#x20;

<figure><img src="../.gitbook/assets/id-type (2).png" alt=""><figcaption></figcaption></figure>

#### Registrant Tags

Registrant tags are used to define the categories for Individuals and groups such as indigenous, solo parents, minors, unemployed, disabled, mentally challenged, etc. These tags can be used by the Eligibility Manager to enrol registrants for targeted programs.

#### Relationships

Relationship is used to record the relation between registrants such as father and son, mother and daughter, and village head and villagers. Relationships can be established between individuals and groups. Some common examples are:

* Individual<>Individual: Father<>Son, Mother<>Daughter, etc.
* Individual<>Group: Village head<>Villagers, Social worker<>Group of beneficiaries, etc.
* Group<>Individual: School<>Principal, Children<>Mother, etc.
* Group<>Group: Class<>School, Schools<>Districts, etc.

OpenG2P platform provides options for directionality in relationships, i.e. bi-directional or uni-directional based on context. Some examples are:

* The father can authenticate the minor child, but the minor child cannot authenticate the father.
* A representative from a group of beneficiaries can receive benefits on behalf of a beneficiary, but the beneficiary cannot receive benefits on behalf of the representative.

The exact interpretation of relationships can vary according to the context and environment of the social protection program. OpenG2P provides all the necessary configurations to the Program Administrator to define complex relationships.

#### Group Types

Group Types define the association among a group of registrants. Some common examples of Group Types are family, household, village, and company.

#### Group Membership Kind

The Group Membership Kind establishes the role of an individual in a group. For example, the individual could be a member or head of the group. This field is especially useful for programs that disburse the benefits to only the head of the group but also record the list of other members in the group.

{% hint style="info" %}
<mark style="color:purple;">**Next generation registry**</mark>

In the roadmap of OpenG2P, an enhanced secure registry with the following features is planned.

1. Tokenized registry
2. Schema base fields
3. REST APIs interface
4. Verification with an ID system
5. Deduplicated entries
6. CRUD operations
7. Complex queries
8. Anonymous profile
9. Data encrypted at rest
10. [Verifiable credentials](broken-reference)
11. Evidence
12. Attestation
{% endhint %}

## FAQs

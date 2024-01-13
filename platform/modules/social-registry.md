---
description: Work in progress
---

# Social Registry

## Introduction

Social Registry (SR) is an independent module offered by OpenG2P to enable creating registries of individuals and groups of people with demographic data with advanced features that makes the SR interoperable and easily fit into the DPI infrastructure of a country. Some of the key benefits of using an SR are:

* Issue Verifiable Credentials (VCs) to registrants
* Share data with other departments and organisations in a standardised manner thus avoiding multiple collection of data
* Provide control to individual persons of their data empowering them.
* Attestation

## Registry update mechanisms

* Individual login and update
* Admin login and update
* Bulk update using CSV
* Import of data from others sources
* Offline update using ODK Central

## Functionality and features

* Registry of human demographic data
* Should be a trusted source of truth
  * Attestation
  * Verifiable Credentials: should be able to issue VC
* Person should have control over his/her data – person should be able to update the data (self service)
* Relationships between people
* Groups and Households
* Privacy & security of data (using MOSIP encryption modules)
* Should be possible to share this data with others (DPI)
  * Compliant to standards like DCI/G2P Connect/GovStack
* Should be possible to add fields in the registry
* Timestamped data
* Change log
* Multiple versions of person record
* Reporting (Statistics)

## Design

### Change log

Change log can be build using the Odoo OCA package [Audit Log](https://github.com/OCA/server-tools/tree/16.0/auditlog). This would be set of changes in any field(s) for the registry.

### Multiple Version

Version might come in following scenarios

* Change in field value
* New updated record comes in for the person which would be termed as a named version (typically surveys)
* Feedback call from the connected applications

While creating multiple records, a marking of default (latest or greatest) record should be possible where in registrar or admin can mark as a bulk or individually.

We may use materialised view of PostgreSQL to keep the default(latest or greatest) records available for a quick fetch.

### Relationships between people

Relationship functionality would primarily address the family relationship.

#### Parent info for a registrant

* Parent1Id
* Parent2Id
* IsAdopted
* GaurdianId

**Spouse Relationship (new table)**

* Person1Id
* Person2Id
* IsMarried
* MarriedOn
* IsSeperated
* SeperatedOn

Current thought process is to set all possible relations with the above data structure.

### Groups and Households

### Attestation

**Attestation table**

* id of the field
* status (NEW, ATTESTED, REJECTED ..)
* attested by
* attestation datetime
* comments

The `status` fields will come from business processes and real use cases.

## User interface

UI required for the following:

* Person to log in, view and update records
* Admin to view and attest fields with comments
* Download of CSV for chosen fields of registry
* Upload of attested CSV

## Bulk attestation

We should be able to download a CSV from the registry, apply bulk attestation, and upload back the CSV. The upload should trigger an update of registry, change log and attestation table

* **Attestation table**
  * id of the field
  * status (NEW, ATTESTED, REJECTED ..)
  * attested by
  * attestation datetime
  * comments

## API

The SR exposes the following REST APIs:

_TBD_

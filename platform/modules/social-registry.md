# Social Registry

## Introduction

Social Registry (SR) is an independent module offered by OpenG2P to enable creating registries of individuals and groups of people with demographic data with advanced features that makes the SR interoperable and easily fit into the DPI infrastructure of a country. Some of the key benefits of using an SR are:

* Issue Verifiable Credentials (VCs) to registrants&#x20;
* Share data with other departments and organisations in a standardised manner thus avoiding multiple collection of data
* Provide control to individual persons of their data empowering them.
* Attestation

## Registry update mechanisms

* Individual  login and update
* Admin login and update
* Bulk update using CSV
* Import of data from others sources
* Offline update using ODK Central

## Features

* Registry of human demographic data
* Should be a trusted source of truth
  * Attestation
  * Verifiable Credentials:  should be able to issue VC&#x20;
* Person should have control over his/her data – person should be able to update the data (self service)
* Privacy & security of data (using MOSIP encryption modules)
* Should be possible to share this data with others (DPI)
  * Compliant to standards like DCI/G2P Connect/GovStack
* Should be possible to add fields in the registry
* Timestamped data&#x20;
* Change log
* Reporting (Statistics)

## DB design

For attestation and change log maintain following tables:

* **Change log table**
  * id of the field
  * changed datetime
  * changed by
  * previous value
  * new value
  * comments
* **Attestation table**
  * id of the field
  * status (NEW, ATTESTED, REJECTED ..)
  * attested by
  * attestation datetime
  * comments

The `status` fields will come from buisness processes and real use cases.

## User interface

UI required for the following:

* Person to login, view and update records
* Admin to view and attest fields with comments
* Download of CSV for chosen fields of registry
* Upload of attested CSV

## Bulk attestation

We should be able to download a CSV from the registry, apply bulk attestation, and upload back the CSV.  The upload should trigger update of registry, change log and attestation table

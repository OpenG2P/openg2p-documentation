# Program Management 2.0

## Context

The document here presents a collection of thoughts and scribbles on the next-generation Program Management capability of OpenG2P.

## Architecture

The idea is to decouple the current Odoo-based Registry and enhance the Program Management (PM) module such that PM pulls data from any external registry compliant with the [G2P Connect](https://g2pconnect.global/) interface. The PM should be able to pull data from multiple registries to create a beneficiary list. The pulled data is expected to have **no** PII or demographic information but just the IDs, type of ID and source of data.

The eligibility definition will contain additional fields to specify the source of data. Something like:

```
monthly_income@TaxRegistry < 5000 AND total_owned_land_area@LandRegistry < 10
```

We have assumed that external registries will have the capability to filter data based on the queries supplied as part of the G2P Connect interface and will be able to return just the IDs of the filtered data. If not, intermediate processing may be required. See [Cache](program-management-2.0.md#cache).

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

The Beneficiary registries will also use Sunbird RC, and thus sharing beneficiary data to other systems will become seamless.

## Cache

What happens to the existing Registry module of OpenG2P?  We believe this module may be used as a cache for intermediate processing.  For instance, if external registries do not have sophisticated filtering capabilities, and so we end up pulling a whole lot of demographic data from them. For further processing, the data needs to be cached. This cache must be cleared after processing is complete and the beneficiary list is created as the PII data of an individual may be required for processing.

## Deduplication

While receiving data from disparate sources, it is likely that IDs used in systems may be different. Here, demographic deduplication may be required. It is envisaged that this deduplication system will be a completely different module/service. _To be designed_.

## Compatibility

This version of PM will NOT be compatible with 1.x version as substantial changes in the architecture are proposed





[^1]: 

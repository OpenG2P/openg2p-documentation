# Program Management 2.0

## Context

The document here is a collection of thoughts and scribbles on the next-generation Program Management capability of OpenG2P.

## Architecture

The idea is to decouple the current Odoo-based Registry and enhance the Program Management (PM) module such that PM pulls data from any external registry compliant with the G2P Connect interface. The PM should be able to pull data from multiple registries to create a beneficiary list. The pulled data is expected to have **no** PII or demographic information but just the IDs, type of ID and source of data.

The eligibility definition will contain additional fields to specify the source of data. Something like:

```
monthly_income@TaxRegistry < 5000 AND total_owned_land_area@LandRegistry < 10
```

We have assumed that external registries will have the capability to filter data based on the queries supplied as part of the G2P Connect interface and will be able to return just the IDs of the filtered data.

## Deduplication

While receiving data from disparate sources, it is likely that IDs used in systems may be different. Here, demographic deduplication may be required to be done. It is envisaged that this deduplication system will be a completely different module/service. _To be designed_.




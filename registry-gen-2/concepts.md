# Concepts

**OpenG2P Registry** is an independent module that enables the creation of **functional** **registries** of individuals, non-human entities and groups with advanced features that make the Registry interoperable and easily fit into the digital public infrastructure (DPI) infrastructure of a country. A registry is not a mere database - it is based on principles of a good [functional registry](https://docs.cdpi.dev/initiatives/dpi-as-a-packaged-solution-daas/upcoming-daas-cohorts/functional-registries)  offering several features that can result into exponential benefits to government and people via data share, user control, issue of verifiable credentials etc.

The registry is offered as ready-to-deploy package which can be configured for a use case.

## Functional architecture

<figure><img src="../.gitbook/assets/registr-gen2-functional-architecture.jpg" alt=""><figcaption></figcaption></figure>

A Registry may contain several "Registers". These are essentially database tables with relationships. The core data resides here. The data at rest may be encrypted.  The Registry provides powerful change management feature — every change to the records, whether by an Admin, claimed by beneficiary, or an update from other systems, necessarily passes through a change control process where approval is required to apply the change to data.  The version history of the data is maintained such that, if required, the previous version of data may be queried. This is especially important for handling beneficiary grievances.  The Registry also maintains an audit trail of all important events in the system for transparency and traceability.&#x20;

OpenG2P Registry is a Dynamic registry — the data may be updated by various mechasims:

1. Agent App&#x20;
2. Beneficiary self service portal
3. Staff portal&#x20;
4. Data ingestion from other systems

Irrespective of the mechanism, every change has to pass through the change management process.

# Concepts

**OpenG2P Registry** is an independent module that enables the creation of **functional** **registries** of individuals, non-human entities and groups with advanced features that make the Registry interoperable and easily fit into the digital public infrastructure (DPI) infrastructure of a country. A registry is not a mere database - it is based on principles of a good [functional registry](https://docs.cdpi.dev/initiatives/dpi-as-a-packaged-solution-daas/upcoming-daas-cohorts/functional-registries)  offering several features that can result into exponential benefits to government and people via data share, user control, issue of verifiable credentials etc. The need for a good registry system is well highlighted in the blog [Dynamic Registry: A Foundation for Effective G2P Delivery](../blogs/dynamic-registry-a-foundation-for-effective-g2p-delivery.md).

The registry is offered with **production grade deployment framework** that can be used for pilot and production deployments.

{% hint style="info" %}
This Registry is internally referred as **Gen 2**  as it is a major evolution from the previous avatar - [Social Registry](../social-registry/).  The architecture and technology of this registry is completely different with FastAPI services being used instead of Odoo, and several rich features offered to suit the needs of various domains.
{% endhint %}

## Functional architecture

<figure><img src="../.gitbook/assets/registr-gen2-functional-architecture.jpg" alt=""><figcaption></figcaption></figure>

A Registry may contain several "Registers". These are essentially database tables with relationships. The core data resides here. The data at rest may be encrypted.  The Registry provides powerful change management feature — every change to the records, whether by an Admin, claimed by beneficiary, or an update from other systems, necessarily passes through a change control process where approval is required to apply the change to data.  The version history of the data is maintained such that, if required, the previous version of data may be queried. This is especially important for handling beneficiary grievances.  The Registry also maintains an audit trail of all important events in the system for transparency and traceability.&#x20;

OpenG2P Registry can be seen as a "dynamic" registry — the data can be updated by various mechasims:

1. Agent App&#x20;
2. Beneficiary self service portal
3. Staff portal&#x20;
4. Data ingestion from other systems

Irrespective of the mechanism, every change has to pass through the change management process.

## One core, many domains


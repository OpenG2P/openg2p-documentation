---
description: >-
  The platform's catalogue of reference data: versioned datasets and
  geography, with approvals, a change feed and an opt-in public catalogue
---

# Master Data Service (Catalogue)

A **catalogue** is the single, governed home of a country's **reference data**:
the datasets and geography that many systems use but none of
them owns. Examples are genders, education levels, units of measure, benefit
types, crops or administrative areas.

The **Master Data Service (MDS)** is OpenG2P's catalogue. It defines each piece of
reference data once, for every service in the deployment. Every change is
approved before it is published, every published version is kept, and a consumer
can always say exactly which version it used. MDS is generic: it serves any sector
(social protection, agriculture, health, …). The examples on these pages use one
country pack (Ethiopia) and a few sectors.

<figure><img src="../../../.gitbook/assets/master-data-service-overview.svg" alt="Master Data Service in three layers. Interfaces: the Admin UI for catalogue administrators, which uses the Staff API; the Staff API for registries and other services; the opt-in Public API for open-data portals and anyone; a change feed to subscribed systems. Functions: the country pack loader, change control, effective dates, access control. Data: datasets and geography, versioned, with releases pinning sets of versions. It relies on IAM, the Audit Manager and PostgreSQL, and optionally on AWE and an object store."><figcaption><p>What MDS holds, what it does, and who uses it</p></figcaption></figure>

MDS holds no partners (see [Partner Management](../partner-management/README.md))
and no registry records. All data first arrives from a **country pack**; see
[Country Packs](country-packs.md). What it holds: [Concepts](concepts.md#what-mds-holds).

## Key features

| Feature | In one line | More |
|---|---|---|
| **Versioned datasets and geography** | Every dataset, and the geography, has numbered versions. A consumer reads the latest, pins a version, or reads as of a date | [Concepts](concepts.md#which-version-a-read-returns) |
| **Effective dates and staged changes** | A version can be approved now and take effect on a future date | [Concepts](concepts.md#effective-dates) |
| **Change control with approvals** | Edits go into a draft, which is submitted and approved by another person (maker-checker) or through the Approval Workflow Engine | [Change Control](change-control.md) |
| **Entry codes and P-codes fixed once published** | Labels can change; entry codes and P-codes cannot. A recode is a retire plus an add. Entries are retired, never deleted | [Concepts](concepts.md#entry-codes-and-p-codes-are-fixed-once-published) |
| **Typed fields and references** | Entries can carry typed fields, a parent (hierarchy) and references to other datasets (cross-classification) | [Concepts](concepts.md#typed-fields) |
| **Multilingual labels** | Labels per language for datasets, entries and units | [Concepts](concepts.md#datasets-and-entries) |
| **Geography with boundary changes** | Splits, merges and renames are recorded as change events. A crosswalk maps old P-codes to new units. Boundaries are kept per version | [Geography](geography.md) |
| **Change feed** | Every change is in an ordered feed; new and effective versions are also pushed to subscribers | [For Consumers](consumers.md#following-changes) |
| **Public catalogue (opt-in)** | Datasets marked public can be read anonymously, with downloads, DCAT and SKOS, each with its [data licence](public-catalogue.md#data-licence) | [Public Catalogue](public-catalogue.md) |
| **Audit** | Every change and every API call is sent to the Audit Manager | [Change Control](change-control.md#audit) |
| **Access rules per staff member** | Some reads are filtered by rules set per staff member in IAM (for example, which geography units they see) | [API Reference](api-reference.md#authentication-and-permissions) |
| **One deployment per country** | A deployment is seeded with exactly one country pack. A second country needs a second deployment, so registry images stay country-neutral | [Deployment](deployment.md) |

Why MDS is built this way is on [Design Decisions](design-decisions.md). The
standards it uses are on [Standards](standards.md).

## Who uses it

Registries, other OpenG2P services, maps and, through the public catalogue,
open-data portals. Who reads what, and how, is on
[For Consumers](consumers.md). Catalogue administrators manage the data in the
admin UI; see the [Admin Guide](admin-guide.md).

## Deployment and source code

MDS ships inside the **`commons-services`** Helm chart; see
[Deployment](deployment.md). Code, images and the changelog:
[Software Versions](versions.md).

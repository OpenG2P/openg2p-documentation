---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Registry Release Notes - v4.0.0

|                        |                                                                                                                                                                                                                                    |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**            | 4.0.0                                                                                                                                                                                                                              |
| **Helm Chart Version** | [4.0.0](https://github.com/OpenG2P/openg2p-registry-gen2-deployment/tree/v4.0.0)                                                                                                                                                   |
| **Release Date**       | 17-Apr-2026                                                                                                                                                                                                                        |
| **Description**        | <p></p><ul><li>First release of Registry Gen 2 - the domain agnostic registry platform</li><li>4.0.0 manifests the <strong>Farmer Registry</strong> (with the farmer domain models defined in the extensions repository)</li></ul> |
| **Previous Version**   | —                                                                                                                                                                                                                                  |

***

## Summary

OpenG2P Registry v4.0.0 implements **domain agnosticism** as the core architectural principle. The platform ships with a [**Farmer Registry**](../../farmer-registry.md) as the first domain manifestation, built entirely using the extension framework without modifying core platform code. This release also includes performance optimizations, expanded authentication capabilities, enhanced data validation, and refined user management workflows.

<div align="center" data-with-frame="true"><figure><img src="../../../../.gitbook/assets/farmer-registry-view.png" alt=""><figcaption></figcaption></figure></div>

***

## Key features

| Feature                                | Description                                                                                    | Details                                                                                                                                      |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Domain Agnosticism & Extensibility** | Core registry is domain-neutral; domain-specific registries are implemented as extensions      | [Metadata-Driven Extensibility](../features/metadata-driven-extensibility.md), [Building a Registry](../developer-zone/building-a-registry/) |
| **Farmer Registry Manifestation**      | Reference domain implementation demonstrating extension architecture                           | [Use Case Implementation](../use-case-implementation.md)                                                                                     |
| **Functional ID Generation**           | Decoupled ID generation via OpenG2P ID Generator; configurable per Register                    | [Functional ID Generation](../design/functional-id-generation.md), [ID Generator](../../../../tools/id-generator/)                           |
| **Multi-Provider Authentication**      | OIDC/OAuth integration via OpenG2P IAM Service; ships with Keycloak support                    | [RBAC Roles & Permissions](../features/rbac-roles-and-permissions.md), [IAM](../../../../identity-and-access-management/)                    |
| **Change Request Infrastructure**      | All write operations flow through centralized change requests with verification and approval   | [Change Management](../features/change-management-and-approval-workflow.md), [Design](../design/change-management.md)                        |
| **Version History**                    | Every register change is logged as a version snapshot linked to its originating change request | [Audit-ability & Trace-ability](../features/audit-ability-and-trace-ability.md)                                                              |
| **Async Task Processing**              | Celery Workers and Beat for background ingestion, outgestion, deduplication, and computation   | [Ingestion Pipeline](../design/ingestion-pipeline.md), [Organization of Codebase](../developer-zone/organization-of-codebase.md)             |
| **Encryption at Rest**                 | Envelope encryption (AES + KMS) for sensitive fields                                           | [Data Integrity, Security & Encryption](../features/data-integrity-security-and-encryption.md), [Design](../design/encryption-at-rest.md)    |
| **Audit & Verification Logging**       | Comprehensive verification logging with audit trails and user action attribution               | [Audit Trail Design](../design/audit-trail-for-write-operations.md)                                                                          |

For the complete feature list, see [Features](../features/).

***

## Components & versions

Refer to [Helm Chart](../deployment/helm-chart-4.x.md) for details on components, dependent services and compability.

## Component architecture

For detailed component architecture and repository descriptions, see [Organization of Codebase](../developer-zone/organization-of-codebase.md).

## Breaking changes

This is the first release of the Gen 2 Registry platform. This is complete new architecture and is NOT COMPATIBLE with [Gen1 Registry](../social-registry/) (3.x and before).

***

## Non Functional Requirements

Refer to [Security and Performance Testing - Design & Approach Document](../developer-zone/non-functional-requirements.md)



***

## Interoperability Standards

The Farmer Registry implements the [Farmer DCI Standards](https://standards.spdci.org/standards/dci-standards/wip-farmers-registry) in the Ingestion and Outgestion pipelines.

## Known issues

Refer to [issue Jiras](https://openg2p.atlassian.net/issues/?jql=type+%3D+Bug+AND+%28status+%21%3D+Closed+AND+status+%21%3D+Resolved%29+AND+labels+%3D+Reg_tagged_4.0.0+ORDER+BY+key+ASC%2C+created+DESC\&atlOrigin=eyJpIjoiZmE2NWQwZDc0NTRhNDViNmI3ZWJiMWU2ODlkMjcxOTYiLCJwIjoiaiJ9).

***

## Testing

{% embed url="https://docs.google.com/spreadsheets/d/1bnKFyO0DAi2M9Mvath17TUAAGKOaEi_-K_v9VGgI-iw/edit?usp=sharing" %}

***

## Deployment

For deployment of Registry, see [Deployment](../../../../deployment/).

***

## Roadmap

For features planned for upcoming releases, see [Versions](./).

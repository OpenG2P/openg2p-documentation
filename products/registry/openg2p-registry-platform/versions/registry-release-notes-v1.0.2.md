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

| | |
| --- | --- |
| **Release Date** | 17-Apr-2026 |
| **Helm Chart Version** | 1.0.2 |
| **Branch** | 4.0.0 |
| **Previous Version** | — |

---

## Summary

OpenG2P Registry v4.0.0 implements **domain agnosticism** as the core architectural principle. The platform ships with a **Farmer Registry** as the first domain manifestation, built entirely using the extension framework without modifying core platform code. This release also includes performance optimizations, expanded authentication capabilities, enhanced data validation, and refined user management workflows.

---

## Key Features

| Feature | Description | Details |
| --- | --- | --- |
| **Domain Agnosticism & Extensibility** | Core registry is domain-neutral; domain-specific registries are implemented as extensions | [Metadata-Driven Extensibility](../features/metadata-driven-extensibility.md), [Building a Registry](../developer-zone/building-a-registry/README.md) |
| **Farmer Registry Manifestation** | Reference domain implementation demonstrating extension architecture | [Use Case Implementation](../use-case-implementation.md) |
| **Functional ID Generation** | Decoupled ID generation via OpenG2P ID Generator; configurable per Register | [Functional ID Generation](../design/functional-id-generation.md), [ID Generator](../../../../utilities-and-tools/id-generator/README.md) |
| **Multi-Provider Authentication** | OIDC/OAuth integration via OpenG2P IAM Service; ships with Keycloak support | [RBAC Roles & Permissions](../features/rbac-roles-and-permissions.md), [IAM](../../../../identity-and-access-management/README.md) |
| **Change Request Infrastructure** | All write operations flow through centralized change requests with verification and approval | [Change Management](../features/change-management-and-approval-workflow.md), [Design](../design/change-management.md) |
| **Version History** | Every register change is logged as a version snapshot linked to its originating change request | [Audit-ability & Trace-ability](../features/audit-ability-and-trace-ability.md) |
| **Async Task Processing** | Celery Workers and Beat for background ingestion, outgestion, deduplication, and computation | [Ingestion Pipeline](../design/ingestion-pipeline.md), [Organization of Codebase](../developer-zone/organization-of-codebase.md) |
| **Encryption at Rest** | Envelope encryption (AES + KMS) for sensitive fields | [Data Integrity, Security & Encryption](../features/data-integrity-security-and-encryption.md), [Design](../design/encryption-at-rest.md) |
| **Audit & Verification Logging** | Comprehensive verification logging with audit trails and user action attribution | [Audit Trail Design](../design/audit-trail-for-write-operations.md) |

For the complete feature list, see [Features](../features/README.md).

---

## Components & Versions

| Component | Version | Repository |
| --- | --- | --- |
| Deployment Package (Helm) | 1.0.2 | openg2p-registry-deployment |
| Registry APIs | — | openg2p-registry-apis |
| Celery Runtimes | — | openg2p-registry-celery |
| Staff Portal UI | — | openg2p-registry-staff-portal-ui |
| Registry Core (library) | — | openg2p-registry-core |
| Domain Extensions | — | openg2p-registry-extensions |
| Standards Templates | — | openg2p-registry-standards |
| Docker Scripts | — | openg2p-registry-docker |

For detailed component architecture and repository descriptions, see [Organization of Codebase](../developer-zone/organization-of-codebase.md).

### External Service Dependencies

| Service | Version | Details |
| --- | --- | --- |
| IAM Service | 1.0.0 | [Documentation](../../../../identity-and-access-management/README.md) |
| ID Generator Service | 1.0.0 | [Documentation](../../../../utilities-and-tools/id-generator/README.md) |
| Master Data Service | 1.0.0 | — |

---

## Breaking Changes

None. This is the first release of the Gen 2 Registry platform.

---

## Known Issues

_None identified at the time of release._

---

## Testing

{% hint style="info" %}
Test results and coverage details to be published.
{% endhint %}

---

## Upgrade Notes

This is the initial v4.x release. For fresh deployment instructions, see [Deployment](../design/deployment/README.md).

---

## Roadmap

For features planned for upcoming releases, see [Versions](README.md).

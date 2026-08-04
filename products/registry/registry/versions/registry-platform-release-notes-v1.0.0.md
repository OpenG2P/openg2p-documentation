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
  actions:
    visible: true
---

# Registry Platform Release Notes - v1.0.0

{% hint style="info" %}
**New home: GitLab.** **`registry-platform`** is now developed at [gitlab.com/openg2p/registry/registry-platform](https://gitlab.com/openg2p/registry/registry-platform).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

|                       |                                                                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**           | 1.0.0                                                                                                                                                                           |
| **Source Repository** | [registry-platform](https://github.com/OpenG2P/registry-platform/tree/v1.0.0)                                                                                                   |
| **Release Date**      | 19-Jun-2026                                                                                                                                                                     |
| **Description**       | <ul><li>First tagged release of the consolidated OpenG2P Registry platform source repository</li><li>Replaces the deprecated openg2p-registry-gen2 split repositories</li></ul> |
| **Previous Version**  | —                                                                                                                                                                               |

***

## Summary

registry-platform v1.0.0 is the first semantic-version tag on the consolidated Registry platform repository. This release captures the domain-agnostic platform: core ORM models and business logic, Staff/Partner/Beneficiary Portal APIs, Celery beat producers and workers, the Staff Portal UI, and the shared UI widget library.

registry-platform is a **platform, not a deployable product**. Operators deploy a **manifestation** that assembles platform runtimes with domain-specific models, Docker build scripts, and a self-contained Helm chart. See [Organization of Codebase](../developer-zone/organization-of-codebase.md).

***

## Key features in this platform line

| Feature                           | Description                                                                          | Details                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Consolidated codebase**         | Single repository replaces seven deprecated Gen 2 split repos                        | [Organization of Codebase](../developer-zone/organization-of-codebase.md#deprecated-repositories) |
| **Domain agnosticism**            | Core platform carries no domain model; manifestations supply registers and metadata  | [Metadata-Driven Extensibility](../features/metadata-driven-extensibility.md)                     |
| **Change request infrastructure** | All writes flow through staged change requests with verification and approval        | [Change Management](../features/change-management-and-approval-workflow.md)                       |
| **Document handling**             | Change-request supporting documents stored in MinIO with metadata in the platform DB | [Change Management design](../design/change-management.md)                                        |
| **Dynamic UI**                    | Declarative widget library renders forms from JSON schema                            | [Dynamic UI Rendering](../features/dynamic-ui-rendering.md)                                       |
| **AWE readiness**                 | Platform includes hooks and metadata for Approval Workflow Engine integration        | [AWE Integration](../design/awe-integration.md)                                                   |

***

## Components and versions

| Component              | Package / image                        | Version at tag |
| ---------------------- | -------------------------------------- | -------------- |
| Core library           | openg2p-registry-core                  | 1.0.0          |
| Staff Portal API       | openg2p-registry-staff-portal-api      | 1.0.0          |
| Partner API            | openg2p-registry-partner-api           | 1.0.0          |
| Beneficiary Portal API | openg2p-registry-bene-portal-api       | 1.0.0          |
| Celery beat producers  | openg2p-registry-celery-beat-producers | 1.0.0          |
| Celery workers         | openg2p-registry-celery-workers        | 1.0.0          |
| Staff Portal UI        | registry-staff-portal-ui               | 1.0.0          |
| UI widget library      | @openg2p/registry-widgets (`ui/ui-widgets`) | 1.1.2          |

Docker images for deployable registry products are built from the platform source plus a domain extension. Image names and tags are owned by each manifestation repository.

***

## Release contents

| Release item             | Links                                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| **Platform source code** | [registry-platform:v1.0.0](https://github.com/OpenG2P/registry-platform/releases/tag/v1.0.0) |
| **Documentation**        | [OpenG2P Registry docs](https://docs.openg2p.org/products/registry/registry/)                |
| **API reference**        | OpenAPI specs under registry-platform/apis/docs/openapi/                                     |

***

## Breaking changes

This tag marks the consolidation milestone. The following repositories are **deprecated** in favour of registry-platform plus per-manifestation repos:

| Deprecated repository                 | Replaced by                          |
| ------------------------------------- | ------------------------------------ |
| openg2p-registry-gen2-core            | registry-platform/core/              |
| openg2p-registry-gen2-apis            | registry-platform/apis/              |
| openg2p-registry-gen2-celery          | registry-platform/celery/            |
| openg2p-registry-gen2-staff-portal-ui | registry-platform/ui/staff-portal-ui |
| openg2p-registry-gen2-ui-widgets      | registry-platform/ui/ui-widgets      |
| openg2p-registry-gen2-deployment      | Per-manifestation Helm charts        |

New deployments should not use the deprecated split repositories or the legacy openg2p-registry base Helm chart.

***

## Compatibility

| Dependency              | Notes                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| **IAM Service**         | OIDC/OAuth token validation for Staff and Partner APIs                                                       |
| **ID Generator**        | Functional ID generation per register metadata                                                               |
| **Master Data Service** | Partner and geo lookup data                                                                                  |
| **MinIO / S3**          | Document storage for change-request attachments                                                              |
| **AWE v1.0.0**          | Optional multi-stage approval gate for change requests. See [AWE Integration](../design/awe-integration.md). |

***

## Known issues

1. Platform source tags and manifestation image/chart tags are tracked independently.
2. Legacy Helm chart version history (4.0.0, 4.1.0) predates this repository consolidation and remains documented under [Versions](./) for reference only.

***

## Roadmap

The current tagged release is [v1.1.0](registry-platform-release-notes-v1.1.0.md); ongoing 1.1.x fixes land on the `1.1` branch and latest work on `develop`. See [Versions](./).

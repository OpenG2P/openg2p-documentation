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

# Registry Platform Release Notes - v1.1.0

{% hint style="info" %}
**New home: GitLab.** **`registry-platform`** is now developed at [gitlab.com/openg2p/registry/registry-platform](https://gitlab.com/openg2p/registry/registry-platform).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

|                       |                                                                                                                                                                                                 |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**           | 1.1.0                                                                                                                                                                                           |
| **Source Repository** | [registry-platform](https://github.com/OpenG2P/registry-platform/tree/1.1.0)                                                                                                                    |
| **Release Date**      | 06-Jul-2026                                                                                                                                                                                     |
| **Description**       | <ul><li>Second platform release line — builds on v1.0.0 with AWE integration, document handling refactor, Partner Management integration, and Staff Portal security hardening</li></ul>             |
| **Previous Version**  | [v1.0.0](registry-platform-release-notes-v1.0.0.md)                                                                                                                                             |

***

## Summary

registry-platform v1.1.0 is a **tagged release** on the `1.1.0` branch. All platform modules carry version `1.1.0`; the UI widget library (`@openg2p/registry-widgets`, source at `ui/ui-widgets`) is at `1.1.4-dev.2`. Ongoing fixes for the 1.1.x line land on the [`1.1`](https://github.com/OpenG2P/registry-platform/tree/1.1) branch before patch tags (e.g. `v1.1.1`).

This release deepens AWE integration, refactors document storage and handling, repoints Partner Management to commons-services, and hardens Staff Portal authentication (CSRF, cookie domain, CSP).

***

## Key features in this platform line

| Feature | Description | Details |
| ------- | ----------- | ------- |
| **AWE integration** | Full approval workflow support in Staff Portal and APIs | [AWE Integration](../design/awe-integration.md) |
| **Document handling refactor** | Unified document controller, abstract MinIO client, upload profiles | [Change Management design](../design/change-management.md) |
| **Partner Management** | Repointed to commons-services; WJS support | — |
| **Staff Portal security** | CSRF validation, cookie domain config, CSP hardening | — |
| **Reference data & data policy** | Attribute search, administrative-area policies, reference-data rename | [Metadata-Driven Extensibility](../features/metadata-driven-extensibility.md) |
| **Intake forms** | Application reference field, configurable reference generator | [Intake Forms](../design/intake-forms/) |
| **UI widgets** | Geo hierarchy, docs widget, logo/favicon, conditional visibility fixes | [Dynamic UI Rendering](../features/dynamic-ui-rendering.md) |
| **Record-level access** | BaseRepository generics approach for row-level filtering | — |

***

## Components and versions

| Component              | Package / image                        | Version at tag |
| ---------------------- | -------------------------------------- | -------------- |
| Core library           | openg2p-registry-core                  | 1.1.0          |
| Staff Portal API       | openg2p-registry-staff-portal-api      | 1.1.0          |
| Partner API            | openg2p-registry-partner-api           | 1.1.0          |
| Beneficiary Portal API | openg2p-registry-bene-portal-api       | 1.1.0          |
| Celery beat producers  | openg2p-registry-celery-beat-producers | 1.1.0          |
| Celery workers         | openg2p-registry-celery-workers        | 1.1.0          |
| Staff Portal UI        | registry-staff-portal-ui               | 1.1.0          |
| UI widget library      | @openg2p/registry-widgets (`ui/ui-widgets`) | 1.1.4    |

***

## Changes vs v1.0.0

### AWE (Approval Workflow Engine)

* `list_tasks_for_request` endpoint and related Staff Portal task list UI.
* `assignee_name` field on `ApprovalTask`.
* Rollback change-request changes when terminal approval validation fails.
* AWE proxy pagination and improved payload resolution.
* Pre-approve hook for change requests.
* Approvals list in Staff Portal.

### Document handling

* Major refactor: unified document controller, abstract `MinioClient`, removed legacy template-file controller.
* Upload validation profiles for logos, favicons, register icons, and dashboard images (1 MB limit).
* Record image URLs included in change-request data; document ingestion deduplicated per register on approval.
* New **Docs** widget for document display in dynamic UI.

### Authentication & security

* IAM permission handling and authentication cookie management refactored.
* Client-side and server-side CSRF token handling; configurable CSRF validation on Staff Portal API.
* `cookieDomain` environment variable for cross-subdomain auth cookies.
* CSP header extended with `upgrade-insecure-requests`.
* Config navigation restricted to `CONFIG_NAV_ACTIONS`; config sub-pages guarded.

### Partner Management & WJS

* Partner Management repointed to commons-services.
* PM-seed auth aligned to the `g2p-bridge` `pmSeedClientId` pattern.
* WJS (Webhook Job Service) support enhancements.

### Intake forms & change requests

* Application reference field with generation API.
* Configurable reference generator for intake submissions.
* Simplified intake-form submission search logic.
* `request_id` added to `VersionForDateData` (populated from change requests).

### Reference data & data policy

* Attribute and attribute-value search APIs.
* Data policy management extended to administrative areas and reference data.
* Attribute labels renamed to **reference data** across UI and APIs.

### UI widgets & Staff Portal

* UI widget library refactored (geo hierarchy, column distribution, translation handling).
* Boolean conditional visibility, dialog-table conditions, and attribute API hooks fixed.
* Logo-within-text and registry favicon support.
* Breadcrumbs updated for register and intake-form pages.
* Register icon remove button; dash removed from new intake-form breadcrumb.

### Other

* Record-level access approach using `BaseRepository` with generics.
* Geo hierarchy service absence handled gracefully in register service.

***

## Compatibility

| Dependency              | Notes                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| **IAM Service**         | Staff Portal application self-registration; registry pushes tile/roles/permissions at install time           |
| **AWE v1.0.0**          | Installed via commons-services; registry registers per-instance callback secret                            |
| **Partner Management**  | Consumed from commons-services (not bundled in registry chart)                                               |
| **MinIO / S3**          | Document storage; bucket handling uses `StrEnum` directly                                                    |
| **Master Data Service** | Partner and geo lookup; geo reference data seeding supported                                                 |

***

## Known issues

1. The `develop` branch carries in-progress work ahead of the `1.1` support line (currently one commit: permission decorator on one API).

***

## Roadmap

For in-progress platform work, see [Versions](./).

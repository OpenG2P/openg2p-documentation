---
description: Version history of the OpenG2P Registry platform and Helm chart releases.
---

# Versions

## Platform source repository (`registry-platform`)

The **version of the [registry-platform](https://github.com/OpenG2P/registry-platform) repository is the platform version**. Manifestations build Docker images and Helm charts on top of a tagged platform ref.

| Branch / tag | Type | Role |
| ------------ | ---- | ---- |
| `develop` | Running | Latest in-progress work |
| `N.N` (e.g. `1.1`) | Running | Active release line — fixes and support for `N.N.x` land here before a patch tag |
| `N.N.N` / `vN.N.N` (e.g. `1.1.0`) | Tagged | Frozen release — tagged the moment the three-part version is cut |

| Platform Version | Last Modified | Comments |
| ---------------- | ------------- | -------- |
| [develop](https://github.com/OpenG2P/registry-platform/tree/develop) | 08-Jul-2026 | **Latest running version.** In progress. Changes ahead of `1.1`: permission decorator enabled on one API (G2P-5319). |
| [1.1](https://github.com/OpenG2P/registry-platform/tree/1.1) | 17-Jul-2026 | **Running release line** for 1.1.x — fixes and support for issues found in tagged 1.1.x releases land here before a patch tag (e.g. `v1.1.1`). Currently at the same commit as [v1.1.0](https://github.com/OpenG2P/registry-platform/tree/1.1.0). |
| [v1.1.0](https://github.com/OpenG2P/registry-platform/tree/1.1.0) | 06-Jul-2026 | **Tagged release.** All platform modules at `1.1.0`; `@openg2p/registry-widgets` at `1.1.4-dev.2`. [Release notes](registry-platform-release-notes-v1.1.0.md). Key changes vs v1.0.0:<br>• **AWE integration** — task list UI, `list_tasks_for_request`, assignee name, CR rollback on failed terminal approval, pre-approve hook.<br>• **Document handling refactor** — unified document controller, abstract MinIO client, upload validation profiles, Docs widget.<br>• **Staff Portal security** — CSRF validation, `cookieDomain`, CSP hardening, IAM cookie/permission refactor.<br>• **Partner Management** — repointed to commons-services; WJS support; PM-seed auth aligned to `g2p-bridge` pattern.<br>• **Reference data & data policy** — attribute search, administrative-area policies, attribute labels renamed to reference data.<br>• **Intake forms** — application reference field, configurable reference generator.<br>• **UI widgets** — geo hierarchy, logo/favicon, conditional visibility fixes.<br>• **Record-level access** — `BaseRepository` generics approach. |
| [v1.0.0](https://github.com/OpenG2P/registry-platform/tree/v1.0.0) | 19-Jun-2026 | **Tagged release.** First tagged release of the consolidated platform repository. Replaces the deprecated openg2p-registry-gen2 split repos. [Release notes](registry-platform-release-notes-v1.0.0.md). |

{% hint style="info" %}
**Maintaining this table.** `develop` is always the first row (latest running version). The `N.N` row tracks the active support line. Add a new tagged row only when a three-part `N.N.N` version is cut — at that moment it is tagged. Update the **Last Modified** date on running rows (`develop`, `N.N`) as work continues; tagged rows carry the date of their tag.
{% endhint %}

***

## Helm chart versions (`openg2p-registry`)

This page tracks the released and in-progress versions of the OpenG2P Registry (Gen 2) Helm chart (`openg2p-registry`). For full deployment details of the current line, see [Helm Chart 4.x](../_archive/deployment/helm-chart-4.x.md).

| Helm Chart Version                                                                       | Components                                                                                                                                                                                                                                                                                                                | Last Modified | Comments                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [4.2.0-develop](https://github.com/OpenG2P/openg2p-registry-gen2-deployment/tree/4.2)    | <p>Same as 4.1.0, plus:<br>openg2p-awe:develop<br>openg2p-awe-ui:develop</p>                                                                                                                                                                                                                                              | 12 May 2026   | <p><strong>In progress.</strong> Key difference vs 4.1.0:</p><ul><li>Integrated <strong>AWE (Approval Workflow Engine)</strong> as a platform subchart (<code>openg2p-awe 0.0.0-develop</code>) — backend + admin UI + its own Keycloak clients (<code>awe-admin-portal</code>, <code>awe-admin-resolver</code>) and a dedicated <code>&lt;release&gt;_awe</code> database.</li></ul>                  |
| [4.1.0](https://github.com/OpenG2P/openg2p-registry-gen2-deployment/tree/v4.1.0)         | Same as 4.0.0.                                                                                                                                                                                                                                                                                                            | 08 May 2026   | <p>Changes vs 4.0.0:</p><ul><li>Intra-cluster service-to-service calls switched to internal Kubernetes service DNS (ID Generator, Staff Portal API).</li><li>MinIO endpoint corrected to the S3 API host (<code>minio-api.&lt;ns&gt;</code>), now operator-configurable.</li><li>Release-name length validator (max 18 chars).</li><li>Resource requests/limits added for all components.</li><li>Master Data DB names aligned with commons-services.</li><li>Audit Manager connection; uninstall script added.</li></ul> |
| [4.0.0](https://github.com/OpenG2P/openg2p-registry-gen2-deployment/tree/v4.0.0)         | <p><a href="https://hub.docker.com/r/openg2p/openg2p-farmer-registry-staff-portal-api">farmer-registry-staff-portal-api:v1.0.2</a><br><a href="https://hub.docker.com/r/openg2p/openg2p-farmer-registry-partner-api">farmer-registry-partner-api:v1.0.2</a><br><a href="https://hub.docker.com/r/openg2p/openg2p-farmer-registry-celery">farmer-registry-celery:v1.0.2</a> (beat-producer + worker)<br><a href="https://hub.docker.com/r/openg2p/openg2p-registry-staff-portal-ui">registry-staff-portal-ui:v1.0.2</a></p> | 21 Apr 2026   | <p>First release of Registry Gen 2 — the domain-agnostic registry platform. 4.0.0 manifests the <strong>Farmer Registry</strong> (farmer domain models supplied via the extensions repository). Stable version.</p>                                                                                                                                                                                |

{% hint style="info" %}
The **Last Modified** date for in-progress (`-develop`) versions is updated as work continues. Released versions carry the date of their tag.
{% endhint %}

# Registry Documentation — Content TODO

This file tracks pages that need content and diagrams that need to be created. Remove items as they are completed.

---

## Pages needing content

### Features

| # | Page | What to write |
|---|------|---------------|
| 1 | `features/deduplication.md` | Feature description: what dedup strategies are available, how trigram-based matching works, how dedup integrates with change management |
| 2 | `features/outgestion-pipeline.md` | Feature description: how data is pushed to external systems, template-based transformation, topic subscriptions |

### Design

| # | Page | What to write |
|---|------|---------------|
| 3 | `design/outgestion-pipeline.md` | Technical design: outgestion workers, topic configuration models, Jinja templates, WebSub publishing flow |
| 4 | `design/partner-apis.md` | Technical design: ingestion endpoint internals, DCI search implementation, authentication and signature verification, error handling |
| 5 | `design/deduplication.md` | Technical design: matching strategy, trigram indexing, deduplicate_schema in g2p_register_schemas, integration with change management |
| 6 | `design/computation-framework.md` | Technical design: what is element computation, how derived and calculated fields work, execution triggers |
| 7 | `design/vc-issuance.md` | Technical design: verifiable credential types, issuance flow, verification, standards used |

### Deployment

| # | Page | What to write |
|---|------|---------------|
| 8 | `deployment/post-installation.md` | Steps after helm install: verify deployment, DB initialisation, Keycloak configuration, registry metadata setup, first login and smoke test |
| 9 | `deployment/upgrade-guide.md` | Upgrade procedure: pre-upgrade checklist, helm upgrade command, DB migrations, post-upgrade verification, rollback procedure |

### Developer Zone

| # | Page | What to write |
|---|------|---------------|
| 10 | `developer-zone/building-a-registry/guide-to-building-a-registry.md` | Step-by-step tutorial for building a domain-specific registry from scratch (ORM models, Pydantic schemas, metadata, Docker images) |
| 11 | `developer-zone/building-a-registry/concepts/build-and-deploy-a-registry.md` | How to build Docker images and deploy a custom registry extension |

### Other

| # | Page | What to write |
|---|------|---------------|
| 12 | `versions.md` | Fill the version table with actual release dates, highlights, and changelog links for each released version |

---

## Diagrams needed

| # | Diagram | Target page | Description |
|---|---------|-------------|-------------|
| 1 | Change management workflow | `design/change-management.md` | Visual flow: Change Request -> Verification(s) -> Approval -> History insert + Register upsert. Show the shadow-write model (proposed vs approved state). |
| 2 | Ingestion pipeline flow | `design/ingestion-pipeline.md` | The 4 async Celery stages with queues between them: API Ingestion -> Classification -> Transformation -> Change Request creation. Show the database tables at each stage. |
| 3 | Outgestion pipeline flow | `design/outgestion-pipeline.md` | Async flow for outbound data: event trigger -> template transformation -> partner delivery. Show topic and subscription models. |
| 4 | Deployment topology | `deployment/README.md` | Kubernetes architecture: pods (Staff Portal API, Partner API, Celery Beat, Celery Workers, UI), databases (PostgreSQL), supporting services (Keycloak, MinIO, Redis, Key Manager). |
| 5 | Consent flow | `design/consent-management.md` | The 8-step consent artefact generation: consent request -> OAuth authentication -> ID Token validation -> Auth Context -> Consent Artefact -> Consent Receipt (signed). |

---

## Old files to archive or delete

These files are no longer referenced in SUMMARY.md. Their content has been merged into the new design pages. They can be removed once you confirm the new pages are accurate.

- `design/high-level-design/concept.md` — merged into `design/data-model.md` and `design/change-management.md`
- `design/high-level-design/encryption-of-data-at-rest.md` — merged into `design/encryption-at-rest.md`
- `design/high-level-design/consent-management/*` (4 files) — merged into `design/consent-management.md`
- `design/high-level-design/ingestion-pipeline/*` (4 files) — merged into `design/ingestion-pipeline.md`
- `design/high-level-design/outgestion-pipeline-push.md` — superseded by `design/outgestion-pipeline.md`
- `design/high-level-design/partner-apis.md` — superseded by `design/partner-apis.md`
- `design/high-level-design/README.md` — no longer in TOC
- `design/detailed-design-notes/README.md` — no longer in TOC
- `design/detailed-design-notes/consent-management.md` — superseded
- `design/detailed-design-notes/deduplication.md` — superseded
- `design/detailed-design-notes/computation-framework.md` — superseded
- `design/detailed-design-notes/database-encryption-at-rest.md` — superseded
- `design/detailed-design-notes/outgestion-pipeline.md` — superseded
- `design/detailed-design-notes/partner-apis.md` — superseded
- `design/detailed-design-notes/vc-issuance.md` — superseded
- `design/detailed-design-notes/element-computation.md` — superseded (merge into computation-framework if needed)
- `design/detailed-design-notes/registry-metadata.md` — superseded by `design/data-model.md`
- `design/detailed-design-notes/ui-ux-wireframes.md` — empty stub, remove or repurpose
- `design/detailed-design-notes/ui-design.md` — empty stub, remove or repurpose
- `design/detailed-design-notes/ingestion-pipeline.md` — content merged into `design/ingestion-pipeline.md`
- `design/detailed-design-notes/rbac-roles-and-permissions.md` — moved to `features/rbac-roles-and-permissions.md`

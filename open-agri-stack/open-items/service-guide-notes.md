---
description: >-
  Where the "Creating a New Platform Service" guide disagrees with current
  practice, found while building the use-case composite.
---

# Service Guide Notes

Found while building the [use-case composite](../implementation/composite.md) from the guide ([Creating a New Platform Service](../../platform/platform-services/creating-a-new-service.md)) and comparing it with recent services (Consent Manager, Partner Management, Master Data, the registry platform, Farmer and Crop Sown registries). For the guide's maintainers; nothing here changes the composite.

| # | The guide says | Current practice | Suggestion |
| --- | --- | --- | --- |
| 1 | Images run as non-root (uid 1001) | No API image does (CM, PM, MDS, registry partner API); only UI images | Follow the guide (this service does) and fix the others, or relax the guide |
| 2 | Restricted `securityContext`, read-only root filesystem | Every chart ships pod and container security contexts disabled; none is read-only | As above. Note: gunicorn 26 needs `--no-control-socket` on a read-only filesystem |
| 3 | Images `openg2p/openg2p-<slug>[-<component>]` | CM `openg2p/consent-manager-api`, PM `openg2p/partner-management-*`, MDS `openg2p/master-data-api`; only RP, FR, CSR follow it | Align names, or document the exceptions |
| 4 | Chart `openg2p-<slug>` under `deployment/charts/` | PM's chart is `partner-management` (no `app-readme.md`); MDS under `deployments/charts/`; registries under `helm/` | One location and name rule |
| 5 | One image per service, audience chosen by `<PREFIX>_API_AUDIENCE` | The registry platform builds one image per API (staff, partner, bene, agent); only CM uses the audience switch | Document both, or converge |
| 6 | Uninstall script at `deployment/scripts/uninstall-<slug>.sh` | CSR has `scripts/uninstall-registry.sh` | Align |
| 7 | Checklist: "CI path filters cover every build input" | The CI page says no path filters, all or nothing | Remove the stale checklist line |
| 8 | Dockerfile pins openg2p-fastapi-common via `ARG` | The CI pin's ref overrides the Dockerfile default: CM's Dockerfile says `1.2.0` but its CI pins `develop`; PM likewise; MDS pins `1.2` against `1.2.1` | Say the CI pin is what counts, and keep the two equal |
| 9 | (not covered) | Wrapper charts (FR, CSR) depend on `openg2p-registry` and inherit its questions via `inherit-questions.sh` and `questions.own.yaml` | Document the wrapper-chart pattern |
| 10 | Hostnames `<slug>-partner.<ns>…` | The registry platform uses `partner-<registryHostname>` | Align |
| 11 | (base image and workers not specified) | Bases vary (slim, alpine); workers 2–8; a workers env var in RP that the settings prefix never reads (`PARTNER_NO_OF_WORKERS`); RP and MDS run `migrate;` so a failed migration doesn't stop the server | Recommend a base, a workers setting through the settings prefix, and `migrate &&` |
| 12 | Links an `_archive/versioning.md` page | Archived | Update the link; CM and RP still depend on `keycloak-init 0.0.0-develop.60` while 1.2.0 is released |
| 13 | README is a thin pointer to GitBook | CM keeps a full `backend/README.md` and `.env.example` | Decide, then align |
| 14 | (not covered) | A service without a database: openg2p-fastapi-common's `init_db` still builds an engine from defaults | Document how to opt out (override `init_db`), or make it skip when no database is configured |
| 15 | (not covered) | `PartnerMgmtKeyStore` (partner keys from PM) exists only on openg2p-fastapi-common `develop`, not 1.2.x | Release it, so partner-facing services can pin a release |

On item 7: agri-stack's CI now does use a path filter (`composite/**` and the workflow file), so that documentation-only pushes don't build or publish a new composite version. The CI page's "no path filters" is therefore not universal either; the guide and the CI page should agree on when a path filter is acceptable.

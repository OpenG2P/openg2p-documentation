---
description: >-
  The composite's read-only staff console: use cases with their data scopes,
  registries and their scope catalogues, partners and the call log. Staff log
  in through IAM (Keycloak staff realm).
---

# Composite Console

The console shows how the composite is set up and what it has been doing. It is **read-only**: use cases, registries and settings are still changed in the Helm values (Git and Helm history record those changes); partner onboarding stays in the Partner Management and Consent Manager portals, which the console links to.

| Page | What it shows |
| --- | --- |
| **Overview** | Composite partner ID, consent mode (passthrough or exchange) and exchange Consent Manager, signing key, Audit Manager on/off; counts of use cases (and files that failed to load), registries and partners; calls and failures in the last 24 hours |
| **Use cases** | Each published use case: sources and their registry, mandatory/optional, required and optional [data scopes](composite-configuration.md#data-scopes), what the consent must grant per registry, inputs, output fields (with their mapping), allowed partners, and the use case file |
| **Registries** | Each configured registry: its URL, whether it answers, and its data scope catalogue (read from the registry with the composite's signature, cached 5 minutes): every scope with its fields and the use case sources that use it. This is where an admin picks the scopes when writing a use case. |
| **Partners** | Every partner named in a use case's `allowed_partners`, its use cases and the keys Partner Management serves for it |
| **Activity** | The call log, newest first, filtered by partner, use case and outcome: time, HTTP status, outcome and reason, duration and each source's status |

## Access

Staff log in through the IAM staff portal (Keycloak staff realm), as for Master Data. The console registers itself in IAM as the application `agri-composite`:

| Role | Permissions |
| --- | --- |
| `AGRI_COMPOSITE_ADMIN` | `composite:view`, `composite:manage` (kept for editing later) |
| `AGRI_COMPOSITE_VIEWER` | `composite:view` |

The console's API is `GET /composite/v1/admin/...` on the composite service, allowed only with an IAM session holding `composite:view`. The partner API is unchanged: it needs no session and is not affected by the login checks.

## Call log

The Audit Manager stays the record of every request (it has no read API), so the console keeps its own call log in a small database (`agri_composite` in the shared Postgres): one row per query whose partner signature verified (unsigned or forged requests are not logged, so nobody can write rows under another partner's name), with the time, use case, partner, HTTP status, outcome and reason, duration and each source's status. Never the subject, the consent or any data. Rows are written in batches in the background, so a query never waits on the database. Once a day one worker (across all pods) deletes rows older than `console.activityRetentionDays` (default 90). The Activity page counts up to 10,000 matching rows and shows "10000+" beyond that.

## Install

In the composite's Rancher form, group **Console**, or in Helm values:

| Value | Default | |
| --- | --- | --- |
| `console.enabled` | `true` | `false`: no UI, no login checks, no database (the partner API only) |
| `global.consoleHostname` | `agri-composite-console.<namespace>.openg2p.org` | The console's address |
| `console.iam.providerApiUrl` | `http://commons-services-iam-staff-portal-api` | IAM staff portal API (in-cluster) |
| `console.iam.publicUrl` | `https://staff-iam.<namespace>.openg2p.org` | IAM staff portal API, public (the browser's login) |
| `console.iam.redisUrl` | `redis://commons-redis-master:6379/0` | Login sessions |
| `console.iam.keycloakClientId` | `agri-composite` | The console's Keycloak client and IAM application |
| `console.db.*` | `commons-postgresql`, `agri_composite`, `agri_composite_user` | Created by the chart's database job; password in Secret `agri-composite-db` (kept on uninstall) |
| `console.pmPortalUrl`, `console.cmPortalUrl` | the namespace's PM and CM portals | Links shown in the console |
| `console.activityRetentionDays` | `90` | Call log retention |

With the console on, the chart also creates the Keycloak client and registers the console in IAM (a Helm hook; set `console.iamRegister.runAsHook: false` in an umbrella install such as the [Agri Exchange bundle](deployment.md)). Then grant staff `AGRI_COMPOSITE_ADMIN` or `AGRI_COMPOSITE_VIEWER` in IAM.

**Uninstall:** [`scripts/uninstall-agri-composite.sh`](https://github.com/openg2p/agri-stack/blob/develop/scripts/uninstall-agri-composite.sh) `--namespace <ns>` removes the release and what survives `helm uninstall`: its Jobs, ConfigMaps and Secrets, the console database and role, and the console's IAM application rows (`--keep-db`, `--keep-iam` to keep them; `--dry-run` to see the plan). It keeps the console's Keycloak client (a reinstall updates it), the PM/CM entries, and the signing Secret unless `--drop-signing-secret`.

{% hint style="info" %}
**Later:** editing use cases in the console (stored in the database, with a record of who changed what and when, also sent to the Audit Manager), and a "give partner X use case Y" flow that checks the partner's key in PM, creates its Consent Manager policy from the use case's scopes and adds it to the use case. See the [open items](../open-items/README.md).
{% endhint %}

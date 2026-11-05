---
description: The Composite's staff console.
---

# Composite Console

The console shows how the Composite is set up and what it has been doing. It is **read-only**: use cases, registries and settings are still changed in the Helm values (Git and Helm history record those changes); partners, their keys and their use-case grants are managed in Partner Management, and consents in the Consent Manager; the console links to both portals.

| Page | What it shows |
| --- | --- |
| **Overview** | Composite partner ID, consent mode and Exchange Consent Manager, signing key, Audit Manager on/off; counts of use cases (and files that failed to load), registries and partners; calls and failures in the last 24 hours |
| **Use cases** | Each published use case: its sources (one search per registry), what happens if a source can't answer, which sources run after which, their required and optional [data scopes](use-case-configuration.md#data-scopes), inputs, output fields (with their mapping), **Granted to** (the partners with a policy for this use case, `name@major`, in Partner Management), and the use case file. ([the labels](#reading-a-use-case)) |
| **Registries** | Each configured registry: its URL, whether it answers, and its data scope catalogue (read from the registry with the Composite's signature, cached 5 minutes): every scope with its fields and the use case sources that use it. This is where an admin picks the scopes when writing a use case. |
| **Partners** | Read from Partner Management: every partner with a policy for a published use case (one policy per use case), with its **Partner (Partner Management ID)**, **Granted use cases** and the keys PM serves for it. Policy versions are in Partner Management. If PM cannot be read, the page says *Partner Management could not be read* and the list may be incomplete; the Overview's partner count shows a dash |
| **Activity** | The call log, newest first, filtered by partner, use case and outcome: time, HTTP status, outcome and reason, the consent used, duration and each source's status |

## Reading a use case

| Label | Meaning |
| --- | --- |
| **Use case** | e.g. `loan-profile · version 1.0.0 (partners call @1)`: the name, the full version, and the major version partners call |
| **Source (search)** | The source's `id`: one search of one registry |
| **Registry** | The registry the search goes to (`controller`) |
| **If it can't answer** | **Fail the request** (`mandatory`) or **Continue without it** (`optional`); the source's status tells the partner |
| **Runs after** | `depends_on`: the sources whose result this search needs |
| **Required scopes**, **Optional scopes** | Data scopes the consent must grant, or may leave out (their fields are then `null`) |
| **Output fields** | What the partner gets: the `mapping` fields and the `derived` values |

## Access

Staff log in through the IAM staff portal (Keycloak staff realm), as for the catalogue. The console registers itself in IAM as the application `agri-composite`:

| Role | Permissions |
| --- | --- |
| `AGRI_COMPOSITE_ADMIN` | `composite:view`, `composite:manage` (kept for editing later) |
| `AGRI_COMPOSITE_VIEWER` | `composite:view` |

The console's API is `GET /composite/v1/admin/...` on the Composite service, allowed only with an IAM session holding `composite:view`. The partner API is unchanged: it needs no session and is not affected by the login checks.

## Call log

The Audit Manager stays the record of every request (it has no read API), so the console keeps its own call log in a small database (`agri_composite` in the shared Postgres): one row per query whose partner signature verified (unsigned or forged requests are not logged, so nobody can write rows under another partner's name), with the time, use case, partner, HTTP status, outcome and reason, duration, each source's status and the consent's ID (as the Exchange CM names it). Never the subject, the consent's content or any data. Rows are written in batches in the background, so a query never waits on the database. Once a day one worker (across all pods) deletes rows older than `console.activityRetentionDays` (default 90). The Activity page counts up to 10,000 matching rows and shows "10000+" beyond that.

## Install

On by default; its settings are in [chart settings: console](../deployment/composite-chart-settings.md#console). With the console on, grant staff `AGRI_COMPOSITE_ADMIN` or `AGRI_COMPOSITE_VIEWER` in IAM.

{% hint style="info" %}
**Later:** editing use cases in the console (stored in the database, with a record of who changed what and when, also sent to the Audit Manager), and a "give partner X use case Y" flow that raises the policy request in Partner Management from the console. See the [open items](../open-items/README.md).
{% endhint %}

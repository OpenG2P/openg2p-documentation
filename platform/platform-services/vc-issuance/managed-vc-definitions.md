---
description: >-
  PROPOSAL: move credential templates out of Helm into approved, versioned registry metadata with an admin UI. Not built.
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
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

# Managed VC Definitions — Design Proposal

> **Status: proposal. Nothing here is built.** Captured so the reasoning is not
> lost; implementation is a later piece of work.

## The problem

Adding one claim to a credential today touches four places, three of which need
a chart release:

| # | Change | Where | Needs |
|---|---|---|---|
| 1 | expose the column | `<registry>_vc_view.sql` in the extension | rebuild db-seed image, reinstall |
| 2 | allow it as a claim | `claim_columns` in Helm values | chart release |
| 3 | put it in the credential | `vcTemplateJson` in Helm values | chart release + register Job re-POSTs to Certify |
| 4 | print it on the card | the SVG ConfigMap | chart release |

Worse than the count is the **coupling**: three separate names must agree —
view column ↔ `claim_columns` ↔ template `${var}` — and nothing checks them
until an agent is standing at a counter with a citizen. `vc_definitions` is also
read from an environment variable at **startup**, so even a values change needs
a pod restart.

VC configuration is the one piece of registry metadata that lives in Helm.
Everything comparable — register definitions, schemas, attributes, intake forms,
UI tabs — is a database row with a Staff Portal configuration screen.

There is even a vestigial slot for this: the farmer extension ships
`meta_data/registry-configurations/g2p_registry_vc_configurations.sql`
containing only `-- No seed data for g2p_registry_vc_configurations`. The table
was anticipated; no model was ever written.

## What is deliberately kept

**The VC view stays.** Its job is schema decoupling, and that job is real: the
Agent Portal API is *platform* code, `G2PRegister` is abstract, and each
manifestation declares its own tables. Something must flatten "this registry's
shape" into "one row of claims".

The view's *other* job — acting as the field allow-list — is what moves.

## Approach

Move the credential's **content** into registry metadata, put it behind an
approval workflow, version it, and let approval be the thing that publishes to
Certify.

### Data model

Three pieces:

**`g2p_registry_vc_configurations`** — the credential *type*.

| Field | Notes |
|---|---|
| `config_id` | e.g. `OpenG2PFarmerCredential`; the id Certify issues against |
| `credential_types`, `scope`, `context_urls` | OpenID4VCI / JSON-LD identity of the type |
| `view` | which VC view the claims are read from |
| `active_version_id` | → the version currently being issued |
| `active` | a type can be switched off without deleting it |

**`g2p_registry_vc_template_versions`** — the versioned, approvable payload.

| Field | Notes |
|---|---|
| `version_no` | monotonic per `config_id` |
| `vc_template_json` | the JSON-LD credential template |
| `claim_columns` | **the approved claim list** |
| `svg_template` | the printed card design |
| `status` | `draft` / `pending` / `approved` / `superseded` / `rejected` |
| `created_by`, `created_at`, `approved_by`, `approved_at` | audit |
| `certify_pushed_at`, `certify_digest` | what was last published, for drift detection |

**`g2p_vc_issuances`** gains a link to the version used (direct FK, or
`config_id` + `version_no` — indirect is fine).

#### Why `claim_columns` and the SVG live on the *version*

Both change what a citizen receives, so both must sit **inside** the approval
boundary. If only the template text were approved, a claim could still be added
by editing something outside the workflow — and adding a field to a credential
must always be a deliberate, approved act, never a side effect of widening a
view for some unrelated reason (reporting, a shared view, a new register field).

That is the property today's explicit `claim_columns` gives us by accident. The
managed design must preserve it on purpose.

### Lifecycle

```
Draft ──submit──► Pending ──approve──► Approved ──► Active
                    │(AWE)                │
                    │                     └─ auto-register with Certify
                    └──reject──► Draft

Active ──(a newer version is approved)──► Superseded   (retained forever)
```

* **Approval is the only thing that publishes.** After approval, registration
  with Certify is automatic — no separate manual step.
* **Superseded versions are never deleted.** An issued credential can always be
  traced to the exact template that produced it.
* **Rollback is not a special path** — re-approving a superseded version is an
  ordinary approval, and republishes.

### Approval workflow

A **separate AWE policy**, not one of the existing record-change policies.
Credential content is a different kind of decision from a change to one
citizen's record, and wants its own approvers.

### Publishing and drift

The template exists in two places — the registry database and Certify's
`credential_config`. They can diverge (a manual Certify edit, a failed publish,
a restored database).

* On approval, push to Certify and store a **digest** of exactly what was sent.
* Compare that digest against Certify's current config on demand, and surface
  "out of sync with Certify" in the UI.

Without this, divergence is silent until an issuance fails.

### Validation at submit time — recommended

At **submit**, before an approver ever sees it, check:

1. every `claim_column` exists in the configured view;
2. every `${var}` in the template resolves to a claim or a known built-in;
3. the SVG parses and its placeholders resolve.

This is the highest-value single item in the proposal. It converts today's three
silent run-time mismatches into one deterministic failure at authoring time, and
it stops approvers being asked to sign off on something that cannot work.

### Preview before submit

Render a **sample PDF** — from a real record or a dummy one — as part of the
draft screen. Approvers otherwise sign off on JSON they cannot picture, which is
not a meaningful approval for an artefact whose whole purpose is to be looked at.

### In-flight issuance

An issuance that began before a version flip **finishes on the version it
started with**. The version is resolved once, at the start of the issuance, and
carried through — not re-read at the point of signing.

### What stays in Helm

Environment-level configuration only:

* issuer DID and signing keys;
* Certify base URL and credentials;
* feature switches (`vcIssuance.enabled`).

Not per-credential content. The chart may still **seed** an initial approved
version so a fresh install issues out of the box; after that the database is
authoritative.

## Multiple credential types

Already supported — `vcDefinitions` is a list, and `config_id` selects among
them at issue time. What is missing is *managing* them, which is what this
proposal adds. The Agent Portal already asks for the type when more than one is
configured.

## Deliberately out of scope

* **Generating or managing the VC view from the UI.** Keeps hand-authored SQL
  for now. Revisit once the metadata path is proven; it means generated DDL
  against a production database and needs its own migration discipline.
* **Driving claims from attribute metadata instead of a view.** Would remove SQL
  authoring entirely, but reintroduces the schema coupling the view exists to
  remove. A later, larger question.

## Open questions

* Does a superseded version's SVG need to be retained for **reprints**, or does
  a reprint use the current active version? (Leaning: reprint reproduces the
  original, so retain.)
* Should a `config_id` be creatable from the UI, or only versions of types the
  manifestation has declared? (Leaning: types are declared by the manifestation,
  versions are managed in the UI.)
* How does this interact with a **registry that has no agent portal** but still
  wants credential types defined?

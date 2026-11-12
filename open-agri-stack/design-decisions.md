---
description: >-
  Why Agri Stack is designed the way it is, and the design changes under
  discussion: the Exchange and the Composite, independent registries, policies in
  Partner Management and consent in the Consent Manager, how departments trust the
  Composite, standards, and the proposal to make the Consent Manager unaware of
  use cases
---

# Design Decisions

This page logs Agri Stack's key design decisions: what was chosen and why. Each
entry has a **status**: *Decided* (built, or agreed and being built) or *Proposed*
(under discussion; nothing changed yet). The design itself is in
[Architecture](architecture/README.md).

| # | Decision | Status |
| --- | --- | --- |
| 1 | [Registries are independent; the Exchange composes](#1-registries-are-independent-the-exchange-composes) | Decided |
| 2 | [The Composite keeps no farmer data](#2-the-composite-keeps-no-farmer-data) | Decided |
| 3 | [Policies in Partner Management, consent in the Consent Manager](#3-policies-in-partner-management-consent-in-the-consent-manager) | Decided |
| 4 | [A use case defines its data; partners are granted use cases](#4-a-use-case-defines-its-data-partners-are-granted-use-cases) | Decided |
| 5 | [Departments trust the Composite, within a ceiling](#5-departments-trust-the-composite-within-a-ceiling) | Decided |
| 6 | [Standard-neutral: DCI is one format](#6-standard-neutral-dci-is-one-format) | Decided |
| 7 | [Reference data in MDS; Beckn only at the network layer](#7-reference-data-in-mds-beckn-only-at-the-network-layer) | Decided |
| 8 | [The Consent Manager is unaware of use cases](#8-the-consent-manager-is-unaware-of-use-cases) | Proposed |
| 9 | [A use-case policy does not list purposes](#9-a-use-case-policy-does-not-list-purposes) | Proposed |

## Decided

### 1. Registries are independent; the Exchange composes

**Decision.** Each department runs its own registry (Farmer Registry, Crop Sown
Registry, …) with its own Partner Management and Consent Manager. Registries share
data, never code: one registry's install never pulls in another's. Partners do not
call the registries; they call the Exchange, whose Composite searches each registry
a use case needs and combines the answers.

**Why.** Departments own their data and release schedules. A partner gets one
answer about a farmer without dealing with each department. See
[Exchange](architecture/exchange.md).

### 2. The Composite keeps no farmer data

**Decision.** The Composite passes each answer on and stores nothing from the
registries. The Exchange stores consents, partners' keys and policies, and audit
records.

**Why.** A copy of registry data at the Exchange would be a second system of
record to protect and keep in step. See
[What it stores](architecture/exchange.md#what-it-stores).

### 3. Policies in Partner Management, consent in the Consent Manager

**Decision.** Partner Management holds who a partner is, its keys and what it may
access (its policies). The Consent Manager holds the farmers' consents. Grants are
approved through Partner Management's onboarding approval. *Decided 2026-09; built
2026-10.*

**Why.** What a partner may access is decided when it is onboarded, by the partner
manager; a consent is one farmer's agreement. Keeping them apart lets each be
approved by the right person. See
[Data-Sharing Policies](architecture/data-sharing-policies.md).

### 4. A use case defines its data; partners are granted use cases

**Decision.** A use case (for example `loan-profile@1`) defines its purpose, the
registries it reads, the data from each and the response. A partner is granted
use cases through a use-case policy in the Exchange's Partner Management. A use
case does not list who may call it, and a partner's grant does not narrow the
use case's data.

**Why.** Who may call a use case is decided at onboarding, not in the use case.
See [Use Cases](architecture/use-cases.md).

### 5. Departments trust the Composite, within a ceiling

**Decision.** To each department, the Composite is one partner, onboarded in the
department's Partner Management with a standing scope policy per registry: the
most the registry releases to it. Partners have no policy in any department. The
department's Consent Manager accepts the Exchange Consent Manager's short-lived
consent tokens. The Exchange's Partner Management does not hold the Composite.

**Why.** A department decides only what it releases, once, and never has to
onboard each partner. See
[Composite as a partner](architecture/exchange.md#composite-as-a-partner).

### 6. Standard-neutral: DCI is one format

**Decision.** Internal records and consent filtering do not depend on one
standard. DCI is one output format among possible others.

**Why.** Countries and partners use different interoperability standards. See
[Standards](architecture/standards.md).

### 7. Reference data in MDS; Beckn only at the network layer

**Decision.** All reference data (crops, seed varieties, farm inputs, livestock,
geography, land) lives in the [Master Data Service](../platform/platform-services/master-data-service/README.md),
defined by the country; international classifications are optional mappings.
Beckn is not used for the registry data layer: its sources are fixed. It belongs
to the network layer above, for discovering providers. IUDX is not used.

**Why.** One versioned catalogue that every registry and service reads. See
[Interoperability with OAN (Beckn)](roadmap/oan-interoperability.md).

## Proposed

### 8. The Consent Manager is unaware of use cases

*Proposed 2026-11-12, from a design review. Nothing is changed yet.*

**What the review observed.**

* **Two cycles at the Exchange.**
  * The Composite reads the partner's use-case policy from the Exchange PM, then
    calls the Exchange CM, which reads the same policy from PM again. One policy
    is enforced in two places, each with its own cache.
  * The Composite calls the Exchange CM to validate, and the CM calls the
    Composite back for the use case's purpose and scopes.
* **Consent is made for a use case.** The Exchange CM records a consent for a use
  case (`name@major`), so the CM depends on an Agri Stack concept, while in the
  departments a consent is for a purpose and data scopes.

**Proposal.** Only the Composite and Partner Management know what a use case is;
the Consent Manager is a generic consent service, the same at the Exchange and in
the departments.

| Component | Holds and does |
| --- | --- |
| **Composite** | The use case definitions: purpose, registries, scopes. Checks that the partner is granted the use case and applies the use-case policy's limits. At validate, sends the CM the use case's purpose and scopes per registry |
| **Partner Management** | Partners' keys, and which partners may use which use cases (use-case policies). To PM, a use case is an item from the Composite's catalogue |
| **Consent Manager** | Consents for a purpose and scopes per registry, as in the departments. At validate: checks that the consent's purpose is the purpose it was sent, intersects the scopes sent with the consent's scopes, and issues consent tokens for the intersection. Reads neither the Composite nor use-case policies |

**The partner portal stays in the Consent Manager**, generic: it offers **consent
templates** (a name, a purpose and the scopes per registry) read from a source set
at install. At the Exchange the source is the Composite, which publishes each use
case as a template; in a department, the registry's data scopes. A consent may keep
the template's name as a label, for display only. Partner Management already reads
its grantable items from a catalogue source in the same way.

**Options considered.**

| Option | Result | Why not |
| --- | --- | --- |
| The CM decides the grant; the Composite stops reading policies | Removes the duplicate policy read | The CM still depends on use cases and on the Composite |
| The Composite decides the grant; the CM checks only the consent, but still makes consents for a use case | Removes the duplicate policy read | The CM still depends on use cases and on the Composite |
| Consents for use cases made through the Composite, not the CM's portal | CM generic | A department has no Composite: the portal must stay in the CM |
| **The CM is generic, with consent templates** (this proposal) | Removes both cycles; one CM everywhere | Larger change |

**Impact.**

* **Consent Manager:** `validate` in use-case mode takes the purpose and scopes
  from the caller; the use-case grant check and the reads of the Composite and of
  use-case policies go; the partner portal and assisted entry offer templates; a
  consent records purpose and scopes. Only the Composite calls the use-case mode
  today.
* **Composite:** publishes use cases as templates; its PM policy read becomes the
  only grant check; applies the use-case policy's limits (subject ID types,
  longest validity, partner-signed consents allowed).
* **Registries:** no change. They use the scope mode, with the policy from the
  department's PM.
* **Still open:** how the limits on consent creation (longest validity,
  partner-signed consents allowed) reach the CM's portal without the CM reading
  use-case policies, for example as part of the template.

### 9. A use-case policy does not list purposes

*Proposed 2026-11-12, from the same review.*

**Observation.** The partner sends a use case; the use case has a purpose; the
Exchange PM grants the use case to the partner. Listing allowed purposes in the
use-case policy repeats what the use case already says.

**Proposal.** Granting a use case grants its purpose: the use-case policy has no
purposes. The allowed purposes stay in the departments' scope policies, where there
is no use case. Today the list is already optional ("Optional limits" in Partner
Management).

**Impact.** Partner Management's use-case policy form and API drop the purposes;
the Composite and the Exchange CM stop checking them. Existing use-case policies
that list purposes need a clean-up.

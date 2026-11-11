# Agency Solution Document

**Version:** 1.0 (Draft for discussion)
**Status:** Strategy / design discussion. No implementation has started.

## 1. Purpose

Programs delivered through the OpenG2P platform rely on field-level partners to enrol beneficiaries and hand over benefits. Examples are NGOs, banks' business correspondents, cooperatives, and local-government outreach teams. This document defines the **Agency Solution**, which lets a department:

- onboard and govern such **agencies**,
- let each agency manage its own **agents**,
- let agents perform registry (enumeration) and disbursement work, online or offline, from an Android tablet,
- keep every action within the **data scope** the department intended.

This version covers ideas, requirements and design direction only.

## 2. Terminology

| Term | Meaning |
|---|---|
| Department staff | Government/program staff who operate the registry and workflows (verification, approval). Existing staff users. |
| Agency | An external organisation authorised by the department to work in a defined geography/scope. |
| Agent | A person belonging to exactly one agency who works in the field. |
| Agency administrator | The first agent of an agency. Manages the other agents of that agency. |
| Data policy | A rule restricting which records a user may see or act on (for example, by geography). |
| Evidence | Artefacts captured at disbursement to prove delivery. |

## 3. Scope

### In scope
1. Agency lifecycle management (create, enable, disable).
2. Agent lifecycle management under an agency.
3. Agent authentication and authorisation (OIDC, Keycloak by default).
4. Data policies for agencies and agents, with agent policies as a strict subset of the agency policy.
5. Registry functionality for agents: intake forms, change requests, and other staff-equivalent operations except workflow actions.
6. Agent allocation to work (enumeration areas, disbursement tasks).
7. Disbursement execution by agents with evidence capture.
8. Android tablet application with full offline support for enumeration and disbursement.

### Out of scope (for v1)
- Payment rails and reconciliation logic (stays in G2P Bridge).
- Agency commission/payout calculation (candidate for a later version).
- iOS or web clients for agents.

## 4. Requirements

### 4.1 Agency management
- **R1.** Department staff create agencies and, at creation, the **first agent**, who becomes the agency administrator.
- **R2.** Staff can **enable or disable** an agency. Disabling an agency immediately blocks all its agents from API access, including new logins and existing tokens.
- **R3.** Staff-facing operations are exposed through a dedicated **agency-management-staff-api**.

### 4.2 Agent management
- **R4.** The agency administrator adds, edits, suspends and removes agents within their own agency only.
- **R5.** An agent belongs to exactly one agency.
- **R6.** Agents are authenticated via OIDC. They live in a **separate Keycloak realm, `openg2p-agents`**, apart from the staff realm. Other OIDC providers must remain pluggable.
- **R7.** The access token carries a **claim identifying the agent's agency** (for example `agency_id`). Services trust this claim and never accept it from the request body.

### 4.3 Registry functionality
- **R8.** Agents can do everything staff can do on the registry, **except workflow operations**.
- **R9.** **Verification and approval are staff-only.** Agents can *initiate* intake form submissions and change requests, which then enter the staff workflow.
- **R10.** Agents are subject to data policies, as staff already are.

### 4.4 Data policies
- **R11.** Data policies can be defined at **agency** level and at **agent** level.
- **R12.** An agent's policies must be a **subset** of the agency's policies. Example: the agency is scoped to State X, and its agents are scoped to individual districts within State X.
- **R13.** Effective access is the intersection of the agency policy and the agent policy. If the agency policy later shrinks, agent policies are automatically clamped (see 8.4).

### 4.5 Allocation
- **R14.** G2P Bridge allocates **agencies** to disbursement work based on geography.
- **R15.** Agent allocation within an agency must respect each agent's data policies (see section 7 for the recommended owner).

### 4.6 Disbursement by agents
- **R16.** Agents can effect disbursements for beneficiaries assigned to them.
- **R17.** For each disbursement the app captures evidence:
  - photograph of the beneficiary,
  - geo-coordinates of the location,
  - biometric verification of the beneficiary,
  - beneficiary confirmation (signature and/or thumb print),
  - date-time stamp.

### 4.7 Offline and device
- **R18.** An Android application on a tablet.
- **R19.** Enumeration (registry work) and disbursement both work **offline** and sync when connectivity returns.

## 5. Solution overview

```
                     +-----------------------+
 Department staff -->| Staff Portal          |
                     +----------+------------+
                                |
                   agency-management-staff-api
                                |
        +-----------------------v------------------------+
        |                 AGENCY SERVICE                 |
        |  agencies | agents | agency/agent policies     |
        |  agent allocation | sync coordination          |
        +--+----------+-----------+---------------+------+
           |          |           |               |
           |          |           |               |
   Keycloak realm   Registry   G2P Bridge     Evidence store
   openg2p-agents   (intake,   (agency        (object storage)
   (agent identity) change     allocation,
                    requests)  disbursement)
           ^
           |  OIDC (PKCE) + agency claim
   +-------+--------------------------+
   |  Agent Android App (tablet)      |
   |  local encrypted DB + sync engine|
   +----------------------------------+
```

### Components
1. **Agency Service** (new repo). Owns agencies, agents, agency/agent data policies, and agent allocation. Exposes:
   - **agency-management-staff-api** for department staff (create/enable/disable agency, view agents).
   - **agency-admin-api** for agency administrators (manage agents, set agent policies, allocate work).
   - **agent-api** for agents (profile, assignments, sync endpoints).
2. **Keycloak, realm `openg2p-agents`.** Holds agent identities. A protocol mapper adds `agency_id` (and the agent role) to the token.
3. **Registry.** Existing. Needs to recognise agent actors, enforce data policies for them, and block workflow actions for agents.
4. **G2P Bridge.** Existing. Allocates agencies to disbursement work by geography and receives disbursement confirmations with evidence references.
5. **Evidence store.** Object storage for photos, signatures and biometric artefacts, referenced from the disbursement record.
6. **Agent Android app.** Offline-first client.

## 6. Identity and access

### 6.1 Authentication
- OIDC authorisation code flow with PKCE from the Android app. Keycloak is the default, and any OIDC provider that can issue the required claims is acceptable.
- The staff realm and the agent realm are kept separate. This keeps agent credential policies, session lifetimes and attack surface apart from staff.

### 6.2 Token claims (proposed)
| Claim | Purpose |
|---|---|
| `sub` | Agent identifier |
| `agency_id` | Agency the agent belongs to |
| `roles` | `agency_admin` or `agent` |
| `device_id` (optional) | Binds the token to a registered tablet |

### 6.3 Authorisation layers
1. **Role**: what operations the actor may call (agent vs agency admin vs staff).
2. **Actor type rule**: workflow operations (verification, approval) are rejected for agent tokens at the registry.
3. **Data policy**: which records the actor may touch (section 8).
4. **Agency state**: a disabled agency is rejected regardless of token validity.

### 6.4 Disabling an agency
Disabling must take effect quickly, not only at next login. Options, with a recommendation:
- Keycloak: disable all users of the agency or revoke sessions. Slow for large agencies.
- **Recommended:** services check agency status (cached for a short time, for example 1 to 5 minutes) on each request, in addition to revoking sessions. This is a single flag and is not dependent on token expiry.

Offline behaviour is covered in section 9.5.

## 7. Agent allocation: where should it live?

**Question:** should agent allocation happen in G2P Bridge or in the Agency Service?

**Recommendation: Agency Service owns agent allocation. Bridge allocates only to the agency level.**

Reasons:
- Bridge already allocates by geography to agencies. Pushing further down to individual agents would force Bridge to know about agents, agent policies and agent availability, which are agency concepts.
- Agent data policies live in the Agency Service. Allocation must honour them (R15), so the data is already there.
- Agencies often want their own say in who does what (workload, language, trust). The agency administrator can adjust the allocation.
- The same allocation mechanism can serve **enumeration** work too, which has nothing to do with Bridge.
- Bridge stays a payments component, and can serve non-agent channels unchanged.

**Proposed flow (disbursement):**
1. Bridge produces disbursement batches and allocates each work item to an agency by geography.
2. Bridge notifies the Agency Service with the work items (beneficiary reference, location, amount reference).
3. Agency Service allocates each item to an agent whose data policy covers the beneficiary's location. Allocation can be automatic (rules: geography, load balancing) or manual by the agency administrator.
4. The agent's app downloads its assignments.
5. After delivery, the app syncs the result and evidence. The Agency Service validates and forwards the confirmation to Bridge.

**Open sub-questions:** reallocation when an agent is suspended or unavailable; whether Bridge should be told which agent was allocated (for audit) or only the agency.

## 8. Data policies

### 8.1 Model
A data policy is a set of constraints, for example `geo: State = X` or `geo: District in [A, B]`. Policies exist on:
- the **agency** (the outer boundary set by the department), and
- each **agent** (set by the agency administrator, within the agency boundary).

### 8.2 Subset rule
When the agency administrator assigns an agent policy, the Agency Service validates it is contained in the agency policy. Example:

| Level | Policy |
|---|---|
| Agency | State = Karnataka |
| Agent 1 | Districts = Mysuru, Mandya |
| Agent 2 | District = Hassan |

An attempt to give an agent a district outside the state is rejected.

### 8.3 Enforcement
- The Registry enforces policies for agent actors in the same way as for staff, using the agent's effective policy (intersection of agency and agent policies).
- The effective policy is resolved server-side from `sub` and `agency_id`. It is not placed whole in the token, because policies change and may be large.
- The Agency Service exposes a policy-resolution endpoint that the Registry and Bridge can call (or cache).

### 8.4 Policy changes
- If the department narrows an agency policy, agent policies that fall outside it are **clamped automatically**, and the administrator is notified.
- Narrowing a policy affects offline devices: data already on a tablet may fall outside the new scope. See 9.5.

### 8.5 Policy dimensions
V1 should support geography. The design should allow other dimensions (program, record type) without redesign. This should reuse the existing staff data-policy engine rather than introduce a second one. **To confirm:** how the current staff data-policy model expresses geography and whether it can be reused as-is.

## 9. Agent Android application

### 9.1 Functions
- Login (OIDC), device registration.
- Enumeration: fill intake forms, create change requests, view records within policy.
- Disbursement: view assignments, verify beneficiary, collect evidence, confirm disbursement.
- Sync status, conflict and error review.

### 9.2 Offline-first design
- All work is performed against a **local encrypted database**. The UI never waits on the network.
- A **sync engine** runs a queue of outbound operations (intake submissions, change requests, disbursement confirmations with evidence) and pulls inbound data (assignments, forms, master data, scoped beneficiary lists).
- Each operation carries a **client-generated unique ID** so retries are idempotent.
- Large evidence artefacts upload separately from the transaction record, with resume support, and are linked by reference.

### 9.3 Data downloaded to the device
Only what the agent's policy and assignments require:
- form definitions and master data (geographies, code lists),
- assigned beneficiaries and disbursement tasks,
- a limited set of beneficiary fields needed for verification (minimised).

### 9.4 Evidence capture at disbursement
| Evidence | Notes |
|---|---|
| Beneficiary photograph | Camera capture, no gallery import |
| Geo-coordinates | GPS at time of disbursement; record accuracy and flag mock-location |
| Biometric verification | Open question (see section 12): on-device match vs server match |
| Beneficiary confirmation | Signature and/or thumb print |
| Date-time stamp | Device time plus server receive time, to detect clock tampering |

All evidence is bundled into one disbursement record, hashed, and linked to the assignment. The bundle must be **tamper-evident**, so that later alteration is detectable.

### 9.5 Offline security and policy enforcement
- Data at rest encrypted with a key protected by the Android Keystore. Remote wipe or lock on device deregistration.
- App PIN/biometric unlock on top of OIDC login.
- **Offline session window:** the agent can keep working offline for a configured period (for example N days) after the last successful token refresh. After it expires, the app locks until the device reconnects.
- On reconnect, before sync, the app checks agency status and agent status. If the agency is disabled, pending items are **held** (not silently discarded) for staff decision.
- If data policy has changed, previously collected offline records outside the new scope are accepted or rejected by a defined rule. **Proposed:** accept work done under the policy valid when the task was assigned, flag for staff review.

### 9.6 Conflicts
- Enumeration: new records rarely conflict. Duplicate detection is a registry concern after sync.
- Change requests: server-side versioning. If the underlying record changed since the agent downloaded it, the change request is flagged for staff review, not auto-merged.
- Disbursement: a task can be completed only once. If it was reassigned or already completed, the second submission is rejected and surfaced to staff.

## 10. Registry integration

- Registry APIs need to recognise an **agent actor** (type, agency, agent ID) for audit, policy and workflow rules.
- Agents' intake submissions and change requests enter the **same workflow** as staff-originated ones, with the origin recorded (agency and agent). Verification and approval steps remain exclusively staff.
- Audit entries record agency and agent.
- **To confirm:** whether agent-initiated records need a separate initial state (for example "submitted by agent, pending staff verification") or the existing workflow states are sufficient.

## 11. Disbursement integration (G2P Bridge)

- Bridge allocates agency by geography and hands work items to the Agency Service.
- On completion, the Agency Service sends Bridge a confirmation containing evidence references and a summary. Bridge treats the evidence as supporting data for the disbursement record.
- Cash-in-hand style disbursement fits this flow directly. Other benefit types (in-kind, vouchers) can reuse the same evidence model.

## 12. Open questions and decisions needed

| # | Question | Leaning |
|---|---|---|
| 1 | Agent allocation owner | Agency Service (section 7) |
| 2 | Biometric match: on-device (offline-capable) or server-side? Offline disbursement implies on-device, which means templates must be downloaded to the tablet. This raises privacy and storage concerns. | On-device matching against minimised templates; needs a privacy review |
| 3 | Offline session window length and what happens at expiry | Configurable per agency, default to be set |
| 4 | Can an agency administrator also perform field work? | Yes, same account, with admin role added |
| 5 | Multiple administrators per agency, and recovery if the only administrator leaves | Allow more than one; staff can reset |
| 6 | Can an agent belong to more than one agency? | No in v1 |
| 7 | Which agent-facing registry operations map to "all staff functionality"? Needs an explicit operation-by-operation list | Produce a matrix with the registry team |
| 8 | Reuse of staff data-policy engine for agency/agent policies | Reuse; confirm it supports subset validation |
| 9 | Device management: one agent per tablet, shared tablets, MDM | Device registration at minimum; MDM optional |
| 10 | Handling of work held when an agency is disabled mid-sync | Hold for staff decision |
| 11 | Evidence retention period and legal admissibility of captured artefacts | Program-level policy; must be confirmed |
| 12 | Language/localisation and low-literacy UX on the tablet | Required; scope in a UX study |
| 13 | Does Bridge need to know the specific agent, or only the agency? | Agency only for allocation; agent ID carried in the confirmation for audit |

## 13. Non-functional considerations
- **Privacy and consent:** beneficiary data on devices is minimised and encrypted. Consent capture for biometrics and photographs is a program decision, and the app must support recording it.
- **Scale:** many agents syncing in bursts (end of day). Sync endpoints must be idempotent and resumable.
- **Auditability:** every agent action is attributable to agent, agency and device.
- **Availability:** agent-facing APIs must degrade gracefully, since the app is offline-first and tolerates outages.
- **Low-bandwidth:** compact payloads, delta sync, deferred media upload.

## 14. Suggested phasing

| Phase | Content |
|---|---|
| 1 | Agency Service: agencies, agents, Keycloak realm and token claim, staff API for enable/disable |
| 2 | Agency and agent data policies; registry enforcement and workflow restriction |
| 3 | Android app: online enumeration (intake, change request), then offline and sync |
| 4 | Agent allocation and disbursement with evidence capture, Bridge integration |
| 5 | Hardening: device management, offline policy-change handling, reporting |

## 15. Proposed new repository

`agency-service` (name to be confirmed) containing the service and its APIs. The Android app would be a separate repository (for example `agent-app-android`).

## 16. Next steps
1. Review this document and settle the open questions in section 12, especially items 1, 2, 7 and 8.
2. Confirm the staff data-policy model and how it extends to agencies and agents.
3. Produce the operation-by-operation permission matrix for agents versus staff on the registry.
4. Then move to detailed design (data model, API specification, sync protocol).

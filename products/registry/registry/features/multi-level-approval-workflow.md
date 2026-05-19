# Multi-Level Approval Workflow

The OpenG2P Registry integrates with the Approval Workflow Engine (AWE) to enforce configurable, multi-stage human approval for every change request and intake form submission. No data mutation — whether initiated by a staff officer, an ingestion pipeline, or an API caller — is committed to the master registry until it has cleared all approval stages defined by the applicable policy. The Registry owns the data and enforces governance; AWE owns the approval orchestration. Together they provide a complete audit-grade change governance layer that can be configured by an administrator without writing code.

***

## End-to-End Flow of Control

Understanding how control passes between the Registry and AWE helps clarify the responsibility of each system:

1. **Submission** — A staff officer submits a change request or an intake form. The Registry validates the payload, persists the proposed change in the change log (shadow table), and marks the artifact's approval status as `PENDING`.
2. **Policy Resolution** — The Registry looks up the most specific AWE policy binding for that artifact — at the register, intake form, or section level — and retrieves the corresponding policy key.
3. **AWE Request Creation** — The Registry calls AWE's `POST /v1/awe/requests` API, forwarding the `artifact_type`, `policy_key`, and a context snapshot derived from the submitted record (field values relevant to approver resolution, such as `record_name`, `register_mnemonic`, and `section_mnemonic`).
4. **Stage Orchestration (AWE)** — AWE evaluates the policy, resolves approvers for the first stage, creates tasks, and assigns them to the resolved approvers. If the policy has parallel stages within a group, AWE creates tasks for all parallel approvers simultaneously.
5. **Approver Action** — Approvers log into the Staff Portal, find their pending tasks in the **Tasks** inbox, open the artifact detail, and record a decision. Each decision is forwarded to AWE via the Registry's proxy endpoint.
6. **Stage Progression (AWE)** — When enough decisions accumulate to satisfy the stage's quorum mode, AWE marks the stage complete and activates the next stage's tasks — or, if the last stage is cleared, resolves the overall request as approved or rejected.
7. **Webhook Delivery** — AWE fires a signed webhook to the Registry containing the final outcome (`request_approved` or `request_rejected`).
8. **Commit or Discard** — The Registry verifies the webhook signature, updates the artifact's approval status, and either writes the proposed change to the master registry table (approved) or discards it (rejected), creating a version history entry in either case.

***

## Policy Configuration

#### Scope-Based Policy Bindings

Approval policies are bound to artifacts through the Staff Portal's **Configuration → AWE Policy Configuration** screen. Each binding maps a policy type and key to a scope: an entire register, a specific intake form within a register, or a single section of an intake form. When a new artifact is submitted, the Registry resolves the binding by walking from the most specific scope (section) up to the least specific (register), applying the first match. This means section-level policies override intake-form–level policies, which in turn override register-level policies.

#### No-Code Administration

Adding, editing, or disabling a policy binding requires no deployment and no code change. An administrator with the appropriate configuration permission can update bindings at any time. The new binding takes effect for all artifacts submitted after the change; in-flight approval requests continue under the policy that was active when they were created.

#### Context Field Selection

Each policy binding specifies a `context_field_names` list that controls which fields from the submitted record are included in the context snapshot forwarded to AWE. Approver-resolution rules in AWE can evaluate these fields — for example, routing a change to a district supervisor whose identifier is stored in the record — without the Registry needing to know the approval logic.

***

## Approval Stages and Modes

#### Sequential and Parallel Stages

An AWE policy is composed of one or more stages. Stages in a policy are sequential by default: stage 2 does not start until stage 1 is fully resolved. Within a single stage, multiple approver groups can be configured to run in parallel — all must complete before the stage advances. This allows a policy such as "field officer first, then district head, then finance controller" to be expressed as three sequential stages, while "two independent district heads must both sign off" is expressed as a single stage with two parallel groups.

#### Approver Resolver Types

Each stage resolves approvers through one of several built-in resolver types. A `user` resolver assigns the task to a specific Keycloak user. A `role` resolver assigns it to all active users carrying a given Keycloak role. A `group` resolver targets members of a Keycloak group. A `json_logic` resolver evaluates a JSON Logic expression against the request's context snapshot to compute the assignee at runtime — enabling dynamic routing based on record data. An `http` resolver calls an external API to retrieve the assignee list, supporting integration with external roster or HR systems.

#### Quorum Modes

Not all parallel approvers in a group are always required. The quorum mode for a group can be set to `all` (every assigned approver must act), `any_N` (at least N of the assigned approvers must act), or a percentage-based threshold. If any approver in a group rejects, the stage and the overall request are rejected immediately regardless of the quorum mode, unless the policy is configured to allow overrides.

#### Segregation-of-Duty

AWE enforces configurable segregation-of-duty guards to prevent conflicts of interest. The submitter of a change request can be excluded from approving it at any stage. A single approver can be restricted from acting on more than one stage of the same request. These guards are declared in the policy and enforced by AWE automatically; the Registry does not need to implement them.

***

## Approver Inbox

#### Task Cards for Change Requests and Intake Forms

The Staff Portal's **Tasks** section contains two sub-views: **Change Request Tasks** and **Intake Form Tasks**. Each view lists only the tasks assigned to the currently logged-in user. Task cards display the record name, register, section or form identifier, current approval stage number, task kind (approver or observer), task status, creation date, and SLA due date. The task status follows a standard lifecycle: `open` → `claimed` → `completed` (or `cancelled`). The inbox is paginated and supports search by context fields such as record name or section identifier.

#### Navigating to the Artifact Detail

Selecting **View Details** on a task card opens the full artifact detail page — the change request view showing the proposed field-level diff against the current record, or the intake form submission view showing the full submission. The approver reviews the content and the context before recording a decision. All approval actions are available directly on the artifact detail page, and the Registry proxies those actions to AWE on the approver's behalf, so the approver never leaves the Registry staff portal.

#### Observer Tasks

Policies may include observer stages alongside approver stages. Observers receive tasks and are notified of the approval progress but their action is not required for the stage to advance. Observers see their tasks in the same inbox alongside approver tasks, distinguished by the `kind: observer` label.

***

## Task Lifecycle Actions

#### Claiming and Deciding

An approver can optionally claim an open task to signal that they are actively reviewing it, preventing duplicate effort in shared-role scenarios. A claimed task is locked to the claiming approver. Once ready, the approver records a decision — **approve**, **reject**, or **abstain** — with an optional written comment. All decisions are forwarded to AWE and stored as immutable decision records.

#### Delegation

When an approver is unavailable — on leave, for example — they can create a delegation window in the Staff Portal specifying a delegate user and a validity period. Any new tasks that would be assigned to them during the window are automatically redirected to the delegate. The task records both the original intended assignee and the delegate for full auditability. Delegation does not affect tasks already assigned before the window begins.

#### Administrator Reassignment

For tasks that cannot be handled through delegation — for example, when an approver leaves the organisation — an administrator can reassign any open or claimed task to a different user from the task detail view. The reassignment preserves the original SLA deadline and adds a reassignment event to the task's audit log.

***

## SLA Enforcement and Escalation

Each approval stage in a policy can carry a deadline expressed in hours. The Staff Portal surfaces this deadline on every task card so approvers can prioritise expiring tasks. When a stage deadline passes, AWE fires a breach event. Depending on the policy's breach action, AWE can automatically escalate to a new assignee set, auto-approve the timed-out stage, auto-reject the entire request, or leave it open for operator intervention. The Registry receives the final outcome through its existing webhook handler regardless of whether the resolution was human-driven or automated.

***

## Audit Trail and Event Timeline

#### Approval Event Timeline per Artifact

Every state change in the approval lifecycle — request created, stage started, task assigned, task claimed, decision submitted, stage completed, request approved or rejected — is captured as an immutable event in AWE and surfaced on the artifact detail page in the Staff Portal as a chronological event timeline. Each entry records the actor's identity, the action, the timestamp, and any comment. This complements the registry's own version history table and gives auditors a complete, tamper-evident record of who reviewed a proposed change and what they decided.

#### Registry Version History

When an approval completes and the Registry commits the change to the master record, it creates a new entry in the register's version history table recording the final state, the timestamp, and the AWE request ID that authorised the mutation. This ties the data-layer audit trail directly to the AWE approval audit trail, enabling end-to-end traceability from submission through approval to committed record state.

***

## Related Pages

* [AWE Integration — Design](https://docs.openg2p.org/products/registry/registry/design/awe-integration.md) — architecture, data model changes, component responsibilities, and the full happy-path sequence diagram.
* [Change Management & Approval Workflow](https://docs.openg2p.org/products/registry/registry/features/change-management-and-approval-workflow.md) — the underlying change request model that the multi-level approval workflow gates.
* [Approval Workflow Engine](https://docs.openg2p.org/platform/platform-services/approval-workflow-engine) — AWE standalone documentation: policy authoring, API reference, and deployment guide.

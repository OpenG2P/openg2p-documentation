# Scenarios catalog

A scan-friendly index of approval patterns AWE can model. Each row points
at the configuration knob (or knobs) that produces it and the how-to
guide that walks through the setup.

> If your scenario isn't listed here, it's likely a combination of a few
> rows below. The four primitives — **stages, rules, modes, and skip /
> escalation policies** — compose freely. Rare patterns AWE intentionally
> doesn't support are listed at the bottom.

## Stage shapes

| # | Scenario | How to configure | Reference |
|--|--|--|--|
| 1 | **Single approver, single stage** ("manager signs off") | One stage, `mode = all`, one `user` rule | [Stage modes](functional-specifications.md#stage-modes) |
| 2 | **Sequential N-stage approval** ("officer → director → secretary") | N stages with distinct `stage_order`; default `parallel_group = null` | [Functional spec → Policy model](functional-specifications.md#policy-model) |
| 3 | **Parallel stages** ("Legal AND Finance, then Director") | Set the same `parallel_group` value on each stage that should run together | [How-to: Run stages in parallel](how-to/parallel-stages.md) |
| 4 | **Single stage with multiple stages following** | Combine #2 and #3 — sequential groups of one or many stages | — |

## Decision modes within a stage

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 5 | **All approvers must approve** | `mode = all` | [Stage modes](functional-specifications.md#stage-modes) |
| 6 | **First N of M approve** ("any 2 of 5") | `mode = any-n`, `mode_value = 2` | [Stage modes](functional-specifications.md#stage-modes) |
| 7 | **Percentage quorum** ("60% of resolved approvers") | `mode = percentage`, `mode_value = 60` | [Stage modes](functional-specifications.md#stage-modes) |
| 8 | **Quorum + a mandatory signature** ("any 2 of 5, but the CEO must be one of them") | `mode = any-n` plus a rule with `required: true` | [How-to: Required approver](how-to/required-approver.md) |
| 9 | **Veto by any single approver** | Already implicit — any `reject` decision terminates the request |  — |

## Approver-resolution patterns

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 10 | **Literal user** | `rule_type = user`, `rule_value = {"user_id": "u-alice"}` | [Rule types](functional-specifications.md#approver-rule-types) |
| 11 | **Anyone holding a Keycloak realm role** | `rule_type = role`, `rule_value = {"role": "DISTRICT_OFFICER"}` | [Rule types](functional-specifications.md#approver-rule-types) |
| 12 | **Anyone holding a role on a specific Keycloak client** ("Registry's `PROGRAM_MANAGER`") | `rule_type = role`, `rule_value = {"role": "PROGRAM_MANAGER", "client": "registry-staff-portal"}` | [How-to: Use a client role in a rule](how-to/client-role-rule.md) |
| 13 | **Members of a Keycloak group path** | `rule_type = group`, `rule_value = {"group": "/states/MH/officers"}` | [Rule types](functional-specifications.md#approver-rule-types) |
| 14 | **Approvers depend on the artifact's data** ("officers of *the request's* district") | `rule_type = expression` with JSONLogic over `context`, OR `rule_type = http` to a Caller-side resolver | [Rule types](functional-specifications.md#approver-rule-types) |
| 15 | **Multiple rules combined** | Rules within a stage union; a user is eligible if **any** rule resolves them | [Rule types](functional-specifications.md#approver-rule-types) |

## Conditional & branching flows

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 16 | **Skip a stage based on artifact data** ("skip Director if amount < 10 000") | `skip_if` (JSONLogic over context) on the stage | [How-to: Skip a stage](how-to/conditional-skip.md) |
| 17 | **Auto-skip when no approvers resolve** | `on_empty = "skip"` on the stage | [Skip rules](functional-specifications.md#skip-rules) |
| 18 | **Auto-reject when no approvers resolve** | `on_empty = "block"` (default) | [Skip rules](functional-specifications.md#skip-rules) |
| 19 | **Tiered routing by amount / category** ("0–10k peer; 10k–1L director; 1L+ secretary") | One stage per tier, each with its own `skip_if` so only the matching tier activates | combine #16 + #2 |

## SLA & timeout handling

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 20 | **Notify on SLA breach, Caller decides** | `sla_hours` set, `on_breach = notify` (default) | [SLA section](functional-specifications.md#sla-and-escalation) |
| 21 | **Auto-escalate to supervisors after SLA** | `sla_hours` set, `on_breach = escalate`, supervisors as `escalation_rules` | [How-to: SLA escalation](how-to/sla-escalation.md) |
| 22 | **Auto-approve if no one responds in time** | `on_breach = auto_approve` | [SLA section](functional-specifications.md#sla-and-escalation) |
| 23 | **Auto-reject if no one responds in time** | `on_breach = auto_reject` | [SLA section](functional-specifications.md#sla-and-escalation) |

## People management

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 24 | **Out-of-office redirect** ("Alice on leave → tasks go to Bob") | Create a delegation row with start/end window | [How-to: Delegation](how-to/delegation.md) |
| 25 | **Pull a stuck task and reassign** | Admin clicks Reassign on the task in the Request detail page | [How-to: Reassign task](how-to/reassign-task.md) |
| 26 | **Non-blocking reviewer** ("Legal must see this but isn't required to approve") | Add a rule with `kind = observer` | [How-to: Add an observer](how-to/observers.md) |
| 27 | **Submitter can't approve their own request** | `forbid_self_approval = true` on the policy | [How-to: Segregation of duties](how-to/segregation-of-duties.md) |
| 28 | **Same person can't approve consecutive stages** | `forbid_repeat_approvers = true` on the policy | [How-to: Segregation of duties](how-to/segregation-of-duties.md) |

## Lifecycle & integration

| # | Scenario | Configuration | Reference |
|--|--|--|--|
| 29 | **Caller cancels a request mid-flight** | `POST /v1/awe/requests/{id}/cancel` with reason | [Request lifecycle](functional-specifications.md#request-lifecycle-state-machine) |
| 30 | **Caller wants ack on every status change** | Provide `callback_url` on the request — AWE pushes signed webhooks | [Webhooks](functional-specifications.md#events-and-webhooks) |
| 31 | **Retry-safe request creation** | Pass `Idempotency-Key` header; AWE replays the stored response on retry | [Idempotency](functional-specifications.md#idempotency) |
| 32 | **Run a request through historical policy logic** (no rewrite mid-flight) | Automatic — requests are pinned to the policy version they started under | [Versioning](functional-specifications.md#policy-versioning-mutable-drafts-immutable-activated-versions) |
| 33 | **Try a policy on sample data without creating a real request** | `POST /v1/awe/policies/{key}/versions/{v}/simulate` with a sample context | [API reference](api-reference.md) |

## Composing patterns

The scenarios above compose. A few common combinations:

* **Govt CR-style 3-stage with quorum + escalation:**
  Stage 1 single officer (mode=all). Stage 2 quorum 2-of-3 directors with
  SLA + escalate. Stage 3 single secretary, with `forbid_repeat_approvers`
  to keep stage 2 directors out.

* **Disbursement-tier flow:**
  Three stages, all guarded with mutually-exclusive `skip_if` JSONLogic on
  amount thresholds. Only one tier activates per request.

* **Legal-and-finance gate before sign-off:**
  Stages 1 + 2 share `parallel_group = 1` (Legal, Finance, both `mode=all`).
  Stage 3 is the Director (sequential after the group).

## What AWE intentionally does NOT do

These are real approval-workflow features, but they live outside the
"resolve approvers + record decisions" boundary AWE keeps. Don't expect
to find them.

| Out-of-scope | Where the responsibility belongs |
|--|--|
| **Send-back / return-for-revision** as an AWE primitive | Caller cancels the request when revision is requested; resubmit creates a fresh request after the artifact is amended (see the design discussion in [functional-specifications.md → Request lifecycle](functional-specifications.md#request-lifecycle-state-machine)). |
| **Centralized approver inbox spanning multiple Callers** | AWE is federated — approvers act in the Caller's UI. Adding a unified inbox is possible but additive (out of scope today). |
| **Storing the artifact itself** (PDFs, beneficiary records, transaction details) | Caller stores the artifact; AWE only holds an `(artifact_type, artifact_id)` reference and the resolution `context` (the small subset of fields the rules need). |
| **Arbitrary BPMN / DAG workflows** with joins, splits, sub-processes | AWE is sequential groups of optionally-parallel stages, not a generic workflow orchestrator. Use a BPMN engine if you need those. |
| **Weighted votes** ("CEO counts as 2") | Use `required: true` instead — semantically clearer and fits the SoD model. |
| **Time-bound approvals** ("approval expires after 30 days") | If the artifact needs re-approval after a period, the Caller initiates a fresh request. |

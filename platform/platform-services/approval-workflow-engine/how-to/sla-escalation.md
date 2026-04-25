# Configure SLA escalation

1. Open the policy version (draft) in the editor.
2. On the stage, set **SLA (hours)** — e.g. `48`.
3. Set **On SLA breach** to one of:
   * **notify** — emit `task_expired` events; Caller decides what to do (default).
   * **auto-approve** — synthesize approve-decisions for all open tasks; advance.
   * **auto-reject** — synthesize reject-decisions; terminate the request.
   * **escalate** — add fresh approvers from the rules below.
4. If you chose **escalate**, an **Escalation rules** block appears. Click
   **+ Add rule** and add one or more rules (user / role / group / etc.) that
   resolve to the escalation approvers (e.g. the supervisors).
5. Save and activate.

The SLA monitor scans every `sla.checkIntervalSeconds` (default 300s). When a
task's `due_at` passes, its stage's `on_breach` action fires once for the
stage even if multiple tasks expire together.

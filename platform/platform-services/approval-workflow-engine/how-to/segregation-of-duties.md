# Forbid self-approval & repeat approvers

1. Open the policy version (draft) in the editor.
2. In the **Metadata** card, tick either or both:
   * **Forbid self-approval** — the request's `requester` is filtered out of
     every stage's approver list.
   * **Forbid repeat approvers across stages** — anyone who approved an
     earlier stage of the same request is filtered out of later stages.
3. Save and activate.

Filters apply at task-creation time. A stage that loses every eligible
approver because of a filter follows the stage's **If no approvers resolve**
setting (skip or block).

Applies only to `approver` rules; observers are never filtered.

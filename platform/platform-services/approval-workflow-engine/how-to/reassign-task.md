# Reassign a stuck task

1. In the AWE admin portal, open **Requests** and click the request id.
2. In the **Stages** card, find the open task you want to move.
3. Click **Reassign** on that task's row.
4. Enter the new assignee's user id (e.g. `u-bob`).
5. Enter a reason when prompted (optional but recommended for audit).

The original task is closed with status `reassigned`. A fresh task is
created for the new user with the original `due_at` preserved. The new
task's row shows "(reassigned from <original_user>)".

Reassign is admin-only (`AWE_ADMIN`). For ongoing leave coverage prefer
[delegation](delegation.md) — it auto-applies to future tasks.

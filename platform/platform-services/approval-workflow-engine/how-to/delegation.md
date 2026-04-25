# Set up out-of-office delegation

1. In the AWE admin portal sidebar, click **Delegations**.
2. In **New delegation**, enter:
   * **User** — the Keycloak user id who is going on leave (e.g. `u-alice`).
   * **Delegate to** — the substitute's user id (e.g. `u-bob`).
   * **Starts at** / **Ends at** — the leave window (your local time).
   * **Reason** — optional.
3. Click **Create delegation**.

While the window is active, any **new** task that would have been assigned
to the user is created for the delegate instead. The task's row shows
`(← original_user)` for audit. Existing tasks are not retroactively
reassigned — use [Reassign a stuck task](reassign-task.md) for those.

To end a delegation early: open Delegations and click **Delete** on the row.

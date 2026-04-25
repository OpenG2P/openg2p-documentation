# Add a non-blocking observer

1. Open the policy version (draft) in the editor.
2. On the stage, click **+ Add rule** and configure who the observer is
   (user / role / group / etc.) — same as for an approver rule.
3. On that rule's row, change the **kind** dropdown from `approver` to
   `observer`. The **required** checkbox automatically disables.
4. Save and activate.

Observers receive a task on the stage, can read the request and post a
comment, but their (in)action does NOT block stage completion. Use this for
roles like Legal or Audit that need visibility but shouldn't gate the flow.

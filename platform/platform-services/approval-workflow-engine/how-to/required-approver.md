# Mark a required (must-approve) approver

1. Open the policy version (draft) in the editor.
2. On the stage, add (or open) the rule whose resolved user(s) must approve.
3. Tick the **required** checkbox on that rule's row.
4. Save and activate.

The stage now passes only when **both** the quorum mode is satisfied **and**
every user resolved by every `required` rule has approved. If a required user
has no remaining open task (expired, reassigned away, etc.), the stage is
rejected.

Common pattern: stage with `mode = any-n`, `mode_value = 2`, three rules
where one is marked required → "any 2 of 3 must approve, but the third one
is mandatory."

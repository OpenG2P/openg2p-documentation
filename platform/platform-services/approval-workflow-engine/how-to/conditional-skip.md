# Skip a stage based on context

1. Open the policy version (draft) in the editor.
2. On the stage you want to make conditional, fill **Skip if (JSONLogic)**.
3. Use a JSONLogic expression that returns truthy to skip. Examples:
   * Skip when amount under 10 000: `{"<=":[{"var":"amount"},10000]}`
   * Skip for a specific district: `{"==":[{"var":"district"},"D1"]}`
   * Skip unless flagged: `{"!":{"var":"high_risk"}}`
4. Save and activate.

The expression evaluates against the request's frozen `context`, and is
checked when the stage would otherwise activate. A skipped stage emits a
`stage_skipped` event and the flow advances.

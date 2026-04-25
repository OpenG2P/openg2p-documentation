# Use a Keycloak client role in a rule

1. Open the policy version (draft) in the editor.
2. On the stage, click **+ Add rule**.
3. Set **rule type** to `role`.
4. In the **Role name** field, enter the role exactly as defined on the
   client (e.g. `PROGRAM_MANAGER`).
5. In the **Client** field, enter the `clientId` (e.g. `registry-staff-portal`).
   Leave blank for a realm role.
6. Save and activate.

AWE looks up the client by `clientId`, then queries that client's role
members. Make sure the AWE service account has `view-clients` and
`view-users` realm-management roles — see
[Deployment → Client-secret sync and service-account roles](../deployment.md#client-secret-sync-and-service-account-roles).

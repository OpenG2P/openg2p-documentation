# 📔 Configure WebSub Partner on Social Registry

### Keycloak Client Setup

* Create a Keycloak client for the Partner (who is trying to subscribe to events on SR) in the same realm containing SR client. Example client id: `openg2p-print-partner-abc`, client name: `ABC Print Partners` .
  * Client Authentication should be enabled.
  * Standard Flow disabled.
  * Implicit Flow disabled.
  * Direct access grants disabled.
  * Service Account Roles enabled.
* Assign the following realm roles under service account roles to the client, depending on what all events they want to subscribe to. `SUBSCRIBE_<event_name>_INDIVIDUAL` .
  * `SUBSCRIBE_WEBSUB_GROUP_CREATED_INDIVIDUAL`.
  * `SUBSCRIBE_WEBSUB_GROUP_UPDATED_INDIVIDUAL`.
  * `SUBSCRIBE_WEBSUB_INDIVIDUAL_CREATED_INDIVIDUAL`.
  * `SUBSCRIBE_WEBSUB_INDIVIDUAL_UPDATED_INDIVIDUAL`.

### Configure Partner in Social Registry

* TODO: elaborate
* Refer to [Datashare WebSub Config](../../../../developer-zone/odoo-modules/g2p-registry-datashare-websub.md#configuration).

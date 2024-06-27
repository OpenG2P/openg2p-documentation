---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Keycloak Client Creation

This guide contains instructions for creating and configuring an OIDC client on Keycloak.

## Procedure

The steps to create a Keycloak client are given below.

1. Log into Keycloak on the OpenG2P cluster.
2. Select the _**Clients**_ from the left menu and click _**Create Client**_ to create the required client.
3. Follow the below general settings while creating a client.
   * Client type**:** `OpenID Connect`
   * Client ID**:** `<any client Id>`  For example, openg2p-sr-odk-prod
   * Name: `<any name>` For example, Social Registry ODK Prod
   * Always display in UI: `On`
   * Client authentication: `On`
   * Authentication flow: Select the `Standard flow` and `Service accounts roles`
   * Valid redirect URIs:  `*`
4. Save the changes and click the _**Credentials**_ tab above. You must note down the client ID and secret to add while installing the OpenG2P modules.
5. Click the _**Client Scopes**_  tab.
6. Select the client that you created in the _**Client Scopes**._
7. Select the _**From Predefined Mappers**_ from the _**Add Mapper**_ drop-down.
8. In the _**Add Predefined Mapper**_ screen, check all the mappers below the _**Name**_ column, and click the _**Add**_ button.
9. After adding predefined mappers, search for the client from the filter, select _**client roles,**_ update, and save the below changes.
   * Client ID: `select your Client ID from the drop-down`
   * Token Claim Name:  `client_roles`
   * Add to ID token: `ON`
   * Add to userinfo: `ON`&#x20;
10. After the successful creation of the client, you can use this client for the OpenG2P module installation from the Rancher UI.

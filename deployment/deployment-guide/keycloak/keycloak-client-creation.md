---
description: Guide to create a Keycloak OIDC client for authentication in modules
---

# Keycloak Client Creation

For logging into various services of our modules, we use Keycloak as the OIDC auth provider. All users are configured on Keycloak.  We also need to configure "clients" on Keycloak for apps to connect to Keycloak. This guide provides the manual and automated mechanims to create a client with appropriate settings for our use.

## Manual procedure

The steps to create a Keycloak client are given below.

1. Log into Keycloak on the OpenG2P cluster.
2. Select a realm.  If the realm does not exist, create one.&#x20;
3. Select the _**Clients**_ from the left menu and click _**Create Client**_ to create the required client.
4. Follow the below general settings while creating a client.
   * Client typ&#x65;**:** `OpenID Connect`
   * Client I&#x44;**:** `<any client Id>`  For example, openg2p-sr-odk-prod
   * Name: `<any name>` For example, Social Registry ODK Prod
   * Always display in UI: `On`
   * Client authentication: `On`
   * Authentication flow: Select the `Standard flow` and `Service accounts roles`
   * Valid redirect URIs:  `*`
5. Save the changes and click the _**Credentials**_ tab above. You must note down the client ID and secret to add while installing the OpenG2P modules.
6. Click the _**Client Scopes**_ tab.
7. Select the client that you created in the _**Client Scopes**._
8. Select the _**From Predefined Mappers**_ from the _**Add Mapper**_ drop-down.
9. In the _**Add Predefined Mapper**_ screen, select to show all mappers on the same page. Check all the mappers below the _**Name**_ column, and click the _**Add**_ button.
10. Search and remove the "Audience Resolve" mapper from the added mappers list. Click on **Add Mapper** -> **By configuration** and select the **Audience** mapper in the **Configure new mapper** page. Configure the audience mapper with the following details.
    * Client ID: `select your Client ID from the drop-down`
    * Add to Access Token: `ON` .
    * Add to ID token: `ON` .
11. After adding predefined mappers, search for "client" in the filter, select _**Client Roles** mapper,_ update, and save the below changes.
    * Client ID: `select your Client ID from the drop-down`
    * Token Claim Name:  `client_roles`
    * Add to ID token: `ON`
    * Add to userinfo: `ON`&#x20;
12. Go one step back. Navigate to Client details -> Client Scopes. Remove "roles" scope.
13. After the successful creation of the client, you can use this client for the OpenG2P module installation from the Rancher UI.

## Automated&#x20;

Refer to [Keycloak Init Automation ](keycloak-init-automation.md)for details on Helm chart to create all the clients.




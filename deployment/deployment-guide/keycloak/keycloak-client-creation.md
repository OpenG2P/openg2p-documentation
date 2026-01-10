---
description: Guide to create a Keycloak OIDC client for authentication in modules
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Keycloak Client Creation

For logging into various services of our modules, we use Keycloak as the OIDC auth provider. All users are configured on Keycloak.  We also need to configure "clients" on Keycloak for apps to connect to Keycloak. This guide provides the manual and automated mechanims to create a client with appropriate settings for our use.

## Manual procedure

The steps to create a Keycloak client are given below.

1. Log into Keycloak on the OpenG2P cluster.
2. Select the _**Clients**_ from the left menu and click _**Create Client**_ to create the required client.
3. Follow the below general settings while creating a client.
   * Client typ&#x65;**:** `OpenID Connect`
   * Client I&#x44;**:** `<any client Id>`  For example, openg2p-sr-odk-prod
   * Name: `<any name>` For example, Social Registry ODK Prod
   * Always display in UI: `On`
   * Client authentication: `On`
   * Authentication flow: Select the `Standard flow` and `Service accounts roles`
   * Valid redirect URIs:  `*`
4. Save the changes and click the _**Credentials**_ tab above. You must note down the client ID and secret to add while installing the OpenG2P modules.
5. Click the _**Client Scopes**_ tab.
6. Select the client that you created in the _**Client Scopes**._
7. Select the _**From Predefined Mappers**_ from the _**Add Mapper**_ drop-down.
8. In the _**Add Predefined Mapper**_ screen, select to show all mappers on the same page. Check all the mappers below the _**Name**_ column, and click the _**Add**_ button.
9. Search and remove the "Audience Resolve" mapper from the added mappers list. Click on **Add Mapper** -> **By configuration** and select the **Audience** mapper in the **Configure new mapper** page. Configure the audience mapper with the following details.
   * Client ID: `select your Client ID from the drop-down`
   * Add to Access Token: `ON` .
   * Add to ID token: `ON` .
10. After adding predefined mappers, search for "client" in the filter, select _**Client Roles** mapper,_ update, and save the below changes.
    * Client ID: `select your Client ID from the drop-down`
    * Token Claim Name:  `client_roles`
    * Add to ID token: `ON`
    * Add to userinfo: `ON`&#x20;
11. Go one step back. Navigate to Client details -> Client Scopes. Remove "roles" scope.
12. After the successful creation of the client, you can use this client for the OpenG2P module installation from the Rancher UI.

## Helm chart

The Helm chart **keycloak-init** automates the above process and is extremely useful while creating clients in a bulk during environment setup. &#x20;

### Functionality

The Helm chart offers the following functionality:

* Creation of multiple clients
* Automatic generation of client secrets and storage of these as **Kubernetes secrets i**n your namespace.  The secrets can be securely read by the module Helm charts instead of passing them as parameters during installation.
* Idempotent:  If client already present, then running the Helm chart again does not change anything. Secrets are also untouched. &#x20;
* Client roles created as well
* A suffix with namespace is added to the name of all clients to distinguish from clients created for other namespaces
* Few default clients are already listed in [values.yaml](https://github.com/OpenG2P/keycloak-init/blob/develop/helm/values.yaml).&#x20;

### Source code

The script, Docker and Helm chart is available [here](https://github.com/OpenG2P/keycloak-init/tree/develop).

### Run

Run the Helm on the command line (Rancher verision is not yet available). Also, running on command line gives more flexibility to update values.yaml as required. &#x20;

_Note that the Helm chart needs to be installed on the cluster and namespace of interest (e.g. sandbox) as all client secrets are created in the same namespace. The cluster and namespace may. not be same as where Keycloak itself runs._

#### Prerequisites

A **client manager** user on Keycloak with limited permissions to run this Helm chart with following parameters:

* User name (example client-manager@openg2p.org)
* Password based credentials
* Roles for this user (limited to only these):
  * default-role-master
  * manage-clients
  * query-clients
  * view-client

#### Steps

* Clone [keycloak-init repo](https://github.com/OpenG2P/keycloak-init/tree/develop).
* Create a secret for the client manager **in installation namespace** with following params. You may create the same using Rancher instead of command line:
  * Type: `Opaque`
  * Secret name: `keycloak-client-manager`&#x20;
  * Key:  `keycloak-client-manager-password`
  * Value:  \<password of the client manager user> _(pick this from Keycloak)_
* Inspect `values.yaml` for list of clients. Update if required. Some clients may require client roles. Review them as well.  Carefully review and update the following parameters:

```
keycloak:
  # Internal service name on the cluster
  url: "https://keycloak2.openg2p.org"
  user: "client-manager@openg2p.org" 
  # Use secret instead of directly passing password here
  password: ""
  realm: "master"
  # If you want to use an existing secret for password
  existingSecret: "keycloak-client-manager" 
  existingSecretKey: "keycloak-client-manager-password"
```

* Run

```
$ helm -n <namespace> install keycloak-init .
```

* Verify the following
  * Clients have been created on Keycloak with client roles
  * Secrets of all the clients have been created in the namespace

### Tear down

* Uninstall the Helm chart

```
$ helm -n <namespace> uninstall kecyloak init
```

* The above **does not delete** clients on Keycloak or Kubernetes secrets. Delete them manually:
  * Kecloak clients (via Admin user interface of Keycloak)
  * Kubernetes secrets for all clients (via Rancher or command line)&#x20;

### Versions

| Helm Chart Version | Date Published | Contents                                                                       |
| ------------------ | -------------- | ------------------------------------------------------------------------------ |
| 0.0.0-develop      | Jan 2026       | Tested version.  After sufficient usage, this will be tagged to fixed version. |
|                    |                |                                                                                |
|                    |                |                                                                                |

### Developer

Build Docker:

```
cd docker
docker build -t openg2p/keycloak-init:develop .
docker push openg2p/keycloak-init:develop 
```

{% hint style="warning" %}
Make sure you build the Docker only on Ubuntu machine and not MacOS as there may be architecture mismtach issues.
{% endhint %}

TODO:

* Automate the Docker build and publish
* Automate Helm package and publish


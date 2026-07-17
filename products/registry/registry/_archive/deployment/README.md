---
description: Deploying OpenG2P Registry on Kubernetes using Helm charts.
---

# Deployment

{% hint style="warning" %}
**Archived.** The registry platform does not ship a Helm chart of its own — each registry builds and publishes its own self-sufficient chart. Deployment documentation now lives with the registry you are installing:

* [**Farmer Registry → Deployment**](../../../farmer-registry/deployment/README.md)

This page describes the retired `openg2p-registry` 4.x wrapper chart and is kept for historical reference only.
{% endhint %}

The Registry is deployed over Kubernetes infrastructure that offers **production-grade** deployment along with powerful security, access control and operational features. Learn more about the deployment architecture [here](../../../../../deployment/openg2p-deployment-model.md).

## Deployment steps

1. [Infrastructure setup](../../../../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../../../../operations/deployment/environment-setup-multi-node.md)
3. [Registry installation](./#registry-installation)&#x20;

## Registry installation

After the steps 1 and 2, since Rancher will be up and running it is recommend that deployment of Registry is done from Rancher UI.

### Prerequisites

1. Infastructure and environment is created as given above
2. You have full admin rights to the cluster and Rancher UI.

### Installation

1. Login to Rancher console
2. Select the cluster and namespace (environment)
3. Under Apps -> Repositories make sure the repository [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) is added
4. Under Apps->Charts refresh all repositories
5. Select "OpenG2P Registry" chart
6. Select the version (_3 digit versions denote frozen versions, while version with -develop tag are moving versions_).
7. On Install Step1
   1. select namespace
   2. give a name to the installation - 'registry' recommended
   3. select 'Customize Helm options before install'
   4. Next
8. Review all variables. Typically you will not need to change anything except for **ID Generator** where your ID types may be differen&#x74;**.**
9. Install
10. Wait for all pods to come up successfully

### Post install check

1. On browser open site 'registry.\<you domain>'.
2. This should open the Keycloak login page. Give 'admin' as user name and 'admin' as password
3. You will be prompted to change the password. Change to a strong password.
4. You should see the Registry home/landing/dashboard page.

# Keycloak Init Automation

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

Run the Helm on the command line or on Rancher. The below procedure is for command line. On Rancher the procedure is like any other chart. &#x20;

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

<table><thead><tr><th width="100">Helm Chart Version</th><th width="100">Date Published</th><th>Contents</th></tr></thead><tbody><tr><td>0.0.0-develop</td><td>Jan 2026</td><td>Tested version.  After sufficient usage, this will be tagged to fixed version. Compatible with Keycloak 24.0.5.</td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr></tbody></table>

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


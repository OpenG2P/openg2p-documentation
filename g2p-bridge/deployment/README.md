# Deployment

This guide explains how to deploy the G2P Bridge on a Kubernetes cluster. The
**entire subsystem installs from a single Helm chart**, `openg2p-bridge`, which
also creates the PostgreSQL database/role, a Redis, the Keycloak client and —
optionally — the bundled Example Bank simulator, all within the same namespace.

For the full description of the chart (features, contents, all parameters), see
[Helm Chart](helm-charts.md). Deployment can be done two ways:

* [Using the Rancher UI](#installation-using-rancher-ui)
* [Using the command line](#installation-using-cli)

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ **Kubernetes cluster** is up and running
* ✅ **Nginx server is configured** (skip this for OpenG2P-in-a-box)
* ✅ **Namespace is created** (via Rancher under a Project)
* ✅ **Project Owner access** on the OpenG2P namespace
* ✅ **Istio gateway** is set up in the namespace
* ✅ Shared **`commons-postgresql`** and **Keycloak** present in the namespace (commons layer)

## Installation using Rancher UI

1. Log in to the Rancher admin console and select your cluster.
2. Go to Apps → Repositories and click Create to add a new repository.
3. Enter "openg2p" as the Name and `https://openg2p.github.io/openg2p-helm/rancher` as the target HTTPS Index URL, then click Create.
4. Select the desired namespace for installation from the filter on the top-right.
5. To see prerelease (`develop`) versions, click your user avatar in the upper right corner and select **Include Prerelease Versions** under Preferences.
6. Navigate to Apps → Charts. **OpenG2P Bridge** will be listed.
7. Click the chart, choose the version, and click Install.
8. Provide a name for the installation (e.g. `g2p-bridge`), tick **Customize Helm options before install**, and click Next.
9. Fill the form (generated from `questions.yaml`):
   * Set the **namespace** segment — all hostnames are derived from it (e.g. `g2p-bridge.<namespace>.openg2p.org`). Override individual hostnames if needed.
   * Choose the **disbursement mode** (digital cash vs in-kind) and, for digital cash, the **sponsor/treasury account**.
   * Choose whether to deploy the bundled **Example Bank** and create the **Keycloak client**.
10. On the Helm Options page, disable the **wait** flag and click Install.
11. Monitor the pods until they all reach `Running` / `Completed` (may take a few minutes).

See [Helm Chart → Key parameters to change](helm-charts.md#key-parameters-to-change)
for the full list.

## Installation using CLI

1.  Clone the consolidated repository:

    ```bash
    git clone https://github.com/OpenG2P/g2p-bridge.git
    cd g2p-bridge/deployment/charts/openg2p-bridge
    ```
2.  Build Helm dependencies (common, postgres-init, redis, keycloak-init):

    ```bash
    helm dependency build
    ```
3.  Install the chart:

    ```bash
    helm install g2p-bridge . -n <namespace> --set global.namespace=<namespace>
    ```

    * Replace `g2p-bridge` with your desired release name. The Bridge **database
      and role are derived from the release name** — release `g2p-bridge` →
      database `g2p_bridge`, role `g2p_bridge_user`.
    * Replace `<namespace>` with your Kubernetes namespace.
    * Use `-f my-values.yaml` to provide custom configuration.
4.  Verify the deployment:

    ```bash
    helm status g2p-bridge -n <namespace>
    kubectl get pods,svc -n <namespace>
    ```
5.  Upgrade after changing values:

    ```bash
    helm upgrade g2p-bridge . -n <namespace> -f my-values.yaml
    ```

### Access links

With `global.namespace=trial` and the default hostnames:

* Partner API: `https://g2p-bridge.trial.openg2p.org/api/g2p-bridge` (Swagger at `/api/g2p-bridge/docs`, health at `/api/g2p-bridge/ping`)
* Bene-Portal API: `https://g2p-bridge-bene-portal.trial.openg2p.org/api/bene-portal`
* Example Bank API: `https://example-bank.trial.openg2p.org/api/example-bank`

{% hint style="info" %}
The bare API base path (e.g. `/api/g2p-bridge/`) returns a 404 by design — there
is no route there. Use `/docs`, `/ping`, or a specific endpoint.
{% endhint %}

### Database

The Bridge uses the shared **`commons-postgresql`** in the namespace; it does not
install its own PostgreSQL. `postgres-init` creates the Bridge database/role
(derived from the release name) and, when the Example Bank is enabled,
`example_bank_db` / `bankuser`.

## Teardown

`helm uninstall` leaves the Postgres database/role behind. To remove a release
completely, use the bundled uninstall script — see
[Teardown / Uninstall](teardown.md).

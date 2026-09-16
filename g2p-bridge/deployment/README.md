---
description: Deploying OpenG2P G2P Bridge on Kubernetes using Helm charts.
---

# Deployment

The G2P Bridge is deployed over Kubernetes infrastructure that offers **production-grade** deployment along with powerful security, access control and operational features. Learn more about the deployment architecture [here](../../deployment/openg2p-deployment-model.md).

Deployment is **largely automated**. Once the cluster and environment are in place, the entire G2P Bridge subsystem — APIs, Celery beat & workers, Redis, the PostgreSQL database/role, the Keycloak client and the optional bundled Example Bank — installs from a **single Helm chart** (`openg2p-bridge`) via the Rancher UI. No manual database, Keycloak or post-install configuration is required.

## Deployment steps

1. [Infrastructure setup](../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../operations/deployment/environment-setup-multi-node.md)
3. [G2P Bridge installation](./#g2p-bridge-installation)

## G2P Bridge installation

After steps 1 and 2, Rancher is up and running, so it is recommended to deploy the G2P Bridge from the **Rancher UI**.

### Prerequisites

1. Infrastructure and environment are created as given above. The **commons** environment provides the shared services the Bridge depends on — **PostgreSQL** and the **Istio** gateway. The Bridge verifies and signs partner requests **in-process**, so it needs **no runtime key service**.
2. You have full admin rights to the cluster and the Rancher UI.

### Installation

1. Login to the Rancher console.
2. Select the cluster and namespace (environment).
3. Under **Apps → Repositories**, make sure the OpenG2P charts Helm repository is added: `https://openg2p.github.io/openg2p-helm`.
4. In Rancher, to display prerelease versions of OpenG2P apps, under your user avatar in upper right corner of the Rancher dashboard enable **Preferences-> Helm Charts-> Include Prerelease Versions.**
5. Under **Apps → Charts**, refresh all repositories.
6. Select the **"OpenG2P Bridge"** chart.
7. Select the version (_3-digit versions denote frozen releases; versions with a `-develop` tag are moving versions_).
8. On Install Step 1:
   1. select the namespace;
   2. give the installation a name — `g2p-bridge` recommended (the database and role are derived from this name);
   3. select **Customize Helm options before install** — needed so you can review the chart options, including the **sanity test suite** (see the note below);&#x20;
   4. Next.

{% hint style="info" %}
**Sanity test suite.** The bundled regression sanity suite is **enabled by default** — it runs the read-only **L0 (smoke)** and **L1 (contract)** API checks on each install/upgrade and creates no data. Enable **L2 (end-to-end)** only on **test environments**, as it creates test data and moves treasury funds. See [Regression Sanity Suite](../development/testing/regression-sanity-suite.md) for what each level covers and how to read the report.
{% endhint %}

9. Review the variables. For a pure **digital cash** deployment you typically only set the **sponsor/treasury account** and choose whether to deploy the bundled **Example Bank** and create the **Keycloak client** — all hostnames are derived automatically from the install namespace. See [Helm Chart → Key parameters to change](helm-charts.md#key-parameters-to-change) for the full list.
10. Install.
11. Wait for all pods to come up successfully (`Running` / `Completed`).

### Post install check

With the default hostnames (namespace `trial` shown):

1. Open `https://g2p-bridge.<namespace>.openg2p.org/api/g2p-bridge/ping` — it should return a healthy response.
2. Open `https://g2p-bridge.<namespace>.openg2p.org/api/g2p-bridge/docs` — the Partner API Swagger UI should load.
3.  If the Example Bank was deployed, confirm the treasury account was seeded:

    ```bash
    curl -s -X POST \
      https://example-bank.<namespace>.openg2p.org/api/example-bank/check_funds \
      -H 'Content-Type: application/json' \
      -d '{"account_number":"SPONSOR0001","account_currency":"USD","total_funds_needed":100}'
    ```

    A response with `"has_sufficient_funds": true` confirms the install is working end to end.

{% hint style="info" %}
The bare API base path (e.g. `/api/g2p-bridge/`) returns a 404 by design — there is no route there. Use `/docs`, `/ping`, or a specific endpoint.
{% endhint %}

### Next steps

With the install healthy, finish the rollout in two short steps. Each is a
self-contained guide — follow the linked page (kept separate so this flow stays
simple):

1. **Load the monitoring dashboards.** Upload the bundled Superset dashboards
   (Operations Overview, Failures, Reconciliation, SPAR, Example Bank) so
   operators can watch disbursements, failures and reconciliation, then open them
   to confirm they render. → [**Dashboards (Superset)**](dashboards.md)
2. **Try out the APIs.** Run the guided, CSV-seeded **API Walkthrough** against
   this install to exercise the full digital-cash disbursement flow end to end and
   see the results — it also doubles as hands-on training.
   → [**API Walkthrough (Postman)**](../development/testing/api-walkthrough.md)

## Reference

* [Helm Chart](helm-charts.md) — what the chart contains, all parameters, and the command-line install option (for advanced / developer use).
* [Keycloak Client](keycloak-client.md) — why the OIDC client is required.
* [Example Bank & Treasury Account](deployment-of-example-bank.md) — the bundled simulator and digital-cash treasury configuration.
* [Domain Names and Certificates](domain-names-and-certificates.md)
* [Teardown / Uninstall](teardown.md) — completely remove a release.

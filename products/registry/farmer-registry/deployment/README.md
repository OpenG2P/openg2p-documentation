---
description: >-
  Installing the Farmer Registry: prerequisites, order, the choices to make in
  the Rancher form, and checks after install.
---

# Deployment

This page lists the steps and choices. What the Farmer Registry is and what its chart adds: [Farmer Registry](../README.md). How domain registries are packaged: [Packaging & the reference registry](../../registry/deployment-and-extension/packaging-and-reference-registry.md#domain-registry-charts).

## Order

1. [Infrastructure setup](../../../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../../../operations/deployment/environment-setup-multi-node.md)
3. **commons-base**, then **commons-services**, in the namespace ([Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md))
4. The Farmer Registry (below)

## Prerequisites

1. Admin rights to the cluster and to Rancher.
2. commons-base and commons-services installed and healthy in the namespace. The registry bundles none of the shared services. From commons-services it uses:

   | Service | Needed for | Setting in the commons-services form |
   | --- | --- | --- |
   | **Master Data** | Coded fields, the geography, sample farmers | **Dataset Themes** includes `agriculture` (the default), **Load Datasets** on. For a demo, also **Load Sample People** on |
   | **AWE** | Change requests. The db-seed Job waits for it | **Install AWE?** on |
   | **Partner Management** and **Consent Manager** | Partner calls: signature checks and consent | On (defaults) |
   | **eSignet**, **Inji Certify**, **Inji Verify** | [Farmer credentials](../README.md#farmer-credentials), which are on in this chart | On. Set **Agent Portal Hostname** to the registry's agent portal host, `<release>-agent.<Base Domain>` ([why](../../registry/features/agent-portal.md#signing-out)) |
   | **Superset** | Dashboards. Optional: without it the dashboard import is skipped | **Install Superset?** on, if dashboards are wanted |

3. The OpenG2P catalogue added in Rancher (**Apps → Repositories**).

{% hint style="warning" %}
The db-seed Job waits for AWE. If AWE is down, db-seed blocks, the install times out, and the later Jobs are never created. Check commons-services first.
{% endhint %}

## Install

### Using Rancher

1. Select the cluster and the namespace.
2. Under **Apps → Charts**, refresh the repositories and select **OpenG2P Farmer Registry**.
3. Choose the version. Three-digit versions are frozen. Tick **Show pre-release versions** to see moving `0.0.0-develop.N` versions.
4. Name the release, e.g. `fr`. The release name is part of the hostnames and the database name, so several registries can share a namespace.
5. Tick **Customize Helm options before install**, then **Next**.
6. Make the choices below, then **Install**.

The form is the platform chart's form plus an **Analytics** group. Each field is described in the form.

### Choices

The defaults suit a production-like install. Change only these.

| Field | Choose | Why |
| --- | --- | --- |
| **Base Domain** | Your environment's domain | Every hostname derives from it. Default `<namespace>.openg2p.org` |
| **Load Sample Data** (+ **Load Sample Images**) | On for a demo only | Sample farmers from Master Data's sample people ([data seeding](data-seeding.md#sample-data)) |
| **Generate bulk demo data** | On for a dashboards or load-test demo only | 100,000 invented farmers ([data seeding](data-seeding.md#bulk-data)) |
| **Sanity - Run Full E2E** | Off, except on a test environment | It leaves test data behind ([sanity testing](sanity-testing.md)) |
| **Verifiable Credentials (Agent Portal)** | Off if farmer credentials are not issued, or eSignet and Inji Certify are not installed | On in this chart |
| **AWE Approver User Password** | Your own | The initial password of the demo change-request approvers |

{% hint style="warning" %}
**Verify Partner Signature** and **Enforce Consent** are on by default. Turning either off returns data to partners unchecked or not cut down to their consent ([Consent-aware data sharing](../../registry/features/consent-aware-data-sharing.md#configuration)).
{% endhint %}

### Settings only in YAML

Set these in **Edit YAML**, if at all. In a values file, platform settings sit under `registry.*` and shared settings under `global.*`.

| Key | Default | Set it when |
| --- | --- | --- |
| `analytics.bulkSample.expectedCountry` | empty | You want bulk generation to fail if Master Data holds another country (e.g. `ETH`) |
| `analytics.dashboards.superset.required` | `false` | The dashboards must load: the install then fails if Superset is not reachable |
| `global.consentDataController` | `farmer-registry` | Partners are bound in the Consent Manager under another controller ID. It changes every scope ID |

### Using the Helm CLI

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm install fr openg2p/openg2p-farmer-registry \
  --namespace <namespace> --version <chart-version> -f values.yaml
```

Add `--devel` to install a `0.0.0-develop.N` version.

## Post-install check

1. Check the Jobs completed: `kubectl -n <namespace> get jobs`. The install runs them in a fixed order; Helm stops at the first failure, so a missing Job means an **earlier** one failed. Order and names: [Install sequence](data-seeding.md#install-sequence).
2. Read the sanity Job's log: `kubectl -n <namespace> logs job/<release>-sanity` ([sanity testing](sanity-testing.md)).
3. Open `https://<release>.<Base Domain>`. You should get the Keycloak login page.
4. Log in with the credentials set up by `keycloak-init`, and change the password when asked.
5. With credentials on, open the agent portal at `https://<release>-agent.<Base Domain>`.

## Before going to production

* Keep **Verify Partner Signature** and **Enforce Consent** on.
* Keep sample data, sample images, bulk data and the full e2e off ([An empty install](../../registry/deployment-and-extension/country-data-and-seeding.md#an-empty-install-for-production)). On commons-services, turn **Load Sample People** off.
* Replace the demo change-request approvers (`alex.carter`, `nina.patel`, in the extension's `awe_meta_data/30_approver_rule.sql`) with your officials.
* Never promote a demo namespace to production. Install fresh.

## Uninstall

`helm uninstall` leaves the database, PVCs, IAM rows and the Superset dashboards behind. Use the repository's script, with `--dry-run` first:

```bash
./scripts/uninstall-registry.sh --namespace <namespace> --release fr --dry-run
./scripts/uninstall-registry.sh --namespace <namespace> --release fr
```

Options include `--keep-iam`, `--keep-dashboards`, `--keep-pvs`, `--force` and `--yes`. It leaves the sanity test partner in Partner Management and the Consent Manager; remove those there if needed.

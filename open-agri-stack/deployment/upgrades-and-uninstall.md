---
description: >-
  Upgrading Agri Stack's charts and images, rotating the signing keys, and
  uninstalling the Composite and the registries with their scripts.
---

# Upgrades and Uninstall

## Upgrading

Each install is upgraded on its own, in Rancher (**Apps → Installed Apps → ⋮ → Edit/Upgrade**): pick the new chart version, keep the values, **Upgrade**. The Exchange and each department can upgrade on their own schedules. There is no upgrade script and no Agri Stack-wide version yet.

| Install | On upgrade | Notes |
| --- | --- | --- |
| Commons Base, Commons Services | Each component's own Jobs and sanity checks run again | [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md); the CM's sanity suite runs on every upgrade ([CM deployment](../../consent-management/deployment/README.md#sanity-tests-in-cluster)) |
| Farmer Registry | The db-seed and sanity hook Jobs run again | [Data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md#install-sequence) |
| Crop Sown Registry | The seed runs again (idempotent); activity types, indicators and the ODK mapping are updated in place | [Crop Sown Registry → Deployment](../../products/registry/crop-sown-registry/deployment/README.md); [upgrading an early install](../../products/registry/crop-sown-registry/versions/README.md#upgrading-an-early-install) |
| Composite | The console's database Job (idempotent), its IAM registration and the sanity hook run again | Below |

**Composite.**

* **Image versions:** **Image Tag** and **Console UI Image Tag**. The chart's default `develop` moves (pulled on every pod start); pin a released version in production.
* **Use cases:** a change to `composite.useCases` (or your own ConfigMap) is picked up by running pods within the reload interval, without a restart or a chart upgrade.
* **Registries and other settings** are environment variables: changing them rolls the pods.
* **After a use case with new data scopes or purposes,** rerun the [Exchange setup](after-install.md#exchange-setup) so each department's scope policy for the Composite (in its PM) covers it.

After any upgrade, check the Composite, the CMs and the registries' partner APIs together: run the [partner test](testing.md#partner-test-public-apis).

### Rotating keys

| Key | How |
| --- | --- |
| Exchange CM signing key | New Secret with the new `.p12`, then a new **Signing Key ID** in Commons Services. The departments read its public keys from the Exchange CM's JWKS URL, not from their own settings |
| Composite signing key | `python scripts/setup_exchange.py … --new-key`: a new key (new `kid`), registered in each PM with a key-update request, and the Secret replaced |
| A partner's key | The partner raises a key-update request in PM ([partner guide](../partner-guide.md#step-2-get-onboarded-in-partner-management)) |

## Uninstalling

`helm uninstall` leaves databases, IAM rows and some Secrets behind. Use each product's script, with `--dry-run` first.

| What | Script | Notes |
| --- | --- | --- |
| Composite | [`scripts/uninstall-agri-composite.sh`](https://github.com/openg2p/agri-stack/blob/develop/scripts/uninstall-agri-composite.sh) `--namespace <ns> [--release agri-composite] [--keep-db] [--keep-iam] [--drop-signing-secret] [--force] [--dry-run] [--yes]` | Removes the release, leftover Jobs, and the ConfigMaps and Secrets labelled with the release; drops the console's database `agri_composite` and its role in `commons-postgresql` (unless `--keep-db`) and deletes the console's IAM rows (unless `--keep-iam`); the signing Secret only with `--drop-signing-secret`. Other options: `--console-db`, `--console-db-user`, `--console-mnemonic`, `--iam-db`, `--postgres-release`, `--postgres-namespace`, `--signing-secret`. `--force` runs while a Helm operation is in progress. Leaves the console's Keycloak client. No PVCs |
| Crop Sown Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/crop-sown-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> [--release csr] [--keep-iam] [--keep-pvs] [--dry-run] [--yes]` | Also drops the registry's database and role in `commons-postgresql`, its IAM rows, PVCs and their PVs ([Uninstall](../../products/registry/crop-sown-registry/deployment/rancher.md#uninstall)) |
| Farmer Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/farmer-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> --release fr [--keep-iam] [--keep-dashboards] [--dry-run] [--yes]` | As above, and first removes the registry's Superset dashboards (its default release name is `registry`, so give `--release fr`) |
| Commons | `helm uninstall` of `commons-services`, then `commons` | [Commons Helm chart: tear down](../../deployment/openg2p-commons-helm-chart.md#tear-down) |

None of the scripts touches Partner Management or the Consent Manager. The partners, their keys and their policies stay in Partner Management: in the Exchange, the Composite and the partners with their use-case policies; in each department, the Composite with its key and scope policies. If needed, disable the partners or revoke their policies there with a policy request ([access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies)).

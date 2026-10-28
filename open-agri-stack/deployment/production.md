---
description: >-
  What a production Agri Stack install changes from the demo defaults: the
  Exchange's form fields and keys, the Composite's settings, approvals,
  internal services, and demo leftovers to remove.
---

# Production

A demo install can keep the defaults; a production install changes the items below. The registries' own production settings are in their guides ([Farmer Registry](../../products/registry/farmer-registry/deployment/README.md#before-going-to-production), [Crop Sown Registry](../../products/registry/crop-sown-registry/deployment/rancher.md#production)).

## Exchange Consent Manager signing key

The demo key is public: anyone could sign consent tokens the departments accept. Create the Secret before installing Commons Services:

```bash
kubectl -n agrix create secret generic agrix-cm-signing \
  --from-file=cm_signing.p12=./cm_signing.p12 --from-literal=password='<p12 password>'
```

## Exchange: Commons Services

| Field | Value | Why |
| --- | --- | --- |
| Base Domain (both commons charts) | The Exchange's domain | The departments find the Exchange CM at `agrix.<parent domain>`; with another name, each department sets **Exchange Domain** |
| Signing Key (Consent Manager) | **existing** | Use your own key |
| Signing Key Secret | `agrix-cm-signing` | The Secret above |
| Signing Key ID | e.g. `agrix-cm-2026-01` | Stamped on each consent token; change it when the key is rotated |
| Install Mock Identity System? | **No** | eSignet connected to the real national ID system |
| Load Sample People | **Off** | |

Step by step: [replacing the demo key](../../consent-management/deployment/README.md#replacing-the-demo-key-for-production-rancher-step-by-step).

## Composite

| Field | Value | Why |
| --- | --- | --- |
| Base Domain | The same as the Exchange's commons | Every hostname sits under it |
| Image Tag, Console UI Image Tag | A released version | `develop` images move |
| Composite Hostname, Console Hostname | Under the Exchange domain | Partners call the Composite there |
| Allowed Browser Origins (CORS) | `https://<partner portal hostname>` | The partner portal reads the use-case list |
| Enable Autoscaling, Min/Max Replicas | On, sized to the load | |
| Edge Rate Limit, Edge Limit (Requests) | On, above the expected peak of all partners together | Needs rights in `istio-system` ([chart settings](../composite/chart-settings.md#scaling-and-rate-limits)) |

## The Composite's key

* **Custody.** Generate it where your organisation generates keys; keep the `.p12` and its password in its secrets store. Set it up [by hand](after-install.md#by-hand), or run the script with `--state-dir` on protected storage and remove the local copy afterwards.
* **Access.** Only the Composite and its operators may read the Secret `agri-composite-signing`.
* **Rotation and compromise:** [Upgrades: rotating keys](upgrades-and-uninstall.md#rotating-keys).

## Approvals

* **Separate the roles.** Partner Management lets the person who raises a request approve it. Have one person raise and another approve every onboarding, key and policy request, at the Exchange and in each department.
* **Departments own their scope policies for the Composite.** The Exchange operator should not hold Partner Management admin rights in a department.
* **Review widenings** of those policies before approving them.

## Services that stay internal

Partner Management's partner API and the CMs' partner APIs have no login: check that no public route exposes them (the charts put them on the internal gateway). The Composite's API is the only public entry for partners.

## Remove demo leftovers

* Test partners in the Exchange PM (e.g. `PARTNER_BANK_A`): disable them, and remove their partner-portal users.
* The registries' sanity partner `PARTNER_CM_SANITY`, if the sanity tests ran.
* Sample data in the registries.
* Local test keys (`~/.agri-partner-test/`, `~/.agri-stack-setup/`).

## Keep

* The Audit Manager on in every install.
* Backups of each Partner Management and Consent Manager database: partners, keys, policies and consents live there.

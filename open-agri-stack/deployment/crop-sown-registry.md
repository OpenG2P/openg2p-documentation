---
description: >-
  Installing the Crop Sown Registry for Agri Stack: its own deployment guide,
  plus the Consent Manager in the department role, the Composite's search URL,
  the Exchange setup and a check.
---

# Crop Sown Registry

Install the Crop Sown Registry by its own guide: [Crop Sown Registry → Deployment](../../products/registry/crop-sown-registry/deployment/README.md) and [Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md), including its checks and [production](../../products/registry/crop-sown-registry/deployment/rancher.md#production) settings. These pages install it in the namespace `dept1`, in the Crops Department's cluster ([topology](README.md#topology)). This page lists only what Agri Stack needs on top. Its role in Agri Stack: [Registries in Agri Stack](../architecture/registries.md#crop-sown-registry).

## Choices for Agri Stack

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM accepts the Exchange's consent tokens, presented by the Composite |
| Commons Services | Exchange Domain (Consent Manager) | Empty, unless the Exchange is not at `agrix.<parent domain>` | The CM reads the Exchange CM's public keys there. On a separate cluster it usually is not ([Separate Clusters](separate-clusters.md)) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) | Consents are collected at the Exchange |
| Crop Sown Registry | Release name | Any; these pages use `csr` | The Composite's **Crop Sown Registry Search URL** is then `https://partner-csr.<domain>/dci/registry/sync/search` ([Composite](composite.md)). The chart has no default for it |
| Crop Sown Registry | Load Sample Data, Load sample crop seasons | **On**, for a demo only | Crop seasons for the Farmer Registry's sample farmers ([sample data](../architecture/registries.md#sample-data)) |

## After install

Run the [Exchange setup](after-install.md#exchange-setup) with `--registry crop-sown-registry=dept1`, once the Composite is installed. It registers the Composite in this namespace's Partner Management and gives it a binding and standing policy in this CM ([the Composite as a partner](../architecture/registries.md#the-composite-as-a-partner)). The script reaches only namespaces in the Exchange's cluster; on a separate cluster, do it by hand: [Separate Clusters](separate-clusters.md#the-composite-in-a-department-on-another-cluster).

## Check

From the [agri-stack](https://github.com/openg2p/agri-stack) repository, once the Composite and the Exchange setup are in place:

```bash
./scripts/exchange_test.sh --namespace agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

The `loan-profile` response has the `season_summaries` and `crop_seasons` sources `ok`. Details and common failures: [Testing](testing.md).

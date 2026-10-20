---
description: >-
  Installing the Farmer Registry for Agri Stack: its own deployment guide, plus
  the Consent Manager in the department role, the Composite's search URL, the
  Exchange setup and a check.
---

# Farmer Registry

Install the Farmer Registry by its own guide: [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md), including its checks and [before going to production](../../products/registry/farmer-registry/deployment/README.md#before-going-to-production). These pages install it in the namespace `trial` ([topology](README.md#topology)). This page lists only what Agri Stack needs on top. Its role in Agri Stack: [Registries in Agri Stack](../architecture/registries.md#farmer-registry).

## Choices for Agri Stack

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM accepts the Exchange's consent tokens, presented by the Composite |
| Commons Services | Exchange Domain (Consent Manager) | Empty, unless the Exchange is not at `agrix.<parent domain>` | The CM reads the Exchange CM's public keys there (e.g. `agrix.openg2p.org` for `trial.openg2p.org`) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) | Consents are collected at the Exchange |
| Farmer Registry | Release name | Any; these pages use `fr` | The Composite's **Farmer Registry Search URL** is then `https://partner-fr.<domain>/dci/registry/sync/search` ([Composite](composite.md)). The chart has no default for it |
| Farmer Registry | Load Sample Data | **On**, for a demo only | Farmers matching the Crop Sown Registry's samples ([sample data](../architecture/registries.md#sample-data)) |

## After install

Run the [Exchange setup](after-install.md#exchange-setup) with `--registry farmer-registry=trial`, once the Composite is installed. It registers the Composite in this namespace's Partner Management and gives it a binding and standing policy in this CM ([the Composite as a partner](../architecture/registries.md#the-composite-as-a-partner)). If this CM does not trust the Exchange's consent tokens, it stops and names the form field.

## Check

From the [agri-stack](https://github.com/openg2p/agri-stack) repository, once the Composite and the Exchange setup are in place:

```bash
./scripts/exchange_test.sh --namespace agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

The `loan-profile` response has the `farmer` source `ok`. Details and common failures: [Testing](testing.md).

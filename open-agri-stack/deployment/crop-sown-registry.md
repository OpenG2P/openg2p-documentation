---
description: >-
  Installing the Crop Sown Registry for Agri Stack: its own install guide, and
  the form fields Agri Stack needs on top.
---

# Crop Sown Registry

Step 1 of the [install order](README.md#install-order), in the namespace `dept1`.

## Install

Follow the Crop Sown Registry's own guide: [Crop Sown Registry → Deployment](../../products/registry/crop-sown-registry/deployment/README.md) and [Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md). It installs Commons Base, Commons Services and the Crop Sown Registry. Change these fields on top:

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM accepts the Exchange's consent tokens, presented by the Composite |
| Commons Services | Exchange Domain (Consent Manager) | Empty, unless the Exchange is not at `agrix.<parent domain>` | Where the CM reads the Exchange CM's public keys. On a separate cluster it usually is not ([Separate Clusters](separate-clusters.md)) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) | Consents are collected at the Exchange |
| Crop Sown Registry | Release name | e.g. `csr` | Sets the registry's partner hostname, `partner-csr.<domain>` |
| Crop Sown Registry | Load Sample Data, Load sample crop seasons | **On** for a demo only | Crop seasons for the Farmer Registry's sample farmers ([sample data](../architecture/registries.md#sample-data)) |

## Check

The registry's own checks pass ([Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md)), and note its partner search URL:

```
https://partner-csr.dept1.openg2p.org/dci/registry/sync/search
```

It is the Composite's **Crop Sown Registry Search URL** in the [Exchange](exchange.md#composite) install.

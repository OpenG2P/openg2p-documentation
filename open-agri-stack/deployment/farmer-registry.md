---
description: >-
  Installing the Farmer Registry for Agri Stack: its own install guide, and the
  form fields Agri Stack needs on top.
---

# Farmer Registry

Step 1 of the [install order](README.md#install-order), in the namespace `trial`.

## Install

Follow the Farmer Registry's own guide: [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md). It installs Commons Base, Commons Services and the Farmer Registry. Change these fields on top:

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM accepts the Exchange's consent tokens, presented by the Composite |
| Commons Services | Exchange Domain (Consent Manager) | Empty, unless the Exchange is not at `agrix.<parent domain>` | Where the CM reads the Exchange CM's public keys (e.g. `agrix.openg2p.org` for `trial.openg2p.org`) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) | Consents are collected at the Exchange |
| Farmer Registry | Release name | e.g. `fr` | Sets the registry's partner hostname, `partner-fr.<domain>` |
| Farmer Registry | Load Sample Data | **On** for a demo only | Farmers matching the Crop Sown Registry's samples ([sample data](../architecture/registries.md#sample-data)) |

## Check

The registry's own checks pass ([Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md)), and note its partner search URL:

```
https://partner-fr.trial.openg2p.org/dci/registry/sync/search
```

It is the Composite's **Farmer Registry Search URL** in the [Exchange](exchange.md#composite) install.

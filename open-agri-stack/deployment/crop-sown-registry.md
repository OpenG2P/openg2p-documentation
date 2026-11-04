---
description: Installing the Crop Sown Registry.
---

# Crop Sown Registry

Step 1 of the [install steps](README.md#install-steps), in the namespace `dept1`.

## Install

Follow the Crop Sown Registry's own guide: [Crop Sown Registry → Deployment](../../products/registry/crop-sown-registry/deployment/README.md) and [Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md). It installs Commons Base, Commons Services and the Crop Sown Registry. Set these fields on top:

| Chart | Field | Value |
| --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** |
| Commons Services | Exchange Domain (Consent Manager) | Empty when the Exchange is at `agrix.<parent domain>`; otherwise its domain ([Separate Clusters](separate-clusters.md)) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) |
| Commons Services | Country Pack | The same as every other install (default `ETH`) |
| Crop Sown Registry | Release name | e.g. `csr` (gives the hostname `partner-csr.<domain>`) |
| Crop Sown Registry | Load Sample Data, Load sample crop seasons | **On** for a demo only ([sample data](testing.md#sample-data)) |

## Check

1. The registry's own checks pass ([Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md)).
2. Note its partner search URL, for the [Composite](exchange.md#composite): `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search`.
3. Once the Exchange is installed, Partner Management serves the Composite's key:

   ```bash
   curl -s https://partner-management-partner-api.dept1.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
   ```

   If not: as for the [Farmer Registry](farmer-registry.md#check).

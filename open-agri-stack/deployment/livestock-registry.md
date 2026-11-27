---
description: Installing the Livestock Registry.
---

# Livestock Registry

Step 1 of the [install steps](README.md#install-steps), in the namespace `dept1`, beside the Crop Sown Registry. Optional: without it, the `loan-profile` use case answers without the farmer's animals (its `livestock` source is optional).

## Install

Follow the Livestock Registry's own guide: [Livestock Registry → Deployment](../registries/livestock-registry/deployment/README.md) and [Deploying on Rancher](../registries/livestock-registry/deployment/rancher.md). In `dept1`, Commons Base and Commons Services are already installed for the Crop Sown Registry ([Crop Sown Registry](crop-sown-registry.md)), with the fields set there; check that Commons Services also has **Install AWE?** on and the `agriculture` domain loaded in Master Data ([Prerequisites](../registries/livestock-registry/deployment/rancher.md#prerequisites)). Set these fields on top:

| Chart | Field | Value |
| --- | --- | --- |
| Livestock Registry | Release name | e.g. `lsr` (gives the hostname `lsr-partner-api.<domain>`) |
| Livestock Registry | Load Sample Data, Load sample events | **On** for a demo only ([Sample Data](sample-data.md)) |

In its own namespace instead, install Commons Base and Commons Services first, with the Commons Services fields of the [Crop Sown Registry](crop-sown-registry.md#install) (**Exchange Role** `department`, the same country pack, **Load Sample People** on for a demo).

## Check

1. The registry's own checks pass ([Verify](../registries/livestock-registry/deployment/rancher.md#verify)).
2. Note its partner search URL, for the [Composite](exchange.md#composite): `https://lsr-partner-api.dept1.openg2p.org/dci/registry/sync/search`.
3. Once the Exchange is installed, Partner Management serves the Composite's key:

   ```bash
   curl -s https://partner-management-partner-api.dept1.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
   ```

   If not: as for the [Farmer Registry](farmer-registry.md#check).
4. Step 3 of the install steps adds the Composite's scope policy for `livestock-registry` in `dept1`'s Partner Management, beside the Crop Sown Registry's ([Releasing Registry Data to the Composite](../administration/releasing-data-to-the-composite.md)). Until then the `livestock` source answers `denied`, and the rest of the loan profile is unaffected.

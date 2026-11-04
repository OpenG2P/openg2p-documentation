---
description: Installing the Farmer Registry.
---

# Farmer Registry

Step 1 of the [install steps](README.md#install-steps), in the namespace `trial`.

## Install

Follow the Farmer Registry's own guide: [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md). It installs Commons Base, Commons Services and the Farmer Registry. Set these fields on top:

| Chart | Field | Value |
| --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** |
| Commons Services | Exchange Domain (Consent Manager) | Empty when the Exchange is at `agrix.<parent domain>`; otherwise its domain |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) |
| Commons Services | Country Pack | The same as every other install (default `ETH`) |
| Farmer Registry | Release name | e.g. `fr` (gives the hostname `partner-fr.<domain>`) |
| Farmer Registry | Load Sample Data | **On** for a demo only ([sample data](testing.md#sample-data)) |

## Check

1. The registry's own checks pass ([Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md)).
2. Note its partner search URL, for the [Composite](exchange.md#composite): `https://partner-fr.trial.openg2p.org/dci/registry/sync/search`.
3. Once the Exchange is installed, Partner Management serves the Composite's key:

   ```bash
   curl -s https://partner-management-partner-api.trial.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
   ```

   If not: **Exchange Role** is not `department`, or Partner Management cannot reach `https://agri-composite.<Exchange domain>/.well-known/jwks.json` (set **Exchange Domain**, or **Composite JWKS URL**); the PM staff API log ("Bootstrap").

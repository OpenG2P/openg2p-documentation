---
description: >-
  What each Agri Stack install is configured with: the Farmer Registry, the
  Crop Sown Registry, the Exchange and the Composite.
---

# Configuration

Agri Stack is built from OpenG2P products: the [registry platform](../../products/registry/registry/README.md) and the registries on it, [Partner Management](../../platform/platform-services/partner-management/README.md), the [Consent Manager](../../consent-management/README.md) and the Composite. Each product is documented once, in its own pages. These pages say only what is configured in each install for Agri Stack.

How to install them is in [deploying on a cluster](../guides/deployment.md). What is still open is in [TODOs and open items](../open-items/README.md).

## Overview

| Install | Product | Configured for Agri Stack | Page |
| --- | --- | --- | --- |
| **Farmer Registry** (department, e.g. `trial`) | [Farmer Registry](../../products/registry/farmer-registry/README.md) | Consent controller `farmer-registry`; Farmer ID and national ID in the DCI farmer record; the data scopes the Composite reads; the Composite as a partner; CM role **department** with a standing policy for the Composite | [Farmer Registry](farmer-registry.md) |
| **Crop Sown Registry** (department, e.g. `dept1`) | [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) | Consent controller `crop-sown-registry`; farmer ID linked to the national ID for consent checks; the data scopes the Composite reads; the Composite as a partner; CM role **department** with a standing policy for the Composite | [Crop Sown Registry](crop-sown-registry.md) |
| **Exchange** (`agrix`) | Commons services: Partner Management, Consent Manager, eSignet | CM role **exchange** (issues a consent token per registry to the Composite); the partner portal with national-ID login and `FARMER_ID`; partners, their bindings and policies | [Exchange](exchange.md) |
| **Composite** (in the Exchange) | Composite ([agri-stack](https://github.com/openg2p/agri-stack)) | Consent mode `exchange`; the two registries' search URLs; the `loan-profile` use case; audit to the Audit Manager | [Composite](composite.md) |

## Names used across installs

The installs only work together if these names match. The defaults match everywhere, so a default install needs none of them set.

| Name | Value | Used by |
| --- | --- | --- |
| Composite partner ID | `agri-composite` | The Composite (`global.compositePartnerId`); its PM entry `PARTNER_AGRI_COMPOSITE` in every PM; the audience of its bindings in the department CMs; the token presenter at the Exchange CM; the trusted presenter at the department CMs |
| Consent-token issuer | `agri-stack-exchange-cm` | The Exchange CM (issuer); the department CMs (trusted issuer) |
| Data controllers | `farmer-registry`, `crop-sown-registry` | Each registry (its variant); the grants in a consent; the Composite's `registries`; the bindings at each CM |
| Subject ID types | `FAYDA_FAN`, `FARMER_ID` | The use case's input; the CM policies |
| Exchange domain | `agrix.<parent domain>` | The department CMs find the Exchange CM's public keys there |

## Repositories

| Repository | What |
| --- | --- |
| [OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform) | The registry platform, including activity registers |
| [OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) | The Farmer Registry extension and chart |
| [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) | The Crop Sown Registry extension and chart |
| [OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager) | The Consent Manager |
| [openg2p/agri-stack](https://github.com/openg2p/agri-stack) | The Composite (`composite/`) and the scripts (`scripts/`) |

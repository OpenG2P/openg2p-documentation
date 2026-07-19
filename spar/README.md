---
description: Social Payments Account Registry
cover: ../.gitbook/assets/SPAR banner-on-light-background.png
coverY: 0
---

# SPAR

The Social Payments Account Registry (SPAR) is an extension of the ID Account Mapper that maintains a mapping of a user ID and [Financial Address](https://docs.cdpi.dev/technical-notes/digital-payment-networks/financial-address) (FA) like bank code, account details, mobile wallet number, etc., primarily aimed at cash transfers in a social benefit delivery system. It is an independent module offered by OpenG2P. SPAR implements the functionality of an ID Account Mapper with the additional feature of offering a self-service portal for a beneficiary to add/update his/her FA. While in countries like India, the ID Account Mapper is updated by a bank (after authenticating a beneficiary), this may not be immediately feasible in many countries as all FSPs need to integrate with ID Account Mapper. In such situations, a department like the social welfare department can install SPAR and offer self-service updates, or via an agent. Of course, an important assumption is that an online ID authentication mechanism is available in the country via APIs. For example, in MOSIP adopting countries both biometric and OTP-based authentication is available.&#x20;

SPAR is a powerful **inclusion** tool as it gives end users the ability to choose how they would like to receive the benefits. &#x20;

SPAR may be housed centrally in a country as a building block of the Digital Public Infrastructure (DPI). Alternatively, a social welfare department can house it and enable other departments to use the same for cash disbursements.

The SPAR subsystem consists of 2 functional components

* SPAR Mapper (ID-Account Mapper)
* SPAR Beneficiary Portal

The SPAR Mapper contains the actual mapping between beneficiary IDs and their respective accounts.

The SPAR Beneficiary Portal provides the APIs that let beneficiaries view and update their account information in the registry. It exposes search APIs for a beneficiary's bank, its branch, or a mobile service provider so that the beneficiary can supply the full financial address where they wish to receive the cash credits for the benefit programs. The Beneficiary Portal is **API-only** — implementing organizations build (or integrate) their own front-end on top of these APIs.

## Functional overview

The following figure provides a Functional Architecture of the SPAR Subsystem.

{% embed url="https://miro.com/app/board/uXjVNDnhJUg=/?embedAutoplay=true&share_link_id=700848931770" %}

## Technical overview

The following picture provides a technical architecture of SPAR.

{% embed url="https://miro.com/app/board/uXjVNmpVpwg=/?embedAutoplay=true&share_link_id=979404557021" %}

The SPAR subsystem consists of the following technology components

* **openg2p-spar-mapper-partner-api** -- A FastAPI based python **microservice** that serves as the ID-mapper registry service. It provides G2P-Connect compliant APIs to update and retrieve financial address information, consumed by partner systems.
* **openg2p-spar-bene-portal-api** -- A FastAPI based python **microservice** that backs the SPAR Beneficiary Portal. It facilitates maintenance of a beneficiary's financial address by providing search APIs for banks, branches and wallet providers so that a beneficiary can provide their complete financial address in the registry. It uses a PostgreSQL persistence layer.

These services share two supporting Python packages:

* **openg2p-spar-models** -- shared SQLAlchemy models and Pydantic schemas (including the simplified DFSP models: BANK, BRANCH and WALLET-PROVIDER).
* **openg2p-spar-mapper-core** -- the core mapper logic library used by the APIs.

All SPAR source now lives in a single consolidated repository,
[spar](https://gitlab.com/openg2p/spar/spar) (`core/` for the Python
projects, `docker/` for the Dockerfiles, `deployment/` for the Helm chart and
scripts).

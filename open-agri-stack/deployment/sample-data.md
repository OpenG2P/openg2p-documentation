---
description: >-
  The sample data a demo install of Agri Stack loads: where it comes from, the
  switch in each install, how the registries' samples line up, and why a
  production install loads none.
---

# Sample Data

A demo install can load sample data in each install, so the registries show farmers, crop seasons and agents, and the [test](testing.md) has a farmer to query. A production install loads none. Sample data is never configuration: the geography and the datasets (crops, seasons, the `AGENT_*` lists…) are, and stay on in production.

Which data is configuration and which is sample, for every registry: [Country data & seeding: every switch](../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#configuration-or-sample-every-switch).

## Where it comes from

Every sample comes from the country pack in [openg2p-data](https://github.com/OpenG2P/openg2p-data) (`packs/<country>/samples/`), except the Crop Sown Registry's two clusters. Only the `ETH` pack has samples; `XKM` (fictitious) has none.

| Install | Switch | Loads | From |
| --- | --- | --- | --- |
| Commons Services (each namespace) | **Load Sample People** (on by default) | Master Data's sample people: 21 individuals in 6 households | The pack's `individuals.json`, `households.json` |
| Commons Services | **Install Mock Identity System?** (on by default) | Test identities for the national ID login, so a sample farmer can log in to the partner portal | Master Data's sample people |
| Farmer Registry | **Load Sample Data** | A farmer for every sample person, with lands, livestock, farm inputs and households; the sample approval policies and the demo staff users they name | Master Data's sample people, and the registry's own farmer fields |
| Farmer Registry | **Load Sample Images** | The sample farmers' photos | openg2p-data, in the db-seed image |
| Crop Sown Registry | **Load Sample Data** | Two clusters, in Ethiopian districts; the sample approval policies and the demo staff users | Fixed in the registry's loader |
| Crop Sown Registry | **Load sample crop seasons** | Crop seasons for every adult sample person | Master Data's sample people |
| Agents Registry, where installed | **Load Sample Data** | 24 extension agents, in the sample farmers' areas; the sample approval policies and the demo staff users | The pack's `agents.json`, taken from openg2p-data when the image is built |
| Agents Registry | **Load sample trainings** | Trainings and certifications for the sample agents | The sample agents |
| Livestock Registry, where installed | **Load Sample Data** | Six vets in the sample farmers' woredas, and one to three animals for every adult sample person; the sample approval policies and the demo staff users | The pack's `veterinarians.json`, taken from openg2p-data when the image is built, and Master Data's sample people |
| Livestock Registry | **Load sample events** | Births, vaccinations, treatments, a sale and a death for the sample animals | The sample animals and vets |

The demo staff users (`alex.carter`, `nina.patel`…) get the password set in each registry's **AWE Approver User Password**, changed at first login. The staff user `admin` is not sample data: commons-base creates it in every namespace.

## For a demo

1. Every Commons Services: the same **Country Pack**, `ETH` (the default), and **Load Sample People** on (the default).
2. Each registry: **Load Sample Data** on; the Crop Sown Registry also **Load sample crop seasons**, the Agents Registry **Load sample trainings**, the Livestock Registry **Load sample events**.
3. Install the registries after their Commons Services: their sample loaders read Master Data at install.

## How the samples line up

The registries' samples describe the same people:

* Sample person `ETH-IND-0007` is farmer `FR-0007` in the Farmer Registry, with lands `LAND-0007-1`, `LAND-0007-2`…
* The Crop Sown Registry's crop seasons are for the same farmers and plots, so a `loan-profile` query returns both for the same farmer. The test queries this farmer ([`test_install.yaml`](https://github.com/openg2p/agri-stack/blob/develop/scripts/test_install.yaml)).
* The mock identity system holds the same people, so a sample farmer can log in with their national ID in the partner portal.
* The sample agents are posted in the areas of the sample farmers.
* The Livestock Registry's sample animals belong to the same farmers (`FR-0007`, with the person's national ID), and its sample vets serve their woredas.

They match only by convention (`FR-<n>`, `LAND-<n>-<k>`): neither registry reads the other, and a change to either registry's sample IDs must be made in both. Details: [Farmer Registry](../../products/registry/farmer-registry/deployment/data-seeding.md#sample-data), [Crop Sown Registry](../../products/registry/crop-sown-registry/deployment/rancher.md#sample-data), [Agents Registry](../registries/agents-registry/deployment/rancher.md#sample-data), [Livestock Registry](../registries/livestock-registry/deployment/rancher.md#sample-data).

## When samples cannot be loaded

There is no fallback. A registry that cannot load the country's samples stops its Job with the reason in the log, and the release fails:

| Cause | Fails |
| --- | --- |
| **Load Sample People** off in the namespace's Commons Services | Farmer Registry db-seed; the Crop Sown Registry's `<release>-activity-samples` |
| A pack without samples, e.g. `XKM` | The db-seed of every registry with **Load Sample Data** on |
| A pack other than `ETH` | Crop Sown Registry db-seed (its clusters are Ethiopian) |
| Master Data not reachable from the registry | The registry's db-seed |

Load what the registry needs and upgrade it, or turn its **Load Sample Data** off.

## In production

* **Load Sample People** off in every Commons Services; **Install Mock Identity System?** off once eSignet uses the real national ID system.
* Every registry's sample switches off. Set up the approval policies in AWE and the staff users in Keycloak.
* Sample records cannot be separated cleanly from real ones afterwards: an install that loaded sample data is not promoted to production. Install fresh.

The rest of production: [Production](production.md).

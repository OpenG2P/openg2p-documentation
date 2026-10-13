---
description: >-
  How a farmer gives a bank consent in Agri Stack: in person at the bank
  with a form (built), in person digitally, or self-service (planned). What is specific to Agri
  Stack; the Consent Manager pages have the details.
---

# Consent Scenarios

A partner (e.g. a bank) needs the farmer's consent before Agri Stack shares the farmer's data with it. The consent is collected and kept by the **Consent Manager (CM)** of the exchange, not by the bank: the farmer confirms it there, or through a channel the CM checks, and the bank presents it by its ID when it queries.

<figure><img src="../../.gitbook/assets/consent-collection-scenarios.svg" alt="Three ways a farmer gives a bank consent, each with a national-ID login: 1, in person with a form (built): staff raise the request in the partner portal, the farmer logs in with the national ID and signs a form that staff upload, Consent Manager staff check it and the Farmer ID in the Farmer Registry, the bank queries with the consent ID and its admin downloads the consent record; 2, in person, digital (planned): after the login the farmer approves on the Consent Manager's screen, the consent is active at once and an SMS lets them revoke; 3, self-service (planned), where the farmer can also revoke"><figcaption><p>The three consent scenarios</p></figcaption></figure>

| Scenario | Status | How the farmer confirms |
| --- | --- | --- |
| **1 · In person, with a form** | **Built** | National-ID login (eSignet) on the bank's device, a signed form, and a check by CM staff |
| **2 · In person, digital** | Planned | National-ID login, then the farmer approves the request on the CM's own screen; active at once, no form, no staff step; an SMS to the registered phone lets them revoke |
| **3 · Self-service** | Planned | National-ID login in their own portal or app, where they approve or decline, and can revoke any consent |

In every scenario the farmer proves who they are with the national ID; an SMS is only ever a notification afterwards, never the proof.

## What is specific to Agri Stack

* **The farmer is identified by the national ID and the Farmer ID.** The consent's subject is the national ID (`FAYDA_FAN`), which the farmer logs in with. Every request must also carry the **Farmer ID** (`partnerPortal.requiredSubjectIdentifiers: [FARMER_ID]`). CM staff check it in the **Farmer Registry**, the source of truth for the link between the two, before approving. Demographics shown to them are those of the national-ID login, labelled as such, and are never compared automatically ([identifiers and demographics](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).
* **The data asked for comes from a use case.** In the partner portal, a request can start from a published use case of the composite (e.g. `loan-profile@1`): its data per registry (required and optional) fills the request.
* **One consent, every registry.** The bank queries the composite with the consent's ID (`message.consent_id`). The exchange CM turns it into one receipt per registry, with only the scopes the use case needs, and each department's CM checks its receipt ([architecture, path B](README.md#components-and-who-talks-to-whom); [exchange receipts](../../consent-management/design/exchange-receipts.md)).
* **The bank keeps a provable copy.** The consent record it downloads (receipt, signed form, CM-signed statement) is the same in every scenario ([the partner's copy](../../consent-management/design/consent-collection.md#the-partners-copy-of-a-consent)).

## Details

| Topic | Page |
| --- | --- |
| The scenarios step by step, what is built, the gaps, the partner portal | [Consent collection](../../consent-management/design/consent-collection.md) |
| The national-ID login (eSignet) | [National ID authentication](../../consent-management/design/consent-collection.md#national-id-authentication-in-the-partner-portal) |
| Turning on the partner portal, the login and the required Farmer ID | [CM deployment](../../consent-management/deployment/README.md#partner-portal-and-consent-evidence-optional) and [deploying on a cluster](../guides/deployment.md#what-to-install-in-agrix) |
| Trying it end to end | [Testing after install](../guides/testing-after-install.md) |
| What happens at query time | [Request flow](request-flow.md) |
| One consent with a grant per registry | [Consent model](consent-model.md) |

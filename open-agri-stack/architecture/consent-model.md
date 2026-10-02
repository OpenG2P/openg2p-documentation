---
description: >-
  One consent for the partner, one grant per registry inside it: why, how it
  works, what is built in the Consent Manager, and what is still open.
---

# Consent Model

{% hint style="info" %}
**Status: partly built (October 2026).**

* **Built:** a partner-signed consent can carry one **grant per registry** (`grants: [{data_controller, data_scopes}]`), and each registry validates its own grant (it sends its `data_controller` to CM `/validate`). A partner can be bound to several registries in CM, each with its own policy. Replay is per consent and registry, and each registry gets its own receipt. See [Consent Manager changes](../implementation/consent-manager.md).
* **Still to do:** presenting a consent collected through CM (farmer approval in CM) at a registry, and policies held in Partner Management. The diagrams haven't been updated yet.
{% endhint %}

## The problem

A partner asks for consent to all the fields it needs. It doesn't know or care which registries hold them. The earlier CM model, however, allowed only **one `data_controller` per consent object**, which would make partners collect a separate consent per registry.

## Proposal

**What the partner sees:** it asks once, for the fields it needs, and gets back **one consent**. It never deals with sources.

**Inside CM:** that one consent holds a **grant per registry** (data controller). Each registry validates only its own grant.

India's Account Aggregator works the same way: one consent artefact lists several data providers, and each provider checks only the accounts that belong to it.

## How it works (target)

**1. Consent request (partner → CM).** The partner states what it needs in business terms. It doesn't name any registries.

```jsonc
POST /consent-requests
{ "subject": {"type":"fayda_token","value":"…"},
  "purpose": "credit-assessment",
  "scopes": ["farmer:profile","farmer:land","crop:season","livestock:herd"],
  "validity": "P90D", "fetch_type": "oneshot" }
```

**2. CM works out which registries are involved.** The PM policy already has **one section per department**, so it doubles as the map from scope to registry. CM also checks that the requested scopes fall within the policy.

**3. The farmer sees one screen, grouped by source.**

* Example: "Farmer Registry (Ministry A): profile, land. Crop Sown Registry: crop seasons. Livestock Registry: herd."
* The farmer authenticates with a Fayda OTP, on their own or with a DA's help.
* Listing the sources tells the farmer _who_ holds the data being shared.
* If allowed, the farmer can decline individual items, so partial consent is possible.

**4. CM issues one consent artefact, signed by CM.**

```jsonc
{ "consent_id": "…", "subject": "…", "aud": "bank-a", "purpose": "credit-assessment",
  "valid_until": "…", "fetch_type": "oneshot",
  "grants": [
    { "controller": "farmer-registry",    "scopes": ["farmer:profile"] },   // land declined
    { "controller": "crop-sown-registry", "scopes": ["crop:season"] },
    { "controller": "livestock-registry", "scopes": ["livestock:herd"] }
  ] }
```

* It's stored as one consent record, with a child row per grant.
* The farmer gets **one receipt** listing all the controllers. Kantara consent receipts and ISO/IEC 27560 both allow several controllers on one receipt.
* Each department can still see every consent that touches its data.

**5. Using the consent.**

* The partner, or the composite acting for it, sends the consent ID or artefact with the request.
* Each registry calls `/validate(consent, controller = itself)`.
* CM returns **that registry's grant ∩ that registry's policy section**.
* Usage is counted **per consent and per controller**, so one-shot and periodic limits apply to each registry separately.

**6. Revocation.** The farmer can revoke the whole consent, or only one source (for example, "stop sharing my livestock data"). The partner is notified either way.

{% hint style="info" %}
**As built,** the partner signs the consent itself (the partner-embedded flow): a compact JWS with a `grants` claim, presented unchanged to every registry, directly or through the composite. The claims, signing and reason codes are in the Consent Manager's [Partner Integration Guide](../../consent-management/partner-integration-guide.md); the Open Agri Stack specifics are in the [partner guide](../guides/partner-guide.md).
{% endhint %}

## Changes in CM

| Area | Change | Status |
| --- | --- | --- |
| Consent model | One consent with several grants, replacing the single `data_controller` field | Built for partner-signed consents (`grants` claim; the single-controller form still works) |
| `/validate` | Takes the calling registry as a parameter; returns only that registry's grant ∩ its policy section, read from PM | Built with policies in CM: `data_controller` on `/validate`, bindings per (partner, controller). Reading policies from PM: open |
| Replay guard | It was keyed on the consent object's ID (`jti`), which would reject the second and third registries presented with the same consent. Move replay protection to a **per-request nonce** (the DCI envelope already carries message IDs and timestamps), and count usage per consent and controller. | Built as replay per (`jti`, controller); the per-request nonce is open |
| Consent screen and receipt | Grouped by source, with per-item decline if allowed | Consent requests with grants built; one receipt per registry today |
| Intermediary presentation | Accept a consent whose audience is the partner when a registered composite presents it | Works for partner-signed consents (the composite forwards the consent unchanged and names the partner in `header.meta.on_behalf_of`); a check that the presenter is a registered composite is open |

## Open questions

1. **Should consent that spans registries always be collected by CM?**
   * CM supports two ways: the partner collects consent in its own app and signs it ("embedded"), or CM collects it through its own screen with a Fayda OTP ("originated").
   * **Recommendation:** make CM collection the default when consent spans departments. Departments are more likely to trust a consent CM witnessed than one the bank vouches for, and the farmer sees the same screen whichever partner is asking.
   * Today a consent collected in CM cannot yet be presented at a registry ([open items](../open-items/README.md)).
2. **Should the farmer be able to decline individual items?**
   * It's better for the farmer, but the partner may get less than its use case needs.
   * The composite response already reports a status per source, so a declined item shows as `denied`.
   * Alternatively, a policy could mark some scopes as mandatory, meaning the farmer must accept all of them or none.

## Related

* [Consent Management](../../consent-management/README.md): the service, its design and APIs
* [Verification & enforcement](../../consent-management/design/verification-and-enforcement.md): the `/validate` pipeline, replay per (`jti`, controller)
* [Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md): what a registry does with the decision

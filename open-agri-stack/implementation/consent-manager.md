---
description: >-
  What changed in the Consent Manager for Agri Stack: one consent with a
  grant per registry, bindings per partner and registry, replay per consent
  and registry.
---

# Consent Manager Changes

The [consent model](../architecture/consent-model.md) needs one consent for the partner with a grant per registry. This is what is built in the [Consent Manager](../../consent-management/README.md) ([OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager)). The contract itself is documented once, in the Consent Management pages; this page only lists the changes and points there.

| Change | What it does | Documented in |
| --- | --- | --- |
| **`grants` claim** | A partner-signed consent can carry `grants: [{data_controller, data_scopes}]`, one per registry. The single-registry form (`data_controller` + `data_scopes` at the top level) still works; combining the two is `malformed_object`. | [Partner Integration Guide, step 5](../../consent-management/partner-integration-guide.md#step-5-construct-the-consent-claims) |
| **`data_controller` on `/validate`** | The calling registry names itself; CM evaluates only that registry's grant. A consent without a grant for it is denied `controller_not_granted`. | [Verification API](../../consent-management/api/verification-api.md) |
| **Bindings per (partner, controller)** | A partner can be bound to several registries, each binding with its own policy, all under the same audience | [Partner policy binding & approval](../../consent-management/design/partner-onboarding-and-policy.md) |
| **Replay per (`jti`, controller)** | Re-presenting the same consent to the same registry returns that registry's earlier decision; a second registry named in the consent gets its own decision, consent artefact and receipt. Revoking at one registry leaves the others in force. | [Security & trust](../../consent-management/design/security-and-trust.md#replay-protection) |
| **Stored decision only after the checks** | A stored decision is returned only after the partner binding and the signature are checked, and only if the presented object is the stored one (same binding, subject and scopes); a different object reusing a known `jti` is denied `replay` | [Verification & enforcement](../../consent-management/design/verification-and-enforcement.md) |
| **`subject_mismatch`** | The subject declared to CM must be the consent's subject | [Partner Integration Guide, step 8](../../consent-management/partner-integration-guide.md) |
| **Consent requests with grants, UI** | Consent requests can carry grants; the admin UI shows them | [Consent lifecycle](../../consent-management/design/consent-lifecycle.md) |
| **Build pin** | `sqlalchemy[asyncio] <2.1`, since the image died at import without `greenlet` | [Open items](../open-items/README.md) |

## What the composite relies on

* The composite forwards the partner's consent **unchanged** to every registry, signs each registry call with its own key, and names the partner in `header.meta.on_behalf_of`. CM verifies the consent against the **partner's** key and audience, not the composite's ([Partner Integration Guide, step 7](../../consent-management/partner-integration-guide.md)).
* `issued_at` must be within CM's freshness window (300 seconds by default, the same window the composite applies to `header.message_ts`), so partners sign a fresh consent for each request.

## Not built yet

* Presenting a consent collected through CM (farmer approval in CM, "originated") at a registry.
* Policies read from Partner Management instead of CM's own `PartnerPolicy`.
* Replay protection on a per-request nonce, with usage counted per consent and controller.
* A check that the presenter of a consent whose audience is a partner is a registered composite.

See [TODOs and open items](../open-items/README.md).

---
description: >-
  What changed in the Consent Manager for Agri Stack: one consent with a
  grant per registry, bindings per partner and registry, replay per consent
  and registry, exchange receipts, and the partner portal for consents
  collected in person.
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
| **Exchange receipts** | An exchange CM issues one signed consent receipt per registry when an allowed presenter (the composite) calls `/validate` with `issue_receipts: true`, limited to grant ∩ policy ∩ `requested_scopes` (`global.agriStackExchange.issuer`, `receiptPresenters`). A department CM accepts receipts from trusted exchange CMs (`trustedReceiptIssuers`, or `trustedIssuer` in Rancher) and checks each receipt's status at its issuer (`GET /consent/v1/receipts/{jti}/status`). All off by default. | [Exchange receipts](../../consent-management/design/exchange-receipts.md) |
| **`/validate` by `consent_id`** | `/validate` also takes the ID of a consent CM holds (with the partner that obtained it), checks it is active, in its validity and about the subject, and returns its grants and receipts | [Verification API](../../consent-management/api/verification-api.md) |
| **Partner portal** | A portal (`partnerPortal.*`, off by default) where partner staff, logged in through the CM's partner realm in Keycloak, record a consent given in person, upload evidence and list their consents | [Consent collection](../../consent-management/design/consent-collection.md#partner-portal) |
| **National-ID login** | The subject logs in with their national ID through eSignet during an assisted request (`partnerPortal.subjectAuth.*`); when on, a request cannot be submitted without it | [Consent collection](../../consent-management/design/consent-collection.md#national-id-authentication-in-the-partner-portal) |
| **Evidence storage** | Uploaded evidence (e.g. the signed consent form) is kept in the object store, bucket `consent-evidence` in the commons Garage (created by the commons-base Garage init job) | [Consent collection](../../consent-management/design/consent-collection.md) |
| **Staff verification, required identifiers** | CM staff verify a submitted request before the consent becomes active; `partnerPortal.requiredSubjectIdentifiers` (e.g. `[FARMER_ID]`) lists identifiers every request must carry, which staff check in the registry | [Consent collection](../../consent-management/design/consent-collection.md#identifiers-and-demographics) |
| **Consent record download** | The partner downloads a consent record signed by CM, naming the key to check it (`partnerPortal.consentRecordJwksUrl`) | [Consent collection](../../consent-management/design/consent-collection.md#the-partners-copy-of-a-consent) |
| **AWE approval optional** | Approval of data-share policies through AWE is off by default (`global.aweEnabled: false`); policies then take effect when the CM admin saves them | [Approval workflow integration](../../consent-management/design/approval-workflow-integration.md) |
| **Build pin** | `sqlalchemy[asyncio] <2.1`, since the image died at import without `greenlet` | [Open items](../open-items/README.md) |

## What the composite relies on

* **Exchange mode** (the default): the composite presents the partner's consent, or a `consent_id`, to the exchange CM and gets a receipt per registry; it sends each registry only its own receipt, which the registry validates at its department CM. The composite needs a binding and policy at each department CM (audience `agri-composite`), set by `scripts/setup_exchange.py`; the partner's bindings are at the exchange CM.
* **Passthrough mode** (a single install): the composite forwards the partner's consent **unchanged** to every registry. CM verifies the consent against the **partner's** key and audience, not the composite's ([Partner Integration Guide, step 7](../../consent-management/partner-integration-guide.md)).
* In both modes the composite signs each registry call with its own key and names the partner in `header.meta.on_behalf_of`.
* `issued_at` must be within CM's freshness window (300 seconds by default, the same window the composite applies to `header.message_ts`), so partners sign a fresh consent for each request.

## Not built yet

* Presenting a consent collected through CM (`consent_id`) in a single install (passthrough), or directly at a registry without the composite.
* Policies read from Partner Management instead of CM's own `PartnerPolicy`.
* Replay protection on a per-request nonce, with usage counted per consent and controller.
* In passthrough, a check that the presenter of a consent whose audience is a partner is a registered composite (in exchange mode, receipts are issued only to `receiptPresenters`).

See [TODOs and open items](../open-items/README.md).

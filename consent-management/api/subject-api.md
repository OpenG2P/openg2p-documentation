---
description: >-
  Subject-facing API implementing GDPR data-subject rights — access consents and
  receipts, and withdraw consent. The UI on top of these comes later.
---

# Subject API

These endpoints implement the **data-subject rights** required by GDPR. They are documented now as
part of the API-first contract; the subject-facing UI is a later phase.

**Auth:** OIDC **bearer token**, scoped to the authenticated subject. Every endpoint operates only
on consents whose subject matches the token's identity claims — a subject can never see another's
consents. **Base path:** `/consent/v1`.

## `GET /my/consents`

List the authenticated subject's consents (right of access). Paginated.

```json
// GET /my/consents?status=active&page=1&size=20  → 200
{
  "items": [
    { "consent_id": "CONSENT-123456", "partner": "Partner A",
      "purpose": { "code": "share_farm_profile", "text": "Share farmer profile with Partner A" },
      "effective_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
      "status": "active", "valid_until": "2026-05-01T12:02:10Z",
      "receipt_id": "RECEIPT-998877" }
  ],
  "total": 1, "page": 1, "size": 20, "pages": 1
}
```

Optional `?status=active|revoked|expired`.

## `GET /my/consents/{consent_id}`

Full detail of one of the subject's consents, including the partner, purpose, scopes, validity,
and source (`embedded` / `originated`).

## `GET /my/receipts/{receipt_id}`

The signed [Consent Receipt](../design/data-model.md#consent-receipt-kantara-iso-27560) for one of
the subject's consents — the portable, verifiable record (right to be informed). `403` if the
receipt does not belong to the authenticated subject.

## `POST /my/consents/{consent_id}/revoke`

Withdraw consent (right to withdraw). Effective immediately: the consent moves to `revoked`, a
revocation record is written, and the partner and subject are notified. Subsequent validation of
that consent fails with `revoked`.

```json
// request
{ "reason": "no longer want to share" }
// response 200
{ "consent_id": "CONSENT-123456", "status": "revoked", "revoked_at": "2025-07-01T10:00:00Z" }
```

`409` if already `revoked` / `expired`; `403` if the consent is not the subject's.

## Notifications

The subject is notified (channel configurable — email / SMS / push) on:

* **grant** — a new consent naming them is issued,
* **revoke** — a consent of theirs is revoked (by them, the controller, or the partner),
* **expiry** — a consent of theirs lapses.

Notification delivery is asynchronous via the consent processing queue.

## Out of scope (for now)

The **UI** (subject portal / consent dashboard) that consumes these endpoints is deferred —
this round is API-first. The contract above is stable enough to build that UI against later.

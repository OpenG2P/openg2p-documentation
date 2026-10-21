---
description: >-
  Subject-facing API for GDPR data-subject rights: list one's consents and
  receipts, and withdraw consent. Runs on the beneficiary API (off by default).
---

# Subject API

These endpoints implement the **data-subject rights** of access and withdrawal. They run on the **beneficiary API**, which the chart ships disabled ([Deployment](../deployment/README.md#api-audiences-one-chart-one-image-a-deployment-per-audience)).

**Auth:** Keycloak bearer token. The subject is read from the token (its subject ID type and value); every endpoint sees only that subject's consents. **Base path:** `/consent/v1`.

## `GET /my/consents`

The subject's consents (right of access). Optional `status` (`active`, `revoked`, `expired`), `page`, `size`.

```json
// GET /my/consents?status=active&page=1&size=20  → 200
{
  "items": [
    { "id": "5b0e…", "consent_id": "5b0e…",
      "subject_id_type": "national_id", "subject_id_value": "FARMER_1234",
      "partner_id": "bank-a", "controller_id": "farmer-registry",
      "purpose": { "code": "share_farm_profile", "text": "Share farmer profile with Partner A" },
      "effective_data_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"],
      "use_case": null, "policy_version": 3, "policy_id": "7d0c9a52-…",
      "policy_ref": "data_controller:farmer-registry",
      "status": "active", "source": "originated",
      "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z",
      "created_at": "2025-05-01T12:02:10Z", "revoked_at": null }
  ],
  "total": 1, "page": 1, "size": 20, "pages": 1
}
```

## `GET /my/consents/{consent_id}`

One of the subject's consents, as above (with `grants`, `assurance` and `consent_request_id` when set). `404` if it is not the subject's.

## `GET /my/receipts/{receipt_id}`

The signed [consent receipt](../design/data-model.md#consent-receipt-kantara-iso-27560) of one of the subject's consents. `403` if it is not the subject's.

## `POST /my/consents/{consent_id}/revoke`

Withdraw consent (right to withdraw). The consent moves to `revoked` and a revocation record is written; the next validation fails with `revoked`.

```json
// request
{ "reason": "no longer want to share" }
// response 200
{ "consent_id": "5b0e…", "status": "revoked", "revoked_at": "2025-07-01T10:00:00Z" }
```

`409` if already `revoked` or `expired`; `403` if the consent is not the subject's.

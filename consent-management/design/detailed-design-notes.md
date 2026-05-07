# Detailed Design Notes

**API Endpoints**

```
POST /consent/create-consent-creation-request
    Request:  {
                consent_type,
                consent_provider_register,
                consent_provider_person_id,
                consent_target_object_ids,
                attribute_lists,
                partner_id,
                purpose,
                validity_from,
                validity_to,
                originated_from
              }
    Response: { consent_creation_request_id, status }
    Auth:     @require_permissions("consent:create")
    Purpose:  Create a new consent request (status defaults to pending)

POST /consent/create-consent-revocation-request
    Request:  { consent_artefact_id, originated_from }
    Response: { consent_revocation_request_id, status }
    Auth:     @require_permissions("consent:revoke")
    Purpose:  Initiate revocation of an existing active consent

POST /consent/approve-consent-request
    Request:  { consent_creation_request_id, auth_provider_id }
    Response: { consent_artefact_id, consent_receipt_id, status }
    Auth:     @require_permissions("consent:approve")
    Purpose:  Approve a pending consent request — creates auth_context,
              consent_artefact, and consent_receipt in sequence

POST /consent/reject-consent-request
    Request:  { consent_creation_request_id, rejection_reason }
    Response: { consent_creation_request_id, status }
    Auth:     @require_permissions("consent:approve")
    Pre-condition: auth_context must already exist for this request
    Purpose:  Reject a pending consent request after citizen has authenticated

GET /consent/get-consent-requests
    Query:    { status?, originated_from?, validity_from?, validity_to?, page?, page_size? }
    Response: { 
                total,
                page,
                results: [{
                  consent_creation_request_id,
                  consent_type,
                  originated_from,
                  status,
                  purpose,
                  validity_from,
                  validity_to,
                  created_at
                }]
              }
    Auth:     @require_permissions("consent:view")
    Purpose:  List all consent requests with optional filtering and pagination

GET /consent/get-consent-request
    Query:    { consent_creation_request_id }
    Response: {
                consent_creation_request_id,
                consent_type,
                consent_provider_register,
                consent_provider_person_id,
                consent_target_object_ids,
                attribute_lists,
                partner_id,
                purpose,
                validity_from,
                validity_to,
                originated_from,
                status,
                created_at,
                approved_at,
                rejected_at,
                expired_at,
                rejection_reason
              }
    Auth:     @require_permissions("consent:view")
    Purpose:  Fetch full detail of a single consent request

POST /consent/validate-consent
    Request:  { consent_artefact_id }
    Response: { is_valid, status, reason? }
    Auth:     @require_permissions("consent:validate")
    Purpose:  Validate whether a consent is currently active
              (checks status = active AND validity_from ≤ now ≤ validity_to)

GET /consent/get-consent-receipt
    Query:    { consent_artefact_id }
    Response: {
                consent_receipt_id,
                consent_artefact_id,
                consent_artefact_hash,
                algorithm,
                signature,
                created_at
              }
    Auth:     @require_permissions("consent:view")
    Purpose:  Retrieve the signed consent receipt for a given artefact

POST /consent/publish-consent-receipt
    Request:  { consent_receipt_id }
    Response: { published, notified_at }
    Auth:     @require_permissions("consent:publish")
    Purpose:  Notify the citizen once consent receipt is verified and ready

GET /consent/get-pending-consent-requests-count
    Response: { count }
    Auth:     @require_permissions("consent:stats")
    Purpose:  Dashboard stat — number of pending consent requests

GET /consent/get-approved-consent-requests-count
    Response: { count }
    Auth:     @require_permissions("consent:stats")
    Purpose:  Dashboard stat — number of approved consent requests

GET /consent/get-rejected-consent-requests-count
    Response: { count }
    Auth:     @require_permissions("consent:stats")
    Purpose:  Dashboard stat — number of rejected consent requests

GET /consent/get-expired-consent-requests-count
    Response: { count }
    Auth:     @require_permissions("consent:stats")
    Purpose:  Dashboard stat — number of expired consent requests

GET /consent/get-auth-context-schema
    Response: { schema }   (JSON-LD)
    Auth:     @require_permissions("consent:view")
    Purpose:  Serve the JSON-LD schema for auth_context

GET /consent/get-consent-artefact-schema
    Response: { schema }   (JSON-LD)
    Auth:     @require_permissions("consent:view")
    Purpose:  Serve the JSON-LD schema for consent_artefact

GET /consent/get-consent-receipt-schema
    Response: { schema }   (JSON-LD)
    Auth:     @require_permissions("consent:view")
    Purpose:  Serve the JSON-LD schema for consent_receipt

GET /consent/get-auth-providers
    Response: { providers: [{ provider_id, provider_name, provider_description }] }
    Auth:     @require_permissions("consent:view")
    Purpose:  List available authentication providers (in review — may be deferred)
```

**Data Models**

```
### ConsentCreationRequest

| Field                       | Type          | Constraints / Notes                                      |
|-----------------------------|---------------|----------------------------------------------------------|
| consent_creation_request_id | UUID          | Primary key, auto-generated                              |
| consent_type                | str           | Enum: baseline, specific                                 |
| consent_provider_register   | str           |                                                          |
| consent_provider_person_id  | str           |                                                          |
| consent_target_object_ids   | list[dict]    | {"register": [<ids>]}                                    |
| attribute_lists             | list[dict]    | {"register": [<fields>]}                                 |
| partner_id                  | str           | Nullable                                                 |
| purpose                     | Text          |                                                          |
| validity_from               | datetime      |                                                          |
| validity_to                 | datetime      |                                                          |
| originated_from             | Enum          | beneficiary, agent, staff, partner                       |
| status                      | str           | pending, approved, denied, expired                       |
| created_at                  | datetime      | Auto-generated                                           |
| approved_at                 | datetime      | Nullable                                                 |
| rejected_at                 | datetime      | Nullable                                                 |
| expired_at                  | datetime      | Nullable                                                 |
| rejection_reason            | Text          | Nullable                                                 |


### ConsentRevocationRequest

| Field                          | Type     | Constraints / Notes                                   |
|--------------------------------|----------|-------------------------------------------------------|
| consent_revocation_request_id  | UUID     | Primary key, auto-generated                           |
| consent_artefact_id            | UUID     | FK → ConsentArtefact                                  |
| originated_from                | Enum     | beneficiary, agent, staff, partner                    |
| status                         | str      | pending, approved, denied, expired                    |
| created_at                     | datetime | Auto-generated                                        |
| approved_at                    | datetime | Nullable                                              |
| rejected_at                    | datetime | Nullable                                              |
| expired_at                     | datetime | Nullable                                              |
| rejection_reason               | Text     | Nullable                                              |


### AuthContext

| Field              | Type     | Constraints / Notes                                              |
|--------------------|----------|------------------------------------------------------------------|
| auth_context_id    | UUID     | Primary key, auto-generated                                      |
| consent_request_id | UUID     | FK → ConsentCreationRequest                                      |
| auth_provider_id   | str      |                                                                  |
| auth_timestamp     | datetime |                                                                  |
| auth_hash          | str      |                                                                  |
| additional_info    | JSON     | Store full token payload; extract sub, iss, exp, iat separately  |
| originated_from    | Enum     | beneficiary, agent, staff                                        |
| created_at         | datetime | Auto-generated                                                   |


### ConsentArtefact

| Field                       | Type       | Constraints / Notes                                      |
|-----------------------------|------------|----------------------------------------------------------|
| consent_artefact_id         | UUID       | Primary key, auto-generated                              |
| consent_creation_request_id | UUID       | FK → ConsentCreationRequest                              |
| auth_context_id             | UUID       | FK → AuthContext                                         |
| status                      | str        | active, revoked                                          |
| consent_type                | str        | baseline, specific — denormalised from request           |
| consent_provider_register   | str        | Denormalised from request                                |
| consent_provider_person_id  | str        | Denormalised from request                                |
| consent_target_object_ids   | list[dict] | {"register": [<ids>]}                                    |
| attribute_lists             | list[dict] | {"register": [<fields>]}                                 |
| partner_id                  | str        | Nullable                                                 |
| purpose                     | Text       | Denormalised from request                                |
| validity_from               | datetime   |                                                          |
| validity_to                 | datetime   |                                                          |
| originated_from             | Enum       | beneficiary, agent, staff, partner                       |
| created_at                  | datetime   | Auto-generated                                           |


### ConsentReceipt

| Field                  | Type     | Constraints / Notes                                         |
|------------------------|----------|-------------------------------------------------------------|
| consent_receipt_id     | UUID     | Primary key, auto-generated                                 |
| consent_artefact_id    | UUID     | FK → ConsentArtefact                                        |
| consent_artefact_hash  | str      | Hash of the artefact payload for integrity verification     |
| algorithm              | Enum     | Signing algorithm e.g. RS256, ES256                         |
| signature              | Text     | Digital signature over the artefact hash                    |
| created_at             | datetime | Auto-generated                                              |


### ConsentProcessingQueue

| Field | Type | Constraints / Notes              |
|-------|------|----------------------------------|
| TBD   |      |                                  |

```



**Logic**

```
### 1. Create Consent Request
`POST /consent/create-consent-creation-request`

1. Validate request payload (consent_type, validity dates, originated_from)
2. Validate validity_from < validity_to
3. Validate consent_target_object_ids and attribute_lists structure
4. Create ConsentCreationRequest with status = pending
5. Return consent_creation_request_id

---

### 2. Approve Consent Request
`POST /consent/approve-consent-request`

Pre-conditions:
- ConsentCreationRequest must exist
- status must be pending

Step 1 — Create AuthContext:
  1. Verify auth_provider_id is valid
  2. Call auth provider to verify authentication
  3. Create AuthContext record:
     - consent_request_id → ConsentCreationRequest
     - auth_provider_id
     - auth_timestamp = now()
     - auth_hash = hash of auth token
     - additional_info = full token payload
     - originated_from = from the consent request

Step 2 — Create ConsentArtefact:
  1. Denormalise fields from ConsentCreationRequest
  2. Link auth_context_id → AuthContext
  3. Set status = active
  4. Create ConsentArtefact record

Step 3 — Create ConsentReceipt:
  1. Serialise ConsentArtefact payload
  2. Hash the payload → consent_artefact_hash
  3. Sign the hash with configured algorithm (RS256 / ES256)
  4. Create ConsentReceipt record

Step 4 — Update ConsentCreationRequest:
  1. Set status = approved
  2. Set approved_at = now()

Step 5 — Publish:
  1. Push to consent_processing_queue for async notification
  2. Trigger POST /consent/publish-consent-receipt

---

### 3. Reject Consent Request
`POST /consent/reject-consent-request`

Pre-conditions:
- ConsentCreationRequest must exist
- status must be pending
- AuthContext must already exist for this request
  (citizen must have authenticated before rejection can be recorded)

Steps:
  1. Validate pre-conditions above
  2. Update ConsentCreationRequest:
     - status = denied
     - rejected_at = now()
     - rejection_reason = from request payload
  3. Return updated status

Note: No ConsentArtefact or ConsentReceipt is created on rejection.

---

### 4. Revoke Consent
`POST /consent/create-consent-revocation-request`
→ then approved via `POST /consent/approve-consent-request`

Phase 1 — Create Revocation Request:
  1. Validate consent_artefact_id exists
  2. Validate ConsentArtefact.status = active
  3. Create ConsentRevocationRequest:
     - consent_artefact_id → ConsentArtefact
     - originated_from = from request payload
     - status = pending

Phase 2 — Approve Revocation Request:
  1. Create AuthContext (same as approval flow — Step 1 above)
  2. Update ConsentArtefact:
     - status = revoked
  3. Update ConsentReceipt:
     - Re-hash and re-sign updated artefact payload
  4. Update ConsentRevocationRequest:
     - status = approved
     - approved_at = now()
  5. Push to consent_processing_queue for async notification

---

### 5. Validate Consent
`POST /consent/validate-consent`

1. Fetch ConsentArtefact by consent_artefact_id
2. Check ConsentArtefact.status = active
   → if revoked: return { is_valid: false, reason: "consent_revoked" }
3. Check validity_from ≤ now() ≤ validity_to
   → if before validity_from: return { is_valid: false, reason: "consent_not_yet_active" }
   → if after validity_to:    return { is_valid: false, reason: "consent_expired" }
4. Return { is_valid: true }

---

### 6. Publish Consent Receipt
`POST /consent/publish-consent-receipt`

1. Fetch ConsentReceipt by consent_receipt_id
2. Verify signature is valid
3. Notify citizen via configured channel (email / SMS / push — TBD)
4. Record notified_at timestamp
5. Return { published: true, notified_at }

---

### 7. Consent Expiry (Background Job)

Runs on a schedule (cron / queue worker):

1. Query ConsentArtefact where:
   - status = active
   - validity_to < now()
2. For each expired artefact:
   a. Update ConsentArtefact.status = revoked (or expired — TBD)
   b. Update ConsentCreationRequest.status = expired
   c. Set ConsentCreationRequest.expired_at = now()
   d. Notify citizen (TBD — same publish flow or separate notification)

---

### 8. Key Business Rules

- A ConsentArtefact is ONLY created on approval — never on rejection or revocation request
- A ConsentReceipt is ONLY created after a ConsentArtefact is successfully created
- Rejection requires AuthContext to exist — citizen must authenticate before rejection is recorded
- A revocation request can only be raised against an active ConsentArtefact
- Validation always reads from ConsentArtefact — not from ConsentCreationRequest
- All state transitions are append-only — timestamps are never overwritten
```

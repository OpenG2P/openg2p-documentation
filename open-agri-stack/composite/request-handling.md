---
description: How the Composite serves a request.
---

# Request Handling

What the [Composite](README.md) does for each partner request, as built. The same request hop by hop, across the installs: [request flow](../architecture/request-flow.md). The use-case keys named here (`requirement`, `depends_on`, `timeout_ms`, …) are in [Use-Case Configuration](use-case-configuration.md#sources).

## Per request

1. Verifies the partner's signature against PM (key `PARTNER_<SENDER_ID>`). Checks the message is fresh (`header.message_ts` within 300 seconds) and addressed to the Composite.
2. Checks that the partner has a policy for the use case (`name@major`) in the Exchange's PM: cached; no grant fails with `partner_not_allowed`, and PM unreadable with nothing cached with `partner_policy_unavailable`.
3. Validates the input (subject type, parameters) and applies the per-partner rate limit.
4. Checks the consent. For a `consent_jws`: the partner's signature, the subject, the validity window, and a grant with the use case's required [data scopes](use-case-configuration.md#data-scopes) for every mandatory source; the Exchange CM then accepts it only if the partner's policy for the use case allows partner-signed consents (`partner_consent_not_accepted`). A `consent_id` is checked by the Exchange CM (active, in its validity, obtained by this partner, about this subject). With no consent, the Exchange CM looks up the partner's active consent for this subject and use case (Exchange mode only; passthrough mode refuses with `consent_required`).
5. Gets a consent token per registry from the Exchange CM, sending the partner, the subject, the use case and its purpose so that the CM applies the partner's policy for that use case. A deny fails the request (`consent_denied`, with the CM's reason, e.g. `consent_not_found`); a mandatory source without a consent token fails it too; an optional one is reported `unavailable`.
6. Calls the sources in dependency order (`depends_on`), in parallel within a level, each a DCI sync search signed with the Composite's key, naming the partner in `header.meta.on_behalf_of` and carrying that registry's consent token. Per-source timeout and retries; overall timeout.
7. Maps the results, computes derived fields, and returns a response signed by the Composite, with a status per source (`ok`, `no_record`, `denied`, `unavailable`, `error`).
8. Sends audit events to the Audit Manager, without ever blocking the request.

## Registry calls

**Every source is one DCI synchronous search** on a registry's **partner API**: `POST /dci/registry/sync/search`. The Composite calls nothing else on a registry, and nothing about a registry is hard-coded: the endpoint comes from the service's settings ([Deployment: registries](../deployment/composite-chart-settings.md#registries)), and what is asked comes from the use case's source (`controller`, `dci`, [query template](use-case-configuration.md#query-templates)). For `loan-profile`, a request makes one call to the Exchange CM, one to the Farmer Registry, then two parallel calls to the Crop Sown Registry.

The Composite renders the source's query template, adds the rest, signs the envelope with its own key and posts it:

```json
{"signature": "<composite's detached JWS>",
 "header": {"version": "1.0.0", "message_id": "…", "message_ts": "…", "action": "search",
            "sender_id": "agri-composite", "receiver_id": "farmer-registry",
            "total_count": 1, "is_msg_encrypted": false,
            "meta": {"on_behalf_of": "bank-a", "request_id": "<request_id>", "use_case": "loan-profile@1"}},
 "message": {"transaction_id": "<request_id>",
             "search_request": [{"reference_id": "<request_id>-farmer", "timestamp": "…", "locale": "eng",
                                 "search_criteria": {"version": "1.0.0",
                                                     "reg_type": "Farmer",
                                                     "reg_record_type": "spdci-extensions-dci:Farmer",
                                                     "query_type": "expression",
                                                     "query": {"type": "expression", "value": {"…": "…"}},
                                                     "pagination": {"page_size": 1, "page_number": 1},
                                                     "authorize": {"consent_jws": "<this registry's consent token>"}}}]}}
```

* `sender_id` is the Composite's PM ID; the registry verifies the Composite's signature against `PARTNER_AGRI_COMPOSITE`.
* `receiver_id` is the source's controller ID unless the registry's `receiverId` is set.
* `header.meta.on_behalf_of` names the partner. The registry logs it; it never grants access.
* The registry's consent token travels at `search_criteria.authorize.consent_jws`, as for a partner calling the registry directly ([Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md)).
* A list query that returns a full page (`page_size` above 1) is reported with the detail "the first N records only".

## Failure handling

| Setting / situation | Behaviour |
| --- | --- |
| `requirement: mandatory` | The source must succeed (`ok` or `no_record`), and the consent must have a grant for its controller, or the request fails |
| `requirement: optional` | Failure is reported in `sources` and the request still succeeds (with `partial_response: allowed`). No grant for it in the consent → `denied`, not called |
| `timeout_ms` | Per attempt |
| `retries` | Extra attempts **on network errors (connect, read, timeout) and HTTP 5xx only**, with a short backoff (0.1 s × attempt, at most 0.5 s). A 4xx or a DCI rejection is not retried |
| `overall_timeout_ms` | When reached, every source not yet finished is `unavailable` with `detail: "overall timeout reached"` |
| `depends_on` | A source whose dependency is not `ok` is **not called**; it takes the dependency's status, with `detail: "not called: dependency '<id>' is <status>"` |
| `partial_response: allowed` | Only a failing mandatory source fails the request |
| `partial_response: denied` | Any source that is `denied`, `unavailable` or `error` fails the request |

### Source statuses

| Status | When |
| --- | --- |
| `ok` | The search succeeded with records |
| `no_record` | The search succeeded with none |
| `denied` | HTTP 401/403; or a rejected search whose reason reads like an authorisation decision (consent, not permitted, subject mismatch, `controller_not_granted`…); or no grant in the consent |
| `unavailable` | Unreachable, timed out, HTTP 408/429/5xx (after retries), or the overall timeout |
| `error` | Any other non-200, a rejected search for another reason, a non-JSON or malformed answer, a response signature that does not verify (when the registry's `partnerId` is set), a template that fails to render, a query with an empty `subject_id`, no endpoint configured |

**When the request fails** because of a source, the HTTP status is: any `denied` → **403** `source_denied`; else any `unavailable` → **504** if a timeout was involved, otherwise **503** (`source_unavailable`); else **502** `source_error`. `sources` is still included.

## Consent mode

The consent mode is a service setting, `exchange` by default, as on the Agri Stack Exchange ([setting it](../deployment/composite-chart-settings.md#consent-mode-and-the-exchange-cm)). Each registry receives its **own consent token** from the Exchange CM, not the partner's consent. The partner onboards and is granted use cases only at the Exchange (its PM); each department CM trusts the Exchange CM's consent tokens and applies the Composite's scope policy in the department's PM.

After the partner checks (steps 1–4 above), the Composite calls the Exchange CM's `POST /consent/v1/validate` with:

```json
{"consent_jws": "<the partner's consent>", "partner_id": "agri-composite",
 "issue_receipts": true,
 "request_context": {"subject_id": {"type": "FAYDA_FAN", "value": "…"},
                     "use_case": "loan-profile@1", "purpose": "credit-assessment",
                     "requested_scopes": ["<the use case's scopes>"]}}
```

* With a `consent_id`, it sends `consent_id` and `consent_partner_id: <the calling partner>` instead of `consent_jws`; with neither, only `consent_partner_id`, and the Exchange CM looks up the partner's active consent for this subject and use case ([consent by lookup](../../consent-management/api/verification-api.md#consent-by-lookup)).
* The Exchange CM applies the calling partner's policy for the use case from PM: it must exist (`use_case_not_granted`), the consent's purpose must match, and a `consent_jws` is accepted only if the policy allows partner-signed consents (`partner_consent_not_accepted`).
* `partner_id` is the Composite's, which must be one of the Exchange CM's **token presenters** (`receiptPresenters`). On `permit`, the answer carries `receipts: {<data_controller>: <consent token JWS>}` (consent tokens are called *receipts* in the API), limited to `requested_scopes`. The Composite applies the use case's scope rules to the grants (`consent_grant_missing`, `consent_scope_missing`) and sends each registry its own token; the registry passes it to its own CM as usual ([Exchange consent tokens](../../consent-management/design/exchange-consent-tokens.md)).

| Situation | Result |
| --- | --- |
| Exchange CM answers `deny` | **403** `consent_denied` (with the CM's reason code); no registry is called |
| No consent token for a **mandatory** source's controller | **403** `consent_receipt_missing`; no registry is called |
| No consent token for an **optional** source's controller | The source is `unavailable`, not called, with `detail: "not called: the exchange Consent Manager issued no consent receipt for <controller>"` |
| Exchange CM unreachable, timed out, HTTP 408/429/5xx, or no URL configured | **503** `consent_exchange_unavailable` (fails closed) |
| Exchange CM answers another non-200 or a non-JSON body | **502** `consent_exchange_error` |
| Use case with `consent.required: false` | The Exchange CM is not called and registries get no consent |

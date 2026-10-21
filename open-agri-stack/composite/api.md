---
description: >-
  API reference for the Agri Stack Composite: list and describe use cases,
  query a use case with a signed envelope, and the staff console's read-only
  API.
---

# Composite API

The Composite serves approved use cases. A partner sends one signed request about one farmer, with the farmer's consent. The Composite queries each registry the use case names and returns one signed response.

* **Base URL:** `https://<composite host>/composite/v1`
* **Who calls it:** partners (banks, MFIs, agritechs) onboarded in Partner Management with a policy there for the use case (`name@major`). Staff use the console API.
* **Signing:** the query body is an envelope `{signature, header, message}`. `signature` is a detached JWS over `{header, message}`, made with the partner's key. The Composite verifies it against the partner's keys in Partner Management (`header.sender_id`). The Composite signs every response, errors included, with its own key.
* **Consent:** send `message.consent_id` (a consent the farmer gave, held by the Exchange's Consent Manager) or `message.consent_jws` (a consent the partner signed). The Exchange turns it into a consent token for each registry.
* **Result:** each source (registry query) gets a status: `ok`, `no_record`, `denied`, `unavailable` or `error`. A failed optional source leaves its fields null. A failed mandatory source fails the request.

{% hint style="info" %}
For the step-by-step (onboarding, keys, consent, signing, verifying the response), see the [Partner Guide](../partner-guide.md).
{% endhint %}

## Operations

| Method | Path | What it does | Signed |
| --- | --- | --- | --- |
| `GET` | `/composite/v1/use-cases` | List the published use cases | No |
| `GET` | `/composite/v1/use-cases/{use_case}` | Describe one use case: subject types, parameters, sources, consent grants and data scopes, output fields | No |
| `POST` | `/composite/v1/use-cases/{use_case}/query` | Query a use case for one subject | Request and response |
| `GET` | `/composite/v1/admin/...` | Console API (staff, read-only) | Staff login |

`{use_case}` is `name` (for example `loan-profile`) or `name@major` (for example `loan-profile@1`). Without a major version, the highest published one is used. The `X-Use-Case-Major` header can name the major version instead.

## Error codes

An error from a query is a signed envelope too. `header.status` is `rjct`, and `message.error` has the `code` and a `message`.

| HTTP | Codes |
| --- | --- |
| 400 | `invalid_envelope`, `wrong_receiver`, `stale_request`, `invalid_use_case`, `invalid_input`, `consent_id_needs_exchange` |
| 401 | `signature_invalid` |
| 403 | `partner_not_allowed`, `consent_required`, `consent_malformed`, `consent_signature_invalid`, `consent_subject_mismatch`, `consent_not_yet_valid`, `consent_expired`, `consent_grant_missing`, `consent_scope_missing`, `consent_denied`, `consent_receipt_missing`, `source_denied` |
| 404 | `unknown_use_case` |
| 429 | `rate_limited` |
| 500 | `signing_unavailable` |
| 502 | `source_error`, `consent_exchange_error` |
| 503 | `source_unavailable`, `consent_exchange_unavailable`, `partner_policy_unavailable` |
| 504 | `source_unavailable` (a mandatory source timed out) |

The two codes about the partner's use-case grant ([data-sharing policies](../architecture/data-sharing-policies.md#fail-closed)):

* **`403 partner_not_allowed`:** the partner has no policy for this use case (`name@major`) in Partner Management. Message: `partner 'bank-b' is not granted the use case loan-profile@1 in Partner Management`.
* **`503 partner_policy_unavailable`:** Partner Management cannot be read to check the grant and no recent answer is cached. Message: `Partner Management cannot be read to check the partner's use-case grant; try again later`.

## Use cases

{% openapi-operation spec="agri-composite-api" path="/composite/v1/use-cases" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/use-cases/{use_case}" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/use-cases/{use_case}/query" method="post" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

## Console API (staff)

The console's read-only API, used by the [Composite Console](console.md). It needs a staff login (IAM) with the `composite:view` permission. It is present only when the console is on.

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/overview" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/use-cases" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/use-cases/{use_case}" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/registries" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/registries/{registry_id}/data-scopes" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/partners" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

{% openapi-operation spec="agri-composite-api" path="/composite/v1/admin/activity" method="get" %}
[OpenAPI agri-composite-api](https://raw.githubusercontent.com/OpenG2P/agri-stack/develop/composite/docs/openapi/openapi-composite.json)
{% endopenapi-operation %}

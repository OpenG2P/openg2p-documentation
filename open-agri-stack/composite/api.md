---
description: The Composite's endpoints.
---

# Composite API Reference

The endpoints of the [Composite](README.md), their request and response formats and error codes. How to use them, step by step (onboarding, keys, consent, signing the request, verifying the response): [Partner Guide: Fetching Farmer Data](../partner-integration-guide.md).

* **Base URL:** `https://<composite host>/composite/v1`
* **Authentication:** a query is a signed envelope `{signature, header, message}`, verified against the partner's keys in Partner Management; every response is signed by the Composite. The console API needs a staff login.

## Operations

| Method | Path | What it does | Signed |
| --- | --- | --- | --- |
| `GET` | `/composite/v1/use-cases` | List the published use cases | No |
| `GET` | `/composite/v1/use-cases/{use_case}` | Describe one use case: subject types, parameters, sources, consent grants and data scopes, output fields | No |
| `POST` | `/composite/v1/use-cases/{use_case}/query` | Query a use case for one subject | Request and response |
| `GET` | `/composite/v1/admin/...` | Console API (staff, read-only) | Staff login |

These three endpoints serve every use case: `{use_case}` is a path parameter, not a separate API per use case. Publishing a use case creates no endpoint and needs no code or deployment of the API: once its file is loaded, it is listed by `GET /composite/v1/use-cases` and answered at `/composite/v1/use-cases/<its name>/query`, for partners with a policy for it. `{use_case}` is `name` (for example `loan-profile`) or `name@major` (for example `loan-profile@1`). Without a major version, the highest published one is used. The `X-Use-Case-Major` header can name the major version instead.

## Error codes

An error from a query is a signed envelope too. `header.status` is `rjct`, and `message.error` has the `code` and a `message`.

| HTTP | `error.code` | Meaning |
| --- | --- | --- |
| 200 | — | Success (some optional sources may still be `denied` / `unavailable` / `error`) |
| 400 | `invalid_envelope`, `wrong_receiver`, `stale_request`, `invalid_use_case`, `invalid_input`, `consent_id_needs_exchange` | Bad envelope, wrong `receiver_id`, `message_ts` more than 300 s from now, bad `@major`, bad subject or parameters (or both `consent_jws` and `consent_id` sent), a `consent_id` when the Composite is not in Exchange mode |
| 401 | `signature_invalid` | The envelope signature does not verify against your PM key (or you are unknown in PM) |
| 403 | `partner_not_allowed` | You have no policy for this use case (`name@major`) in Partner Management: ask the Exchange's partner manager ([Partner Guide, step 2](../partner-integration-guide.md#step-2-get-onboarded-in-partner-management)) |
| 403 | `consent_required`, `consent_malformed`, `consent_signature_invalid`, `consent_subject_mismatch`, `consent_not_yet_valid`, `consent_expired`, `consent_grant_missing`, `consent_scope_missing` | A consent problem found by the Composite before any registry is called (`consent_required`: no consent sent in passthrough mode; `consent_scope_missing`: a mandatory source's required scopes are not granted) |
| 403 | `consent_denied` | The Exchange Consent Manager denied the consent; its reason code is in the message (e.g. `consent_not_found`: you sent none and it holds none for this farmer and use case; `partner_consent_not_accepted`: you signed the consent but your policy does not allow it; `use_case_not_granted`, `purpose_not_allowed`, `policy_unavailable`) |
| 403 | `consent_receipt_missing` | The Exchange Consent Manager issued no consent token for a mandatory source's registry |
| 403 | `source_denied` | A mandatory source was denied (e.g. by the Consent Manager at the registry) |
| 404 | `unknown_use_case` | No published use case of that name / major |
| 429 | `rate_limited` | Rate limit reached |
| 500 | `signing_unavailable` | The Composite cannot sign (its key is missing); the body is unsigned (`signature` empty). Every other answer, errors and `429` included, is signed |
| 502 | `consent_exchange_error` | The Exchange Consent Manager rejected the call or gave an unreadable answer |
| 502 / 503 / 504 | `source_error` / `source_unavailable` | A mandatory source failed: error / unavailable / timed out |
| 503 | `consent_exchange_unavailable` | The Exchange Consent Manager could not be reached, timed out, or is not configured |
| 503 | `partner_policy_unavailable` | Partner Management cannot be read to check your use-case grant and no recent answer is cached; try again later |

**`503 partner_policy_unavailable`** and **`403 partner_not_allowed`** are the two answers about the partner's use-case grant; why they fail closed: [data-sharing policies](../architecture/data-sharing-policies.md#fail-closed).

When a registry denies a consent, the reason in `message.sources.<id>.detail` comes from the Consent Manager's `reason_code` ([Consent Manager Partner Integration Guide, step 8](../../consent-management/partner-integration-guide.md)).

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

---
description: APIs available for the Registry Partner ecosystem
---

# Partner API

{% hint style="info" %}
**Every partner API call must be signed.** `POST /dci/registry/sync/search`, `POST /partner/ingest_data`, `POST /partner/activity/append_activities`, `POST /partner/activity/correct_activities` and `POST /partner/data_scopes` carry a detached JWS made with the partner's key, which the registry verifies against Partner Management. The unsigned `GET /partner/data_scopes` is off by default. Only `/ping` and the API description are open. `REGISTRY_PARTNER_API_SIGNATURE_VALIDATION_ENABLED` (on by default) switches the check off for testing only. See [Authentication and signature verification](../../design/partner-apis.md#authentication-and-signature-verification).
{% endhint %}

{% openapi-operation spec="registry-partner-api" path="/partner/ingest_data" method="post" %}
[OpenAPI registry-partner-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-partner.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-partner-api" path="/dci/registry/sync/search" method="post" %}
[OpenAPI registry-partner-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-partner.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-partner-api" path="/ping" method="get" %}
[OpenAPI registry-partner-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-partner.json)
{% endopenapi-operation %}

{% openapi-schemas spec="registry-partner-api" schemas="DciAuthorize,DciConsent,DciEncryptedMessage,DciPagination,DciPurpose,DciQuery,DciRequestHeader,DciResponseHeader,DciSearchCriteria,DciSearchRequest,DciSearchRequestEnvelope,DciSearchRequestItem,DciSearchResponse,DciSearchResponseEnvelope,DciSearchResponseItem,DciSearchResultData,DciSearchResultPagination,DciSortItem,ErrorListResponse,ErrorResponse,G2PPaginationResponse,G2PResponseHeader,G2PResponseStatus,HTTPValidationError,IngestDataPayload,IngestDataResponse,IngestDataResponseBody,ValidationError" grouped="true" %}
[OpenAPI registry-partner-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-partner.json)
{% endopenapi-schemas %}

---
description: APIs available for the Registry Partner ecosystem
---

# Partner API

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

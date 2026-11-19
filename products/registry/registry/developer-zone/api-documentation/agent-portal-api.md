---
description: APIs used by the Agent Portal UI to issue and verify credentials
---

# Agent Portal API

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/get_vc_types" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/lookup_beneficiary" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/start_authentication" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/get_authentication_status" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/create_wallet_offer" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-issuance/issue_vc" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/vc-verification/verify_vc" method="post" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-operation spec="registry-agent-portal-api" path="/ping" method="get" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-operation %}

{% openapi-schemas spec="registry-agent-portal-api" schemas="AuthenticationStatusPayload,AuthenticationStatusRequest,AuthenticationStatusRequestBody,AuthenticationStatusResponse,AuthenticationStatusResponseBody,AuthenticationStatusResultPayload,ErrorListResponse,ErrorResponse,G2PPaginationRequest,G2PPaginationResponse,G2PRequestHeader,G2PResponseHeader,G2PResponseStatus,HTTPValidationError,IssueVcPayload,IssueVcRequest,IssueVcRequestBody,IssueVcResponse,IssueVcResponseBody,IssueVcResultPayload,LookupBeneficiaryPayload,LookupBeneficiaryRequest,LookupBeneficiaryRequestBody,LookupBeneficiaryResponse,LookupBeneficiaryResponseBody,LookupBeneficiaryResultPayload,StartAuthenticationPayload,StartAuthenticationRequest,StartAuthenticationRequestBody,StartAuthenticationResponse,StartAuthenticationResponseBody,StartAuthenticationResultPayload,ValidationError,VcTypeInfo,VcTypesResponse,VcTypesResponseBody,VcTypesResultPayload,VerifyCredentialPayload,VerifyCredentialRequest,VerifyCredentialRequestBody,VerifyCredentialResponse,VerifyCredentialResponseBody,VerifyCredentialResultPayload,WalletOfferPayload,WalletOfferRequest,WalletOfferRequestBody,WalletOfferResponse,WalletOfferResponseBody,WalletOfferResultPayload" grouped="true" %}
[OpenAPI registry-agent-portal-api](https://raw.githubusercontent.com/OpenG2P/registry-platform/develop/apis/docs/openapi/openapi-agent-portal.json)
{% endopenapi-schemas %}

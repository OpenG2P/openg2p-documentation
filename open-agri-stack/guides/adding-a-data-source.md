---
description: >-
  Adding a registry as a data source of a composite use case, step by step:
  registry prerequisites, Partner Management, Consent Manager, the composite's
  configuration, the partner's consent, and testing. Example: a Livestock
  Registry.
---

# Adding a Data Source

A use case's data sources are registries. Adding one needs **no code in the composite**: the registry must speak DCI with consent, PM and CM must know about it, and the composite gets a URL and a new `sources[]` entry. This guide uses a **Livestock Registry** (controller `livestock-registry`) added to `loan-profile` as an optional source.

{% hint style="info" %}
The Livestock Registry is [planned](../design/register-model-design.md#livestock-registry-an-entity-and-occurrences-in-one-registry), not built. Its record type, scopes and query below are illustrative; use the real ones of the registry you add.
{% endhint %}

## Overview

| Step | Where | Who |
| --- | --- | --- |
| [1. Registry prerequisites](#step-1-registry-prerequisites) | The registry | Registry team |
| [2. Identities in Partner Management](#step-2-identities-in-partner-management) | PM | PM administrator |
| [3. Bindings and policies in the Consent Manager](#step-3-bindings-and-policies-in-the-consent-manager) | CM | CM administrator, department (AWE) |
| [4. Register the endpoint in the composite](#step-4-register-the-endpoint-in-the-composite) | Composite Helm values | Agri Stack operator |
| [5. Add the source to the use case](#step-5-add-the-source-to-the-use-case) | Use-case YAML | Use-case author |
| [6. Partners add a grant](#step-6-partners-add-a-grant) | Partner's consent | Each partner |
| [7. Test](#step-7-test) | Laptop / cluster | Operator |

## Step 1 — Registry prerequisites

The registry must answer the composite exactly as it answers a partner:

* **DCI synchronous search** at `POST /dci/registry/sync/search` on its partner API, for the record type the use case needs. Every OpenG2P registry built on the [registry platform](../../products/registry/registry/README.md) has it ([Partner APIs](../../products/registry/registry/design/partner-apis.md)).
* **Signature validation against PM** on (`global.partnerSignatureValidationEnabled`, the default), with the PM key backend (`global.registryCryptoBackend: partner-mgmt`) and `global.partnerManagementApiUrl` pointing at PM. It then accepts the composite's signature (`PARTNER_AGRI_COMPOSITE`).
* **Consent enforcement** on (`global.consentEnforcementEnabled`, the default), with `global.consentManagerUrl`, and **`global.consentDataController`** set to the registry's controller ID: here `livestock-registry` (it defaults to `global.registryVariant`). The registry sends it to CM `/validate`, so CM evaluates only this registry's grant. See [Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md).
* **Subject identifiers that pass the consent subject check.** The registry rejects a search whose subject is not the consent's subject. The consent's subject is what the partner sent (a Fayda FAN or a farmer ID), so the registry must hold that identifier on its records, or link its own key to it (`subject_id_fields` for an activity register, e.g. a farmer ID recorded with the farmer's FAN). If the registry is keyed on something else (e.g. a farmer ID only), the source must [depend on a source](#step-5-add-the-source-to-the-use-case) that returns that key, and the registry must be able to link it to the consent's subject.
* **A data scope catalogue.** Consents name the registry's [data scopes](../../products/registry/registry/design/data-scopes.md), `<controller>.<name>` (e.g. `livestock-registry.animals`, `livestock-registry.owner_reference`): by default one per register section, plus any named scopes the extension ships in `meta_data/data-scopes/`. The registry publishes them at `POST /partner/data_scopes` (signed) and filters each record to the consented fields before rendering it. If another source depends on a value from this registry's record, one scope must carry it.

## Step 2 — Identities in Partner Management

* **The composite** is already a PM partner (`PARTNER_AGRI_COMPOSITE`); the new registry verifies it with the key PM serves. Nothing to add.
* **The registry**, if you want the composite to verify the registry's **response** signatures: onboard the registry in PM under its DCI ID (e.g. `livestock-registry` → `PARTNER_LIVESTOCK_REGISTRY`) with its signing key, and set `partnerId` in step 4. Optional.

See the PM [API reference](../../platform/platform-services/partner-management/api-reference.md).

## Step 3 — Bindings and policies in the Consent Manager

For **each partner** that will receive the new data, the CM administrator creates a binding of the partner to the new controller and a policy for it ([Partner policy binding & approval](../../consent-management/design/partner-onboarding-and-policy.md)):

| Binding | Value |
| --- | --- |
| `audience` | the partner's ID, e.g. `bank-a` |
| `controller_id` | `livestock-registry` |
| `partner_mgmt_id` | `PARTNER_BANK_A` |

with a policy listing the scopes the department allows (e.g. `animals`, `owner_reference`), the purpose (`credit-assessment`), the subject identifier types (`FAYDA_FAN`, `FARMER_ID`), the signing algorithms, the maximum validity and the fetch type. A new or wider policy may wait for the department's AWE approval.

## Step 4 — Register the endpoint in the composite

Add the registry's DCI search URL under its controller ID, in the composite's Helm values (Rancher **Edit YAML**):

```yaml
composite:
  registries:
    farmer-registry:
      url: https://partner-fr.<dept-domain>/dci/registry/sync/search
      partnerId: ""
    crop-sown-registry:
      url: https://partner-csr.<dept-domain>/dci/registry/sync/search
      partnerId: ""
    livestock-registry:
      url: https://partner-lsr.<dept-domain>/dci/registry/sync/search   # the registry's partner API (full URL)
      partnerId: ""                                          # or livestock-registry, to verify its responses
```

The chart passes this to the service as `AGRI_COMPOSITE_REGISTRIES`; the upgrade rolls the pods. Add the registry **before** any use case names it: a use case whose sources name a controller with no endpoint fails to load.

## Step 5 — Add the source to the use case

Add a `sources[]` entry to the use case (in `composite.useCases.loan-profile`), with its query template, dependencies, requirement and timeouts, and map its records into the output:

```yaml
sources:
  # … farmer, season_summaries, crop_seasons as before …
  - id: herd
    controller: livestock-registry
    requirement: optional          # the request still succeeds without it
    depends_on: [farmer]           # only if the registry needs the farmer ID from the Farmer Registry
    dci:
      reg_type: Livestock          # the registry's register
      reg_record_type: spdci-extensions-agri:Animal   # the record type it serves (illustrative)
      query_template: |
        {%- set ns = namespace(fid=none) -%}
        {%- if subject.type == 'FARMER_ID' -%}{%- set ns.fid = subject.value -%}{%- endif -%}
        {%- for rec in sources.farmer.records -%}
          {%- for ident in rec.farmer_personal_details.member_identifier or [] -%}
            {%- if ns.fid is none and ident.identifier_type == 'FARMER_ID' and ident.identifier_value -%}
              {%- set ns.fid = ident.identifier_value -%}
            {%- endif -%}
          {%- endfor -%}
        {%- endfor -%}
        {"query_type": "expression",
         "query": {"type": "expression",
                   "value": {"expression": {"query": {"owner_id": {"$eq": {{ ns.fid | tojson }} } } } } },
         "pagination": {"page_size": 50, "page_number": 1} }
    timeout_ms: 3000
    retries: 1

response:
  mapping:
    # … existing mappings …
    herd.animals: "$.sources.herd.records"
  derived:
    # … existing derived values …
    herd.animal_count: "count($.sources.herd.records)"
```

* **`depends_on`:** leave it out if the registry can be searched by the partner's subject directly (then it is called in the first level, in parallel with the farmer). Keep it if the query needs another source's result.
* **`requirement`:** `optional` for data that is useful but not essential; `mandatory` only if the use case is meaningless without it (a failure or missing grant then fails the whole request).
* **Timeouts:** `timeout_ms` and `retries` per source; check that `execution.overall_timeout_ms` still leaves room for the new level (here 8000 ms covers two levels of 3000 ms).
* **Version:** adding an optional source and new output fields is backward compatible: bump the minor version (`1.1.0`). A change that breaks the response (renamed or removed fields) needs a new major.
* The template is rendered with sample input when the file loads; a template that doesn't render valid JSON stops the file from loading (the previous version keeps serving). The rules are in [query templates](composite-configuration.md#query-templates).

## Step 6 — Partners add a grant

A partner's consent must carry a **grant for the new controller**, naming scope IDs from the new registry's catalogue, to get the new data. Example, for `loan-profile` with a livestock source:

```json
"grants": [
  {"data_controller": "farmer-registry", "data_scopes": ["farmer-registry.farmer_identifiers", "farmer-registry.personal_details", "…"]},
  {"data_controller": "crop-sown-registry", "data_scopes": ["crop-sown-registry.crop_season", "…"]},
  {"data_controller": "livestock-registry", "data_scopes": ["livestock-registry.animals", "livestock-registry.owner_reference"]}
]
```

**Partners whose consent lacks the new grant:**

| The new source is | Without a grant |
| --- | --- |
| `optional` | It is reported `denied` (`detail: "the consent has no grant for livestock-registry"`) and **not called**; the rest of the response is unchanged |
| `mandatory` | The request **fails** before any registry is called: `403 consent_grant_missing` |

So add a new source as `optional` unless every partner can be asked to update its consent first. The describe endpoint's `consent_grants_needed` lists the new controller once the use case reloads.

## Step 7 — Test

* **Describe:** `GET /composite/v1/use-cases/loan-profile` should list the new source, its `depends_on`, the new output fields and `livestock-registry` in `consent_grants_needed`. If it doesn't, check the composite's logs for a load error.
* **End to end:** the [end-to-end test](end-to-end-test.md) sets up PM and CM for the registries in its built-in list (Farmer and Crop Sown) and builds a consent with those two grants; for a new registry, set up the CM binding and policy (step 3) yourself, and call with the [partner test kit](partner-guide.md#test-kit) after extending its grants, or with your own client.
* **Check the statuses:** with a grant and a matching record the new source is `ok`; without a record `no_record`; without a grant `denied`; with the registry down `unavailable`, while the rest of the response still comes back.

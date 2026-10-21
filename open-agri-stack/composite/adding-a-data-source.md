---
description: >-
  Adding a registry as a data source of a Composite use case, step by step:
  registry prerequisites, Partner Management, the department's ceiling for the
  Composite, the Composite's configuration, the partner's consent, and testing. Example: a Livestock
  Registry.
---

# Adding a Data Source

A use case's data sources are registries. Adding one needs **no code in the Composite**: the registry must speak DCI with consent, the department's PM and CM must accept the Composite, and the Composite gets a URL and a new `sources[]` entry. This guide uses a **Livestock Registry** (controller `livestock-registry`) added to `loan-profile` as an optional source.

{% hint style="info" %}
The Livestock Registry is [planned](../design/livestock-registry.md), not built. Its record type, scopes and query below are illustrative; use the real ones of the registry you add.
{% endhint %}

## Overview

| Step | Where | Who |
| --- | --- | --- |
| [1. Registry prerequisites](#step-1-registry-prerequisites) | The registry | Registry team |
| [2. Identities in Partner Management](#step-2-identities-in-partner-management) | PM | PM administrator |
| [3. The Composite's ceiling in the department](#step-3-the-composites-ceiling-in-the-department) | Department PM and CM | Department partner manager, operator (setup script) |
| [4. Register the endpoint in the Composite](#step-4-register-the-endpoint-in-the-composite) | Composite Helm values | Agri Stack operator |
| [5. Add the source to the use case](#step-5-add-the-source-to-the-use-case) | Use-case YAML | Use-case author |
| [6. Partners add a grant](#step-6-partners-add-a-grant) | Partner's consent | Each partner |
| [7. Test](#step-7-test) | Laptop / cluster | Operator |

## Step 1 — Registry prerequisites

The registry must answer the Composite exactly as it answers a partner:

* **DCI synchronous search** at `POST /dci/registry/sync/search` on its partner API, for the record type the use case needs. Every OpenG2P registry built on the [registry platform](../../products/registry/registry/README.md) has it ([Partner APIs](../../products/registry/registry/design/partner-apis.md)).
* **Signature validation against PM** on (`global.partnerSignatureValidationEnabled`, the default), with the PM key backend (`global.registryCryptoBackend: partner-mgmt`) and `global.partnerManagementApiUrl` pointing at PM. It then accepts the Composite's signature (`PARTNER_AGRI_COMPOSITE`).
* **Consent enforcement** on (`global.consentEnforcementEnabled`, the default), with `global.consentManagerUrl`, and **`global.consentDataController`** set to the registry's controller ID: here `livestock-registry` (it defaults to `global.registryVariant`). The registry sends it to CM `/validate`, so CM evaluates only this registry's grant. See [Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md).
* **Subject identifiers that pass the consent subject check.** The registry rejects a search whose subject is not the consent's subject. The consent's subject is what the partner sent (a national ID or a farmer ID), so the registry must hold that identifier on its records, or link its own key to it (`subject_id_fields` for an activity register, e.g. a farmer ID recorded with the farmer's national ID). If the registry is keyed on something else (e.g. a farmer ID only), the source must [depend on a source](#step-5-add-the-source-to-the-use-case) that returns that key, and the registry must be able to link it to the consent's subject.
* **A data scope catalogue.** Consents name the registry's [data scopes](../../products/registry/registry/design/data-scopes.md), `<controller>.<name>` (e.g. `livestock-registry.animals`, `livestock-registry.owner_reference`): by default one per register section, plus any named scopes the extension ships in `meta_data/data-scopes/`. The registry publishes them at `POST /partner/data_scopes` (signed) and filters each record to the consented fields before rendering it. If another source depends on a value from this registry's record, one scope must carry it.

## Step 2 — Identities in Partner Management

* **The Composite** (`PARTNER_AGRI_COMPOSITE`) must be onboarded with its key in the department's PM; the new registry verifies it with the key PM serves. The setup script adds it if missing ([step 7](#step-7-test)).
* **The registry**, if you want the Composite to verify the registry's **response** signatures: onboard the registry in PM under its DCI ID (e.g. `livestock-registry` → `PARTNER_LIVESTOCK_REGISTRY`) with its signing key, and set `partnerId` in step 4. Optional.

See the PM [API reference](../../platform/platform-services/partner-management/api-reference.md).

## Step 3 — The Composite's ceiling in the department

The department that runs the new registry decides what it releases to the Composite ([data-sharing policies](../architecture/data-sharing-policies.md)). It needs:

* **A scope policy for the Composite** in the department's PM: partner `PARTNER_AGRI_COMPOSITE`, data controller `livestock-registry`, with the scopes and purposes of the use cases that read the registry (e.g. `livestock-registry.animals`, `livestock-registry.owner_reference`; `credit-assessment`), the subject identifier types (`FAYDA_FAN`, `FARMER_ID`), the signing algorithms, the maximum validity and the fetch type ([scope policy for the Composite](../architecture/registries.md#scope-policy-for-the-composite)). [`scripts/setup_exchange.py`](../deployment/after-install.md#exchange-setup) raises it as a PM policy request from the published use cases and approves it ([step 7](#step-7-test)); to approve it yourself, see [access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies).
* **Trust of the Exchange CM** as a consent-token issuer, in the department's CM: **Exchange Role** department in the department's commons-services form (`global.agriStackExchange.role`; it trusts `agri-stack-exchange-cm` presented by `agri-composite` by default). The setup script checks it and stops if it is missing. See [Exchange consent tokens](../../consent-management/deployment/README.md#setting-up-a-department).

Partners need nothing per registry: a partner with a policy for `loan-profile@1` in the Exchange's PM gets the new source with it, as far as its consent grants it ([step 6](#step-6-partners-add-a-grant)). A new major version (`loan-profile@2`) needs its own policy per partner in the Exchange's PM.

## Step 4 — Register the endpoint in the Composite

Add the registry's DCI search URL under its controller ID, in the Composite's Helm values (Rancher **Edit YAML**):

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
    scopes: [livestock-registry.owner_reference, livestock-registry.animals]   # the consent must grant these
    optional_scopes: [livestock-registry.animal_location]                      # may grant; else their fields are null
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
    timeout_ms: 10000
    retries: 0

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
* **`scopes` and `optional_scopes`:** scope IDs from the registry's catalogue. The consent must grant every one of `scopes` (else a mandatory source fails the request, an optional one is reported `denied` and not called); `optional_scopes` it may leave out. They are listed per registry in the describe endpoint's `consent_scopes`, and in Exchange mode they are the `requested_scopes` the consent tokens are limited to. See [data scopes](use-case-configuration.md#data-scopes).
* **Timeouts:** `timeout_ms` and `retries` per source; check that `execution.overall_timeout_ms` still covers the slowest path. In `loan-profile` it is 25000 ms, for two levels of 10000 ms; `herd` depends on the farmer, so it runs in the second level with the crop sources and adds no level.
* **Version:** adding an optional source and new output fields is backward compatible: bump the minor version (`1.1.0`). A change that breaks the response (renamed or removed fields) needs a new major.
* The template is rendered with sample input when the file loads; a template that doesn't render valid JSON stops the file from loading (the previous version keeps serving). The rules are in [query templates](use-case-configuration.md#query-templates).

## Step 6 — Partners add a grant

A partner's consent must carry a **grant for the new controller**, naming scope IDs from the new registry's catalogue (at least the source's `scopes`), to get the new data. A consent held in the Consent Manager (`consent_id`) needs the grant too, so a new consent is recorded. Example, for `loan-profile` with a livestock source:

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

* **Describe:** `GET /composite/v1/use-cases/loan-profile` should list the new source, its `depends_on`, the new output fields and `livestock-registry` in `consent_grants_needed`. If it doesn't, check the Composite's logs for a load error.
* **End to end:** rerun the [Exchange setup](../deployment/after-install.md#exchange-setup) with `--registry <controller>=<namespace>` for the new registry: it adds the Composite's key and its scope policy with the use cases' scopes to that department's PM (PM requests, raised and approved). Then test with the [partner test](../deployment/testing.md#partner-test-public-apis), which builds the consent from the use case's `consent_scopes`.
* **Check the statuses:** with a grant and a matching record the new source is `ok`; without a record `no_record`; without a grant `denied`; with the registry down `unavailable`, while the rest of the response still comes back.

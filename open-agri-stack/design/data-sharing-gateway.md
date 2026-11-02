---
description: >-
  Decisions for restructuring Agri Stack: the Exchange becomes a generic Data
  Sharing Gateway, a stack is content (packs) on top of it, registries are
  called through standard-aware connectors, and the Exchange setup moves into
  the install.
---

# Data Sharing Gateway

**Status: decided.** Setup at install is built; the rest is not, and its steps are in [TODOs](../open-items/README.md#platform-and-build).

## Why

The Composite, Partner Management (PM) and the Consent Manager (CM) work for any set of registries, yet their code, charts and names say "Agri" throughout (`agri_composite`, `AGRI_COMPOSITE_*`, `agriStackExchange`, `agri-stack-exchange-cm`, `PARTNER_AGRI_COMPOSITE`). The same layer should serve a Health stack, or any other, with no Agri code in it.

## The Data Sharing Gateway

* **Name.** What is called the Exchange today becomes the **Data Sharing Gateway**. It pulls data from many registries with consent, combines it per use case and delivers it to authorised consumers: one direction, so "exchange" over-promises. Two-way exchange between parties is OAN's job ([Interoperability with OAN](oan-interoperability.md)).
* **Write-backs stay with the registries.** Data coming back (a bank reporting a loan disbursed, a lab uploading soil results) is a write to a registry through that registry's own partner APIs, not through the gateway.
* **Generic.** No mention of Agri, or of any stack, in the gateway's code, charts or Rancher forms; no "context" option either. The Composite stays its component name.
* **Rename.** The Agri names above become generic. The change breaks environment variables, values keys, the consent token's issuer and audience, and partner IDs, so it is one coordinated release of the Composite, CM, PM and Commons Services. The CM roles `exchange` / `department` are renamed with it (e.g. `gateway` / `source`).

## Stacks are content

A stack (Agri Stack, a later Health stack) is a set of choices on top of the gateway, delivered as content, not as a chart. There is no stack umbrella chart: registries live in their own namespaces and usually exist before the gateway, and the gateway already has its charts (Commons Services and the Composite).

| Pack | Loaded by | Agri Stack contents |
| --- | --- | --- |
| **Gateway pack** | The Composite chart (a ConfigMap built from the folder, or an OCI or image artifact) | Registries (controller ID, standard or profile, connector options); connector profiles; use cases |
| **Catalogue pack** | Master Data (the country pack, as today) | The Agri catalogue and scope codes |
| **Reference registry configurations** | The registry installs | Farmer Registry and Crop Sown Registry fields and sample data |

URLs stay chart values, since they differ per install. A country copies the packs and edits them; its own registries, names and fields are system integrator work. Farmer Registry and Crop Sown Registry are references, not prescriptions.

**What sets one stack apart from another:** its use cases, its catalogue and code lists, its reference registries, and the standards its registries speak. None of it is code in the gateway.

### Repositories

* **The gateway's repository** (today's `agri-stack`, renamed; name open) holds the Composite and generic tooling (setup script, partner kit).
* **`agri-stack`** stays as the place people look for the product. It holds content only: the packs, reference registry configurations, examples, and demo and test scripts. Its README only links to the documentation; all documentation stays in GitBook.
* The registries stay in their own repositories.

## Standards

**The standard belongs to the registry, not the use case.** A registry speaks one standard for every use case, so the registry's entry in the gateway pack names it once (`standard: dci-sync-search@1`). A use case names only the registry.

**A connector handles the standard:** the envelope, signing and response-signature checks, where the consent token goes, where the records are in a response, telling *denied* from *failed*, and pagination. The gateway engine knows connectors, not standards. DCI is the first connector (what `core/dci.py` does today); others are added as needed and are not tied to a stack.

**When a registry does not match a standard**, or a government has proprietary standards:

| Level | When | Where | Gateway code? |
| --- | --- | --- | --- |
| 1. Connector options | Small deviations: another version, envelope fields, consent in a header, another records path or refusal code, another signing algorithm | The registry's entry in the gateway pack | No |
| 2. Derived profile | A standard close to an existing one: overrides on top of it (`et-dci@1 extends dci@1`) | A profile file in the gateway pack, written once | No |
| 3. Generic HTTP/JSON profile | A proprietary but ordinary REST/JSON standard, declared in full: request template, consent placement, records path, denied and error rules, pagination | A profile file in the gateway pack, written once by the system integrator | No |
| 4. Connector plugin | What a declaration cannot express: custom crypto, session or multi-step auth, XML/SOAP, async callbacks, cursor pagination, an unusual query language | A Python package implementing the connector interface, in an image built `FROM` the Composite API image, set in the Composite chart's image field | Yes, outside the gateway's own code |

The connector interface is published: build the request from criteria, subject and consent; parse the response into a status and records; sign and verify; next page; and say whether it supports given criteria, so that a use case it cannot run fails when it is saved, not when it is called.

**Proprietary data models need nothing extra.** Each registry's catalogue lists its own scopes and fields; the gateway never assumes DCI's data model.

## Writing use cases

Defining use cases becomes an administrator's job, so an administrator never sees envelopes or status rules. A use case states:

* registries and scopes, picked from the catalogue;
* inputs: subject ID types and parameters;
* the query as plain criteria (`foundational_id = subject`, `crop_year = parameters.crop_year`), which the connector translates;
* output fields, picked from the fields the chosen scopes expose.

Raw request templates and JSONPath mappings stay available for what criteria cannot express (for example, reading the Farmer ID from another source's record).

| Who | Writes |
| --- | --- |
| OpenG2P | The engine and the connectors |
| Stack or system integrator | The packs: registries and their standards, profiles, catalogue, starter use cases |
| Gateway administrator | Use cases, as needs emerge |

## Setup at install

**Built.** The former one-time setup after install is done by the install, in production too ([what the install sets up](../architecture/exchange.md#what-the-install-sets-up)):

* **Partner portal realm.** keycloak-init already creates the realm, client and roles. It also declares the `partner_id` user attribute and its token mapper, configurable per realm and client and set by the CM chart. Creating partner staff users stays an operations task.
* **The Composite's key.** The Composite chart generates its signing key into a Secret at install when it is missing, and serves its public keys at `/.well-known/jwks.json`. It writes to no Partner Management.
* **Onboarding the Composite.** A generic PM chart option (`bootstrapPartners: [{partnerId, jwksUrl}]`) onboards partners at install; the install raises and approves the request, an exception to separating the roles. PM reads a partner's keys from its JWKS URL when needed (cached), instead of copying them once at onboarding.
* **Any install order.** Because PM fetches the key when needed, a department can onboard the Composite before the gateway exists. Registries usually exist first: the department's Commons Services upgrade that sets the gateway role and domain also onboards the Composite. A fresh install can put the gateway first.
* **Departments decide what they release.** The department's bootstrap creates only the partner and its key source, with no scope policy. Until the department's administrator adds one, the registry releases nothing to the gateway.
* Changing keys after install: by hand ([Keys](../administration/keys.md)). One script tests an install, configured with the install's names ([Testing](../deployment/testing.md)).

## Open questions

1. The gateway repository's name (`data-sharing-gateway`, `composite`).
2. The criteria language and field picker now, or first only the connector split with use cases as files.
3. Gateway packs and use cases edited in the console: starter use cases from the pack seed the database ([editing use cases in the console](../open-items/README.md#composite)).
4. The gateway pack's delivery format: a ConfigMap from a folder, or an OCI or image artifact.
5. Whether a department may list its scope policy for the gateway in its own install values (an empty list releases nothing).

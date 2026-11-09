---
description: The Exchange for any stack.
---

# Generic Exchange

**Status: decided, not built** ([Roadmap, phase 3](README.md#phase-3-many-departments-other-stacks-conveniences)).

## Why

The Composite, Partner Management (PM) and the Consent Manager (CM) work for any set of registries, yet their code, charts and names say "Agri" throughout (`agri_composite`, `AGRI_COMPOSITE_*`, `agriStackExchange`, `agri-stack-exchange-cm`, `PARTNER_AGRI_COMPOSITE`). The same layer should serve a Health stack, or any other, with no Agri code in it.

## A generic Exchange

* **Generic.** No mention of Agri, or of any stack, in the Exchange's code, charts or Rancher forms; no "context" option either. The Composite stays its component name.
* **Rename.** The Agri names above become generic. The change breaks environment variables, values keys, the consent token's issuer and audience, and partner IDs, so it is one coordinated release of the Composite, CM, PM and Commons Services. The CM roles `exchange` / `department` keep their names.

## Stacks are content

A stack (Agri Stack, a later Health stack) is a set of choices on top of the Exchange, delivered as content, not as a chart. There is no stack umbrella chart: registries live in their own namespaces and usually exist before the Exchange, and the Exchange already has its charts (Commons Services and the Composite).

| Pack | Loaded by | Agri Stack contents |
| --- | --- | --- |
| **Exchange pack** | The Composite chart (a ConfigMap built from the folder, or an OCI or image artifact) | Registries (controller ID, standard or profile, connector options); connector profiles; use cases |
| **Catalogue pack** | Master Data (the country pack, as today) | The Agri catalogue and scope codes |
| **Reference registry configurations** | The registry installs | Farmer Registry and Crop Sown Registry fields and sample data |

URLs stay chart values, since they differ per install. A country copies the packs and edits them; its own registries, names and fields are system integrator work. Farmer Registry and Crop Sown Registry are references, not prescriptions.

**What sets one stack apart from another:** its use cases, its catalogue datasets, its reference registries, and the standards its registries speak. None of it is code in the Exchange.

### Repositories

* **The Exchange's repository** (today's `agri-stack`, renamed; name open) holds the Composite and generic tooling (setup script, partner kit).
* **`agri-stack`** stays as the place people look for the product. It holds content only: the packs, reference registry configurations, examples, and demo and test scripts. Its README only links to the documentation; all documentation stays in GitBook.
* The registries stay in their own repositories.

## Standards

**The standard belongs to the registry, not the use case.** A registry speaks one standard for every use case, so the registry's entry in the Exchange pack names it once (`standard: dci-sync-search@1`). A use case names only the registry.

**A connector handles the standard:** the envelope, signing and response-signature checks, where the consent token goes, where the records are in a response, telling *denied* from *failed*, and pagination. The Exchange's engine knows connectors, not standards. DCI is the first connector (what `core/dci.py` does today); others are added as needed and are not tied to a stack.

**When a registry does not match a standard**, or a government has proprietary standards:

| Level | When | Where | Exchange code? |
| --- | --- | --- | --- |
| 1. Connector options | Small deviations: another version, envelope fields, consent in a header, another records path or refusal code, another signing algorithm | The registry's entry in the Exchange pack | No |
| 2. Derived profile | A standard close to an existing one: overrides on top of it (`et-dci@1 extends dci@1`) | A profile file in the Exchange pack, written once | No |
| 3. Generic HTTP/JSON profile | A proprietary but ordinary REST/JSON standard, declared in full: request template, consent placement, records path, denied and error rules, pagination | A profile file in the Exchange pack, written once by the system integrator | No |
| 4. Connector plugin | What a declaration cannot express: custom crypto, session or multi-step auth, XML/SOAP, async callbacks, cursor pagination, an unusual query language | A Python package implementing the connector interface, in an image built `FROM` the Composite API image, set in the Composite chart's image field | Yes, outside the Exchange's own code |

The connector interface is published: build the request from criteria, subject and consent; parse the response into a status and records; sign and verify; next page; and say whether it supports given criteria, so that a use case it cannot run fails when it is saved, not when it is called.

**Proprietary data models need nothing extra.** Each registry's catalogue lists its own scopes and fields; the Exchange never assumes DCI's data model.

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
| Exchange administrator | Use cases, as needs emerge |

## Open questions

1. The Exchange repository's name (e.g. `composite`).
2. The criteria language and field picker now, or first only the connector split with use cases as files.
3. Exchange packs and use cases edited in the console: starter use cases from the pack seed the database ([editing use cases in the console](README.md)).
4. The Exchange pack's delivery format: a ConfigMap from a folder, or an OCI or image artifact.
5. Whether a department may list its scope policy for the Composite in its own install values (an empty list releases nothing).

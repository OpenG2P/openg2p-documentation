---
description: >-
  Creating a Composite use case, step by step: what the partner needs, the
  use-case file, putting it into the Composite's configuration, checking it
  loaded, granting it to partners, the departments' ceilings, and testing. Also how to
  read a use case in the console.
---

# Creating a Use Case

A use case is one configuration file the [Composite](README.md) loads; no code changes. These are the steps. The file format is in [Use-Case Configuration](use-case-configuration.md), how a use case runs in the [Composite overview](README.md#what-the-first-version-does); adding a new registry as a source is in [Adding a Data Source](adding-a-data-source.md).

## Step 1 — Decide what the partner needs

Write down:

* **Purpose:** why the partner asks (e.g. `credit-assessment`). It goes in the consent, and the partners' and departments' policies in Partner Management must allow it.
* **Inputs:** how the farmer is identified ([subject ID types](use-case-configuration.md#subject-id-types)) and any parameters (e.g. a crop year).
* **Output fields:** what the partner gets back.

Then find which registries hold that data and which of their [data scopes](../../products/registry/registry/design/data-scopes.md) cover it. Each registry's scope catalogue is on the console's **Registries** page; the scopes the shipped registries offer are under [farmer data](../architecture/registries.md#farmer-data-the-composite-reads) and [crop data](../architecture/registries.md#crop-data-the-composite-reads).

## Step 2 — Write the use case file

Start by copying [`composite/use-cases/loan-profile.yaml`](https://github.com/openg2p/agri-stack/blob/develop/composite/use-cases/loan-profile.yaml) and change its name (`use_case`), `version`, `title`, `purpose` and `input`. The parts to get right:

* **`sources`:** one search per registry. For each:
  * `controller`: the registry.
  * `requirement`: what happens if it can't answer. `mandatory` fails the request; `optional` continues without it ([failure handling](README.md#failure-handling)).
  * `depends_on`: the sources it runs after, when its query needs their result (e.g. the farmer ID from the farmer record).
  * `scopes` and `optional_scopes`: the data scopes from step 1 ([data scopes](use-case-configuration.md#data-scopes)).
  * `dci.query_template`: the search ([query templates](use-case-configuration.md#query-templates)).
* **`response.mapping` and `response.derived`:** the output fields, copied from the sources or computed ([response mapping and derived values](use-case-configuration.md#response-mapping-and-derived-values)).

Every key is listed in [use-case file structure](use-case-configuration.md#file-structure); unknown keys stop the file from loading. [The `loan-profile` use case](use-case-configuration.md#the-loan-profile-use-case) explains the sample setting by setting.

## Step 3 — Put it into the Composite's configuration

Use cases are entries in the Composite's Helm values ([Deployment: Composite, use cases](../deployment/composite.md#use-cases)):

* **Rancher:** open the Composite app, **Edit YAML**, and add an entry under `composite.useCases`: the use case's name, then the file's text as a block (`my-use-case: |`). Upgrade. Templates must be inline here (`query_template: |`), since each entry becomes one `<name>.yaml` key.
* **Your own ConfigMap** (e.g. GitOps): set `composite.existingUseCasesConfigMap` to its name and add the file as key `<name>.yaml` (and any `.j2` templates next to it).

Running pods pick up the change within the reload interval (`composite.useCasesReloadSeconds`, default 30 s, plus the time the ConfigMap takes to update), without a restart.

## Step 4 — Check it loaded

* **Console:** the **Use cases** page lists it. A file that failed to load is shown there with its error.
* **API:** `GET /composite/v1/use-cases` (or `/composite/v1/use-cases/<name>`) on the Composite returns it with its sources, output fields and `consent_scopes`.

Only `status: published` is served. If it is missing, check the error on the console or in the Composite's logs.

## Step 5 — Grant it to partners

A partner gets one **use-case policy per use case** it may call. In the Exchange's Partner Management, give each partner a policy for this use case as `name@major` (e.g. `my-use-case@1`), with the use case's purpose:

* **A new partner:** in its onboarding request, with its keys.
* **An onboarded partner:** **Add policy** on the partner (a policy request). Its other use cases' policies are untouched.

Steps: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md). The [partner test](../deployment/testing.md#partner-test-public-apis) does this for its test partner when given the PM admin credentials (`--use-case`).

## Step 6 — Update the departments' ceilings for the Composite

Rerun the [Exchange setup](../deployment/after-install.md#exchange-setup) (`scripts/setup_exchange.py`) after step 4, so the new use case is published. It reads the published use cases and, in each department's PM, raises and approves a policy request that widens the Composite's scope policy to cover the new scopes and purpose ([scope policy for the Composite](../architecture/registries.md#scope-policy-for-the-composite)). Without the script, each department widens it itself ([when use cases change](../deployment/exchange.md#when-use-cases-change)). Until then the registry withholds the new scopes.

## Step 7 — Test

* **Partner test:** `python scripts/partner_test.py --base-domain <domain> --partner <partner> --use-case <name> --auto-approve` ([partner test](../deployment/testing.md#partner-test-public-apis)). It builds the consent from the use case's scopes. It sends only the `crop_year` and `season` parameters (`--crop-year`, `--season`).
* **`scripts/exchange_test.sh`** runs the Exchange setup and the partner test in one go (`--use-case <name>`, default `loan-profile`).

Read the status of each source in the response: `ok`, `no_record`, `denied`, `unavailable` or `error` ([source statuses](README.md#source-statuses)). A mandatory source that isn't `ok` or `no_record` fails the request.

## Reading a use case in the console

The **Use cases** page of the [console](console.md) shows each use case with these labels:

| Label | Meaning |
| --- | --- |
| **Use case** | e.g. `loan-profile · version 1.0.0 (partners call @1)`: the name, the full version, and the major version partners call (`loan-profile@1`). A breaking change to the response needs a new major. |
| **Source (search)** | The source's `id`: one search of one registry |
| **Registry** | The registry the search goes to (`controller`) |
| **If it can't answer** | `requirement`. **Fail the request** (`mandatory`) or **Continue without it** (`optional`): the response still succeeds if the registry is down, has no record, or the consent doesn't cover it; the source's status tells the partner. |
| **Runs after** | `depends_on`: the sources whose result this search needs |
| **Required scopes** | Data scopes the consent must grant for this source |
| **Optional scopes** | Data scopes the consent may leave out; the fields they cover are then `null` |
| **Output fields** | What the partner gets: the `mapping` fields and the `derived` values. Scopes are what the Composite may read from a registry; output fields are what the partner receives. |

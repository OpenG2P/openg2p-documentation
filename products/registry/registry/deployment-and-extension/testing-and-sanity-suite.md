---
description: >-
  The in-built sanity/e2e suite, its two-part model (tests that are independent
  of the registry's domain vs tests tied to its fields), and how a domain
  registry extends the field-specific tests.
---

# Testing & the sanity suite

The platform ships an end-to-end **sanity suite** as an image, `openg2p-registry-sanity-tests` (source in `registry-platform/test/sanity`). It runs as a Kubernetes Job against a *deployed* registry and exercises the real flows — auth, consent-aware DCI search, and a change-request through the full AWE approval workflow — not just unit tests. The reference registry passes it out of the box, so every platform build is self-verified.

## Two axes: smoke vs e2e, and generic vs field-specific

The suite is organised along **two independent axes**.

**Axis 1 — depth:**

* **Smoke** — liveness/wiring (ping, OpenAPI routes). Fast; safe to run on every install/upgrade.
* **e2e** — full signed round-trips (DCI search + consent enforcement; change-request → AWE approval → applied change → version history → audit).

**Axis 2 — dependence on the domain (the important one for extenders):**

| Set | Depends on the registry's fields? | Examples |
|---|---|---|
| **Set 1 — extension-independent** | **No** — tests the *platform mechanics*, identical for every registry | ping/readiness, auth, "search without consent is rejected", "bad signature is rejected", the change-request → AWE → apply → history **flow** |
| **Set 2 — field-specific** | **Yes** — tied to *which* register, *which* fields, *which* consent scopes | the DCI response actually contains the consented field values; a specific field round-trips through a change request; scope clamping over the registry's own scopes |

Set 1 is written once, in the platform, and **runs unchanged on any registry** — including one that has been extended into a completely different domain. Set 2 is where a domain registry differs, because the fields, register mnemonic, UI sections and DCI template are its own.

## How a domain registry extends the tests

The sanity image mirrors the app's base-and-extension shape. The **harness** (clients, signing, consent/partner/keycloak/AWE seeding, DB helpers) and **Set 1** are baked into `openg2p-registry-sanity-tests`. A domain registry builds its own sanity image **FROM** it and supplies only its **Set 2** — the field-specific tests and config — while Set 1 and the harness are inherited and run as-is:

```dockerfile
ARG RP_VERSION=<version>
FROM registry.gitlab.com/openg2p/registry/registry-platform/sanity-tests:${RP_VERSION}

COPY test/sanity/sanity/fixtures.py               /app/sanity/fixtures.py
COPY test/sanity/sanity/data_seed.py              /app/sanity/data_seed.py
COPY test/sanity/tests/test_e2e_dci.py            /app/tests/test_e2e_dci.py
COPY test/sanity/tests/test_e2e_change_request.py /app/tests/test_e2e_change_request.py
```

Four files overwrite the reference registry's versions at the same paths. Nothing else about the image changes — no `sanity.env`, no extra test directory.

Concretely, adapting Set 2 for a new registry means pointing the suite at your domain:

* the register **mnemonic / id** and the table it seeds a test record into;
* the **consent scopes** and the assertions on the returned DCI record (your DCI template's shape);
* the **UI tab / section** the change-request test edits, and the field it changes.

Most of this is configuration; genuinely new scenarios are a few small pytest files that reuse the shipped harness fixtures. Set 1 is not touched.

### The configuration, exactly

Everything above is supplied as env from the chart's `registry.sanity.*` values rather than baked into the image — which is what lets one image run against any environment. Three of the keys mislead, so they are worth stating precisely:

| Value | Type | Note |
|---|---|---|
| `farmerRegisterId` | string | **This is the register id**, whatever the registry is about — the subchart helpers, the suite's `cfg` object and every variant's override use this spelling. See *inherited names* below |
| `regType` | string | Your register mnemonic; goes into the DCI envelope as `reg_type` |
| `regRecordType` | string | The DCI record type |
| `searchText` | string | The injected record's `functional_record_id`. Must equal what your `data_seed.py` writes — the DCI search matches `search_text ILIKE '%…%'` |
| `dataScopes` | **comma-separated string** | Not a YAML list. Must name real **top-level keys** of your outbound DCI template |
| `deniedScopes` | **comma-separated string** | Scopes deliberately not consented to; the clamping test asserts they never come back |
| `crTabId` / `crSectionId` | string | A real, **editable** section, or the change-request write is rejected |

{% hint style="warning" %}
Left at their defaults these carry the **reference registry's** values, so the suite passes or fails for reasons unrelated to your registry. A mistyped values key renders happily with the subchart default and gives no warning — after `helm template`, grep the output for `SANITY_FARMER_REGISTER_ID` and `SANITY_DCI_REG_TYPE` and check they are yours.
{% endhint %}

{% hint style="info" %}
**Inherited names.** `farmerRegisterId` in the chart, and `FARMER_INTERNAL_ID` / `farmer_seeded` / `cfg.farmer_register_id` in the suite, are named for the registry the harness was first written against. They mean *"the seeded registrant"*. Renaming them means changing the platform harness, `conftest.py` and every variant's overlay in one commit, so they stay — treat them as generic.
{% endhint %}

### The tests that need no cluster

The sanity suite proves a **deployed** registry works, and needs commons-services, Keycloak admin and a namespace. A second, much cheaper set proves the **repository** is coherent — field names resolving to real columns, dropdowns having code lists, consent scopes existing in the DCI template, seed SQL being re-runnable — and runs in CI on every push, before anything is published.

Those checks catch a class of failure the sanity suite cannot see early enough, because it is silent: see [Contracts that fail silently](../developer-zone/building-a-registry/contracts-that-fail-silently.md). Every registry should ship both.

## Running it

The suite is enabled and configured through the Helm chart's `sanity.*` values (image, `enabled`, `runE2e`, and the field config above). Its output narrates each e2e test as a clearly titled, timestamped step sequence with a pass/fail footer, so a Job log reads as a readable end-to-end story rather than raw assertions.

{% hint style="info" %}
Because Set 1 is domain-independent, the same platform-level guarantees (auth, consent enforcement, approval-workflow integrity, audit) are re-verified on **every** registry built on the platform — the extender only proves that *their* fields flow correctly.
{% endhint %}

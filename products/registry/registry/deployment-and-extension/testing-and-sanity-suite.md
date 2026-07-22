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
FROM openg2p/openg2p-registry-sanity-tests:<version>
COPY tests_fields/   /app/tests_fields/     # your field-specific tests (Set 2)
COPY sanity.env      /app/sanity.env        # your register id, fields, scopes, UI tab/section
```

Concretely, adapting Set 2 for a new registry means pointing the suite at your domain:

* the register **mnemonic / id** and the table it seeds a test record into;
* the **consent scopes** and the assertions on the returned DCI record (your DCI template's shape);
* the **UI tab / section** the change-request test edits, and the field it changes.

Most of this is configuration; genuinely new scenarios are a few small pytest files that reuse the shipped harness fixtures. Set 1 is not touched.

## Running it

The suite is enabled and configured through the Helm chart's `sanity.*` values (image, `enabled`, `runE2e`, and the field config above). Its output narrates each e2e test as a clearly titled, timestamped step sequence with a pass/fail footer, so a Job log reads as a readable end-to-end story rather than raw assertions.

{% hint style="info" %}
Because Set 1 is domain-independent, the same platform-level guarantees (auth, consent enforcement, approval-workflow integrity, audit) are re-verified on **every** registry built on the platform — the extender only proves that *their* fields flow correctly.
{% endhint %}

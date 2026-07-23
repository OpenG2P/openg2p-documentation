---
description: >-
  The in-cluster sanity suite for the National Social Registry — what it inherits
  from the platform and the field-specific tests this repo contributes.
---

# Sanity testing

The National Social Registry is verified end-to-end in-cluster by a pytest suite run as a post-install/upgrade Helm Job. As with the chart and the images, the suite is **inherited from the platform and narrowed here**.

{% hint style="info" %}
The two-part test model — what is extension-independent, what is field-specific, and how a registry extends it — is documented once in the platform docs: [**Testing & the sanity suite**](../../registry/deployment-and-extension/testing-and-sanity-suite.md). This page covers only the NSR side.
{% endhint %}

## What is inherited, what is NSR's

The platform publishes `openg2p/openg2p-registry-sanity-tests` containing the **harness** (signing, DCI envelope building, PM/CM/Keycloak/AWE seeding, DB helpers, step logging, the run entrypoint) and **Set 1 — the extension-independent tests**: liveness and wiring, and the fail-closed cases (a search without consent, with a bad signature, or with an unknown consent audience must all be rejected). Those run unchanged on every registry.

The NSR image is a thin `FROM` of it that layers on **Set 2 — the field-specific parts**, four files in [`test/sanity`](https://github.com/OpenG2P/national-social-registry/tree/develop/test/sanity):

| File | What is NSR-specific |
|---|---|
| `sanity/fixtures.py` | The seeded test record and the `g2p_register_individuals` tables |
| `sanity/data_seed.py` | Idempotent injection into `g2p_register_individuals` |
| `tests/test_e2e_dci.py` | Assertions against the NSR DCI template |
| `tests/test_e2e_change_request.py` | The register and history rows are verified in the NSR tables |

Everything else — the register id, DCI reg-type, consent scopes and the change-request tab/section — is **configuration**, supplied as env from the chart's `registry.sanity.*` values rather than baked into the image.

{% hint style="info" %}
NSR's Individual register currently matches the platform's reference registry, because **the reference was derived from NSR**. These four files are therefore close to the platform's own. Owning them here is deliberate: it means NSR's fields can diverge — new registers, a changed DCI template, different UI coordinates — without touching the platform.
{% endhint %}

### A note on inherited names

`cfg.farmer_register_id` and the `farmer_seeded` pytest fixture are names owned by the **inherited** harness and `conftest.py`. They are not NSR concepts — here they simply carry NSR's Individual register and its seeded record.

## What the e2e covers

Two flows, both against a live deployment:

* **DCI data-sharing** — the partner signs a DCI envelope and an embedded consent JWS with its Partner Management key; the registry verifies the envelope, calls Consent Manager `/validate`, renders the record through the DCI template, and clamps it to the consented scopes. The suite asserts the consented scope carries the seeded values *and* that unconsented scopes never appear.
* **Change request → approval → history → audit** — a change request is raised through the staff-portal-api, every AWE stage is approved through the AWE proxy, AWE's HMAC-signed webhook applies the change, and the suite asserts the new value, the history row and the audit trail.

The change-request flow deliberately never calls `approve_change_request` directly — that endpoint flips the request to approved without consulting AWE, so using it would make the test pass while proving nothing about the approval policy.

## Running it

| Value | Default | Effect |
|---|---|---|
| `registry.sanity.enabled` | `true` (NSR overlay) | Create the sanity Job at all |
| `registry.sanity.runE2e` | `false` | `false` → smoke only, creates no data. `true` → the full e2e, which seeds a persistent test partner and test user |
| `registry.sanity.failOnError` | `true` | `true` → the Job propagates pytest's exit code, so a failing suite fails the install. `false` → always exit 0 (opt-out). Gates on **failures**, not skips: tests whose dependencies are unconfigured still skip and stay green |

A dependency that is **configured but broken** now fails rather than skips — a green run that had silently dropped every consent and signature test was worse than a red one.

The sanity Job runs **last**, after `db-seed` and `iam-register` — its change-request tests need the registry's roles→permissions catalog registered in IAM first, or they get a 403. Finished pods are retained so their logs stay readable:

```bash
kubectl -n <namespace> logs job/<release>-sanity
```

Output is narrated: each e2e test prints a titled banner, timestamped step lines, and a pass/fail footer, so the Job log reads as an end-to-end story rather than raw assertions.

{% hint style="warning" %}
Because the hooks are ordered, **a db-seed failure stops the chain before the sanity Job is created**. If you see no `<release>-sanity` Job at all, check `db-seed` first — the release will be in `failed` state.
{% endhint %}

{% hint style="warning" %}
The e2e seeds a **shared, persistent** test partner in Partner Management and a binding in Consent Manager, and provisions a `sanity-e2e` Keycloak user. These are deliberately left in place after a run so a failure can be inspected. Remove them explicitly when decommissioning an environment.
{% endhint %}

## Extending the tests

A change to an NSR field that the e2e asserts on — the DCI template shape, the register tables, or the edited field — means updating the corresponding Set 2 file above. Anything that is only a different id, scope or tab/section is a values change, not a code change.

---
description: >-
  The in-cluster sanity suite for the National Social Registry — inherited whole
  from the platform, and why no NSR test code is needed.
---

# Sanity testing

The National Social Registry is verified end-to-end in-cluster by a pytest suite run as a post-install/upgrade Helm Job. NSR is the one registry that inherits the **entire** suite — harness, generic tests and field tests — and contributes no test code of its own.

{% hint style="info" %}
The two-part test model — what is extension-independent, what is field-specific, and how a registry extends it — is documented once in the platform docs: [**Testing & the sanity suite**](../../registry/deployment-and-extension/testing-and-sanity-suite.md).
{% endhint %}

## Why NSR needs no field tests

The platform's **reference registry was derived from NSR** (Individual + Household, trimmed). Everything the field-specific tests depend on is therefore already the NSR's:

| What the field tests bind to | Reference registry | NSR |
|---|---|---|
| Register mnemonic and id | `Individual`, `a0000000-…-000000000001` | same |
| Register / history tables | `g2p_register_individuals`, `g2p_register_history_individuals` | same |
| DCI template shape | demographics under `demographic_info` | same (only the `@id` URI prefix differs) |
| Consent scopes | `demographic_info`, denied `member_identifier` | same |
| Change-request UI coordinates | tab `individual_info_tab`, section `in_demographic_details` | same |
| Edited field | `middle_name` (from core `G2PPerson`) | same |

So the published `openg2p/openg2p-registry-sanity-tests` image runs unchanged against an NSR deployment, and every platform sanity default in the chart is already correct. The overlay only has to switch it on:

```yaml
registry:
  sanity:
    enabled: true
```

There is no `openg2p-nsr-sanity-tests` image and no `test/` directory in the repo.

## What the e2e covers

Two flows, both against a live deployment:

* **DCI data-sharing** — the partner signs a DCI envelope and an embedded consent JWS with its Partner Management key; the registry verifies the envelope, calls Consent Manager `/validate`, renders the record through the DCI template, and clamps it to the consented scopes. The suite asserts the consented scope carries the seeded values *and* that unconsented scopes never appear.
* **Change request → approval → history → audit** — a change request is raised through the staff-portal-api, every AWE stage is approved through the AWE proxy, AWE's HMAC-signed webhook applies the change, and the suite asserts the new value, the history row and the audit trail.

## Running it

| Value | Default | Effect |
|---|---|---|
| `registry.sanity.enabled` | `true` (NSR overlay) | Create the sanity Job at all |
| `registry.sanity.runE2e` | `false` | `false` → smoke only, creates no data. `true` → the full e2e, which seeds a persistent test partner and test user |
| `registry.sanity.failOnError` | `false` | `false` → the Job exits 0 even when tests fail, so it never blocks an install. `true` → gate the deployment on it |

The sanity Job runs **last**, after `db-seed` and `iam-register` — its change-request tests need the registry's roles→permissions catalog registered in IAM first, or they get a 403. Finished pods are retained so their logs stay readable:

```bash
kubectl -n <namespace> logs job/<release>-sanity
```

{% hint style="warning" %}
The e2e seeds a **shared, persistent** test partner in Partner Management and a binding in Consent Manager, and provisions a `sanity-e2e` Keycloak user. These are deliberately left in place after a run so a failure can be inspected. Remove them explicitly when decommissioning an environment.
{% endhint %}

## If NSR's fields diverge

Should NSR's Individual register, DCI template or UI coordinates diverge from the reference, the fix is the pattern every other registry already uses: build a thin sanity image `FROM openg2p-registry-sanity-tests`, overlay the handful of field-specific files, and point `registry.sanity.image` at it. Anything that is only a different id, scope or tab/section stays a values change. See [Testing & the sanity suite](../../registry/deployment-and-extension/testing-and-sanity-suite.md).

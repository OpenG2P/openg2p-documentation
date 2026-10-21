---
description: >-
  Running the Farmer Registry's sanity suite, choosing smoke or full e2e, and
  reading the results.
---

# Sanity testing

This page lists the steps and choices. What the suite tests and how it is built: [Testing & the sanity suite](../../registry/deployment-and-extension/testing-and-sanity-suite.md) (all registries) and [Sanity tests](../README.md#sanity-tests) (what the Farmer Registry adds).

The suite runs as the Job `<release>-sanity` on every install and upgrade.

## Choose smoke or full e2e

| Choice | Form fields | Use it for |
| --- | --- | --- |
| **Smoke** (default) | **Run Sanity Tests** on, **Sanity - Run Full E2E** off | Every environment, including production. Creates nothing |
| **Full e2e** | **Sanity - Run Full E2E** on | Test environments only. Checks a signed, consented DCI search and a change request through AWE approval |

By default a failing test fails the install (**Sanity - Fail the Deploy on Test Failure**). Turn that off only where an unverified deploy is better than a failed one.

## Run the full e2e

1. Check commons-services has Partner Management, the Consent Manager and AWE running, and **Verify Partner Signature** and **Enforce Consent** are on.
2. Turn on **Sanity - Run Full E2E** and install or upgrade.
3. The install first seeds the test partner (its key and its scope policy in Partner Management, which lets it present the consents it signs), the sanity farmer `SANITY-FARMER-0001` and a `sanity-e2e` Keycloak user ([Install sequence](data-seeding.md#install-sequence)), then runs the suite.

{% hint style="warning" %}
The e2e's test data is **never deleted**: the test partner in Partner Management (`PARTNER_CM_SANITY`, its key and its access policy), the sanity farmer and the Keycloak user stay for inspection. An environment that has once run the e2e keeps them. Disable the partner in Partner Management when you decommission the environment.
{% endhint %}

## Read the results

```bash
kubectl -n <namespace> logs job/<release>-sanity
```

The finished pod is kept, so the log stays readable until the next run. Each e2e test prints a titled banner, timestamped steps and a pass or fail line.

* A test that **skips** had a dependency that is not configured (e.g. no commons-services yet). Skips do not fail the install.
* A test that **fails** had a configured dependency that is broken. Check that service first.
* No `<release>-sanity` Job at all means an earlier Job failed. See [Install sequence](data-seeding.md#install-sequence).

## When a farmer field changes

A change to what the e2e checks (the farmer DCI template, the farmer tables, or the field the change request edits) means updating the matching file in [`test/sanity`](https://github.com/OpenG2P/farmer-registry/tree/develop/test/sanity) ([which files](../README.md#sanity-tests)). A different register, scope, tab or section is a change to the chart's `registry.sanity.*` values, not to code.

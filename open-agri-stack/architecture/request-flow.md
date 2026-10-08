---
description: >-
  One request through Agri Stack, end to end: a bank asks for a farmer's
  credit profile held across three registries.
---

# Request Flow

The worked example is **Access to Credit**: a bank wants a farmer's credit profile, and the data comes from three registries.

<figure><img src="../../.gitbook/assets/open-agri-stack-request-flow.svg" alt="Sequence: bank → ingress → composite, which checks the bank's association with the policy → three registries; each registry validates its grant in the one consent with CM; the livestock registry times out"><figcaption><p>One request, end to end</p></figcaption></figure>

In this example the livestock registry is down. The bank still gets the farmer and crop data, and the response says `livestock: unavailable` rather than failing the whole request.

## Steps

1. **Bank → ingress.** The bank calls the `credit-profile` use case with the farmer's identifier and the consent, and signs the request with its PM key.
2. **Ingress → composite.** The OpenG2P deployment's ingress (Nginx, Istio) routes the request to the composite, which verifies the bank's signature. There is no separate API gateway (see [entry point](README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)).
3. **Composite → PM.** The composite checks that the bank is associated with the policy this use case refers to (`credit-assessment`).
4. **Composite → registries.** The composite sends a DCI `sync/search` to each source in parallel. Each call is signed with the composite's own PM key and carries the bank's consent and original request ID unchanged.
5. **Registry → CM.** Each registry calls CM `/validate`.
6. **CM → PM.** CM checks the consent, fetches that registry's policy section from PM (cached), and returns the effective scopes.
7. **Registries → composite.** Each registry releases only the effective fields and returns a status: `ok`, `no_record`, `denied` or `unavailable`.
8. **Composite → bank.** The composite assembles the response, returns it and discards everything. Every hop emits audit events linked by the request ID, and CM records the usage so the farmer can see it.

{% hint style="info" %}
Steps 4–6 pass the **same** consent to every registry, and each registry validates only its own grant in it (see [consent model](consent-model.md)).
{% endhint %}

## How this differs in the first version

The [composite as built](../implementation/composite.md) follows this flow with these differences:

* The policy association (step 3) is checked against the use case's `allowed_partners`, a stand-in until PM holds policies.
* Policies are still held in CM, per partner binding and registry; CM does not read them from PM (step 6).
* The composite calls sources in dependency order: in `loan-profile` the Crop Sown Registry is called after the Farmer Registry, because it needs the farmer ID that the Farmer Registry returns.

## Use-case (composite) configuration

The `credit-profile` use case is defined by a configuration file loaded by the generic composite service. The file covers sources, query templates, response mapping, timeouts and the checks run before publishing. See [use-case composite](../design/use-case-composite.md) and the [composite configuration guide](../guides/composite-configuration.md).

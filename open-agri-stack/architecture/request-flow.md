---
description: >-
  One request through Agri Stack at query time, end to end: a bank asks the
  composite for a farmer's loan profile, the exchange Consent Manager issues a
  consent token per registry, and each registry checks its consent token at its own
  Consent Manager.
---

# Request Flow

The farmer has already given the bank consent, as in [consent scenarios](consent-scenarios.md). This page follows what happens when the bank uses it.

The worked example is path B ([architecture](README.md#components-and-who-talks-to-whom)) in **exchange mode**, the composite's default: a bank asks for a farmer's `loan-profile@1`, with data from the Farmer Registry (Agriculture Department) and the Crop Sown Registry (Crops Department).

<figure><img src="../../.gitbook/assets/open-agri-stack-request-flow.svg" alt="Sequence, path B in exchange mode: the bank's signed query with its consent reaches the composite through the Agriculture Department's ingress; the composite checks the bank's signature against the exchange PM, then asks the exchange CM for one consent token per registry; it searches the Farmer Registry with its consent token, which the Farmer Registry checks at its own CM; then the Crop Sown Registry in the Crops Department, the same way; the composite returns a signed response with a status per source"><figcaption><p>One request, end to end (exchange mode)</p></figcaption></figure>

## Steps

1. **Bank → composite.** The bank's system sends a signed query for `loan-profile@1` with the farmer's identifier (national ID FAN or Farmer ID) and the consent, as either:
   * `message.consent_id`: the ID of a consent collected in the exchange CM (the usual case, [scenario 1](consent-scenarios.md)); or
   * `message.consent_jws`: a consent the bank signed itself, with one grant per registry.

   The Agriculture Department's ingress (Nginx, Istio) routes it to the composite. There is no separate API gateway (see [entry point](README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)).
2. **Composite checks the bank.** It verifies the request signature against the bank's key in the exchange's Partner Management (cached), checks the message is fresh, that the bank is in the use case's `allowed_partners`, the input and the rate limit. For a `consent_jws`, it also checks the bank's signature on the consent and that the consent grants each mandatory source's scopes.
3. **Composite → exchange CM: consent tokens.** The composite calls the exchange CM `/validate` with the consent, `issue_receipts: true` (consent tokens are called *receipts* in the API) and the use case's scopes as `requested_scopes`. The exchange CM checks the consent (active, in its validity, given for this farmer to this bank) and the bank's data-share policy, and returns one signed consent token per registry. Each token carries only the effective scopes: **use case ∩ bank's policy ∩ consent**.
4. **Composite → Farmer Registry.** A DCI `sync/search`, signed with the composite's own key, carrying the Farmer Registry's consent token and naming the bank in `header.meta.on_behalf_of`.
5. **Farmer Registry → its own CM.** The registry calls its department's CM `/validate` with the consent token. That CM verifies the token against the exchange CM's public keys (`trustedReceiptIssuers`), checks it is addressed to this registry and presented by `agri-composite`, checks its status at the exchange CM (not revoked), and intersects its scopes with its own standing policy for the composite.
6. **Farmer Registry → composite.** The registry releases only those scopes and returns the record.
7. **Composite → Crop Sown Registry.** The same, through the Crops Department's ingress, with that registry's consent token, checked at the Crops Department's CM. The composite calls it after the Farmer Registry, because it searches by the Farmer ID the Farmer Registry returned (`depends_on`).
8. **Composite → bank.** The composite maps the results, signs the response and returns it, then keeps nothing. Each source has a status: `ok`, `no_record`, `denied`, `unavailable` or `error`. Fields from a failed source are `null`. Every hop emits audit events linked by the request ID.

{% hint style="info" %}
**When a source is left out.** A mandatory source that the consent doesn't cover fails the whole request. An optional source whose scopes the consent does not grant is **not called** and is reported `denied`. An optional source whose registry is down is reported `unavailable`; the bank still gets the rest.
{% endhint %}

What each part of the use case does (sources, scopes, templates, mapping, timeouts) is in the [use-case composite design](../design/use-case-composite.md) and the [composite configuration guide](../guides/composite-configuration.md). The request and response formats are in the [partner guide](../guides/partner-guide.md).

## Variants

* **Passthrough mode (a single install).** The consent mode is a service-wide chart setting. In `passthrough` there is no exchange CM: the bank's signed `consent_jws` goes unchanged to each registry, which validates its own grant in it at its own CM. The bank must then be bound at each registry's CM. `consent_id` needs exchange mode.
* **Path A: direct to a registry.** The bank calls one registry's partner API (DCI) itself, with a consent for that registry. The registry checks the signature at its own PM and the consent at its own CM, as in step 5. No composite is involved.
* **Path C: registry to registry** is not in use today ([registry data sync](../design/registry-data-sync.md)).

## Target

Data-share policies are held in each CM today, one per partner binding and registry. In the target design they are held in Partner Management, and the composite's `allowed_partners` check becomes a check of the bank's association with the use case's policy there.

---
description: >-
  One request through Agri Stack at query time, end to end: a bank asks the
  Composite for a farmer's loan profile, the Exchange Consent Manager issues a
  consent token per registry, and each registry checks its consent token at its own
  Consent Manager.
---

# Request Flow

The farmer has already given the bank consent, as in [consent](consent.md#how-a-farmer-gives-consent). This page follows what happens when the bank uses it.

The worked example is path B ([architecture](README.md#components-and-who-talks-to-whom)) in **Exchange mode**, the Composite's default: a bank asks for a farmer's `loan-profile@1`, with data from the Farmer Registry (Agriculture Department) and the Crop Sown Registry (Crops Department).

Solid arrows are requests; dashed arrows are replies.

<figure><img src="../../.gitbook/assets/open-agri-stack-request-flow.svg" alt="Sequence, path B in Exchange mode: the bank's signed query, with a consent or none, reaches the Composite through the Agriculture Department's ingress; the Composite checks the bank's signature and its use-case grant against the Exchange PM, then asks the Exchange CM for one consent token per registry (the CM looks the consent up when the bank sent none); it searches the Farmer Registry with its consent token, which the Farmer Registry's own CM checks offline and against the department's ceiling for the Composite; then the Crop Sown Registry in the Crops Department, the same way; the Composite returns a signed response with a status per source"><figcaption><p>One request, end to end (Exchange mode)</p></figcaption></figure>

## Steps

1. **Bank → Composite.** The bank's system sends a signed query for `loan-profile@1` with the farmer's identifier (national ID FAN or Farmer ID) and one of:
   * **no consent**: the Exchange CM looks up the consent it holds (the usual case for consents collected in the partner portal, [scenario 1](consent.md));
   * `message.consent_id`: the ID of a consent held by the Exchange CM;
   * `message.consent_jws`: a consent the bank signed itself, with one grant per registry, accepted only if its use-case policy allows partner-signed consents.

   The Agriculture Department's ingress (Nginx, Istio) routes it to the Composite. There is no separate API gateway (see [entry point](README.md#api-gateway-functions)).
2. **Composite checks the bank.** It verifies the request signature against the bank's key in the Exchange's Partner Management (cached), checks the message is fresh, that the bank has a policy for `loan-profile@1` in the same Partner Management (cached), the input and the rate limit. For a `consent_jws`, it also checks the bank's signature on the consent and that the consent grants each mandatory source's scopes.
3. **Composite → Exchange CM: consent tokens.** The Composite calls the Exchange CM `/validate` with the consent (if the bank sent one), `issue_receipts: true` (consent tokens are called *receipts* in the API) and the use case's scopes as `requested_scopes`. It also sends the bank, the farmer, the use case (`loan-profile@1`) and its purpose. With no consent, the Exchange CM picks the bank's active consent for this farmer and use case (the latest-expiring one); none → the request is denied (`consent_denied`, reason `consent_not_found`). The Exchange CM checks the consent (active, in its validity, given for this farmer to this bank, for the use case's purpose) against the bank's use-case policy, read from the Exchange's Partner Management, and returns one signed consent token per registry (valid 5 minutes by default, never past the consent). Each token carries only **the use case's scopes ∩ consent** ([data-sharing policies](data-sharing-policies.md)). The response names the consent used (`message.consent_id`).
4. **Composite → Farmer Registry.** A DCI `sync/search`, signed with the Composite's own key, carrying the Farmer Registry's consent token and naming the bank in `header.meta.on_behalf_of`.
5. **Farmer Registry → its own CM.** The registry calls its department's CM `/validate` with the consent token. That CM:
   * checks the token offline: its signature against the Exchange CM's public keys (cached), issuer, that it is addressed to this registry and presented by the Composite, the farmer, and expiry. A revocation therefore takes effect within the token's short lifetime. A status call back to the Exchange CM is available as an option (off by default);
   * intersects the token's scopes with the department's ceiling, the Composite's scope policy for this registry in the department's Partner Management, and returns the result to the registry.
6. **Farmer Registry → Composite.** The registry releases only those scopes and returns the record.
7. **Composite → Crop Sown Registry.** Two DCI searches of the same registry, in parallel: the farmer's season summaries and their crop seasons, each with the Crop Sown Registry's consent token, through the Crops Department's ingress. Its CM checks the token as in step 5. The searches use the Farmer ID from the request or, if the bank sent the national ID, the one in the Farmer Registry's record. Today they always run after step 6 (`depends_on`); running them alongside the Farmer Registry search when the request already carries the Farmer ID is not built yet.
8. **Composite → Bank.** The Composite maps the results, signs the response and returns it, then keeps nothing. Each source has a status: `ok`, `no_record`, `denied`, `unavailable` or `error`. Fields from a failed source are `null`. Every hop emits audit events linked by the request ID.

{% hint style="info" %}
**When a source is left out.** A mandatory source that the consent doesn't cover fails the whole request. An optional source whose scopes the consent does not grant is **not called** and is reported `denied`. An optional source whose registry is down is reported `unavailable`; the bank still gets the rest.
{% endhint %}

What each part of the use case does (sources, scopes, templates, mapping, timeouts) is in the [Composite design](../composite/README.md) and the [Use-Case Configuration](../composite/use-case-configuration.md). The request and response formats are in the [Composite API](../composite/api.md) reference.

## Variants

* **Path A: direct to a registry.** The bank calls one registry's partner API (DCI) itself: searching the farmer by ID with no consent (the registry's CM finds the consent it holds), or with a consent it signed, if allowed. The registry checks the signature at its own PM and the consent at its own CM, against the bank's scope policy for that registry in its PM. No Composite is involved.
* **Path C: registry to registry** is not in use today ([registry data sync](../design/registry-data-sync.md)).

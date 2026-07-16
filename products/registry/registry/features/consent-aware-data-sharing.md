# Consent-Aware data sharing

The Registry shares personal data with an external partner only when a **positive
authorization decision** comes back from the dedicated **Consent Manager (CM)**
microservice. Consent logic is deliberately *not* embedded in the registry: the registry
is the **Policy Enforcement Point (PEP)**, the Consent Manager is the **Policy Decision
Point (PDP)**. The registry never interprets consent semantics, never holds partner
signing keys, and never evaluates consent policy.

{% hint style="info" %}
The full contract — consent object format, signatures, key handling, configuration and
request flow — is specified **once**, on the Consent Manager side:
[Registry integration (the PEP side)](../../../../consent-management/design/registry-integration.md).
This page covers only what the *registry* does.
{% endhint %}

## How it works

Consent travels **with the request**. A partner calling the registry's DCI search API
embeds its consent object — a compact JWS signed with the partner's own key — in the
DCI-standard `authorize` block:

```
message.search_request[i].search_criteria.authorize.consent_jws
```

The registry partner-api then:

1. **Verifies the caller** — checks the DCI envelope signature against the partner's
   public key fetched from **Partner Management**. The registry stores no partner keys.
2. **Delegates the decision** — forwards the consent JWS verbatim to the Consent
   Manager's `/validate`. CM verifies the signature against the same Partner Management
   key, evaluates the partner's data-share policy, and returns a decision plus the
   **effective data scopes** (consent scope ∩ policy).
3. **Enforces the decision** — clamps every returned record to those effective scopes.
   A narrower consent or policy can only ever *remove* fields, never add them. Any
   non-permit decision rejects the request (**fail-closed**).

CM separately records a canonical **consent artefact** and issues a signed **consent
receipt** — the audit / non-repudiation evidence. The registry keeps none of it.

## Configuration

Enforcement is governed by two **independent** switches on the partner-api. Both default
**off**, so the feature is opt-in per deployment and existing behaviour is unchanged
until you enable it:

| Switch | Effect when ON |
| --- | --- |
| **Verify Partner Signature** | verify the DCI envelope signature against Partner Management keys |
| **Enforce Consent** | call the Consent Manager and clamp returned fields to the consented scopes |

When a switch is OFF the bypass is logged and stamped into the DCI response header
`meta`, so a bypassed response can never be mistaken for an authorised one. The exact
env vars and Helm values are listed in
[Registry integration](../../../../consent-management/design/registry-integration.md#configuration-registry-partner-api).

## Related

* [Consent Management](../../../../consent-management/README.md) — the service, its design and APIs
* [Registry integration (the PEP side)](../../../../consent-management/design/registry-integration.md) — the full contract
* [Partner integration guide](../../../../consent-management/partner-integration-guide.md) — for partners: onboarding, keys, obtaining consent, signing
* [Partner APIs](../design/partner-apis.md) — the registry's DCI search API

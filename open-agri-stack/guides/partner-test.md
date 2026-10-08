---
description: >-
  Testing the composite the way a partner uses it: onboarding, access, consent
  and the query, all through the public APIs. No kubectl, no database.
---

# Partner Test (Public APIs)

[`composite/scripts/partner_test.py`](https://github.com/openg2p/agri-stack/blob/develop/composite/scripts/partner_test.py) walks through what a partner such as a bank does, using only the environment's public URLs. It runs from any machine that can reach them. Unlike the [laptop end-to-end test](end-to-end-test.md), it uses no kubectl and reads no database.

```bash
python composite/scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a
```

* **`--base-domain`:** every URL defaults to `https://<service>.<base domain>`: `agri-composite`, `partner-management-partner-api`, `pm-staff-portal` (PM's admin API), `consent-manager`, and Keycloak's staff realm. Each one can be overridden (`--composite-url`, `--pm-staff-url`, …).
* **`--partner`:** a partner the use case allows (`allowed_partners`).
* **`--fan`:** the farmer's ID, as the farmer would give it to the bank (`--subject-type FARMER_ID` for a Farmer ID). Default `946053125409`: sample person `ETH-IND-0007` of the country pack in openg2p-data, who is sample farmer `FR-0007` with land in the Farmer Registry and crop seasons in the Crop Sown Registry of any install with sample data.

## Steps

| Step | What happens |
| --- | --- |
| **1. Use case** | GET the use case from the composite: purpose, inputs, the registries the consent must grant |
| **2. Key** | The partner's signing key (EC P-256), kept in `--state-dir` (default `~/.agri-partner-test/<base domain>`) and reused |
| **3. Onboard** | The partner's key in Partner Management. **With PM admin credentials:** the script raises the onboarding (or key-update) request and waits for a PM admin to approve it in the PM portal; `--auto-approve` approves it with the same credentials. **Without:** it prints the partner ID and the public key (also written to the state directory) for a PM admin to onboard and approve. Either way it waits (`--wait`, default 30 min) until PM's public key API serves the key |
| **4. Access** | The partner's binding and policy per registry in the Consent Manager. **With CM admin credentials:** the script creates them. If the CM's optional AWE approval of policies is turned on (off by default), it waits for the approval. **Without:** it prints what a CM admin must set up and waits for Enter (`--no-prompt` skips the wait) |
| **5. Consent and query** | A consent for the farmer with a grant per registry, signed by the partner; the signed request is POSTed to the composite's public URL |
| **6. Result** | The response signature is checked against the composite's key served by PM; each source's status is printed, and the JSON is saved (git-ignored, owner-only) |

## Admin credentials (optional)

Keycloak client credentials of the staff realm, read from the environment so they never appear on a command line:

| Variable | Client (option) |
| --- | --- |
| `PM_ADMIN_CLIENT_SECRET` | `--pm-client-id`, default `commons-services-staff-portal` (role `partner_manager`) |
| `CM_ADMIN_CLIENT_SECRET` | `--cm-client-id`, default `consent-manager` (role `CONSENT_MANAGER_ADMIN`) |

With both set and `--auto-approve`, the run needs no manual step:

```bash
export PM_ADMIN_CLIENT_SECRET=… CM_ADMIN_CLIENT_SECRET=…
python composite/scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a --auto-approve --no-prompt
```

## What the operator sets up beforehand

The script covers only the partner's side. The rest is part of installing the environment, and the query fails if it is missing:

* the composite, with its signing key onboarded in PM as `agri-composite`;
* in a [distributed deployment](../design/distributed-deployment-architecture.md), each department's PM and CM set up for the composite (its key; a binding and policy for `agri-composite`), and each department CM trusting the exchange CM's receipts.

## Exit codes

`0` ok; `1` error; `2` a step was not completed (an approval timed out, or a conflict needs a decision); `3` the query failed or a source did not answer ok.

---
description: >-
  One-time operator setup of an Agri Exchange after install, with one script:
  the composite's signing key, its key in each Partner Management, and the
  composite's bindings and policies in each department Consent Manager.
---

# Exchange Setup

[`scripts/setup_exchange.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/setup_exchange.py) does the operator setup the Helm charts cannot do, once after installing the Agri Exchange and the department registries. Run it again after adding a registry, or a use case that needs new data scopes; it changes only what is missing.

Partners (e.g. a bank) are **not** set up here: they onboard through Partner Management and the Consent Manager. To test the composite as a partner, use the [partner test](partner-test.md).

## What it sets up

| Where | What |
| --- | --- |
| Exchange namespace | Secret `agri-composite-signing` (a generated `.p12`), then a restart of the composite. A Secret whose key the exchange PM already serves is left alone. |
| Exchange PM and each department PM | The composite (`PARTNER_AGRI_COMPOSITE`) with its signing key: onboarded and approved, or the key added with a key-update request and approved. Each registry checks the composite's signature at its **own** PM. |
| Each department CM (exchange consent mode) | A binding and policy for the composite (audience `agri-composite`) per registry. **Scopes and purposes come from the composite's published use cases**: per registry, the union of each use case's `consent_scopes` (required and optional) and their purposes. An existing policy is only widened, never narrowed. |
| Each department CM (checked, not set) | That it trusts the exchange CM's receipts for the composite (`global.agriStackExchange.trustedIssuer`), and that the exchange CM issues them (`issuer`, `receiptPresenters`). These are Helm values; the script names the missing one and stops. |

In passthrough consent mode the registries check each partner's own consent at their CM, so each partner needs a binding there; the script then sets up only the composite's key.

## Prerequisites

* The exchange (commons and the composite) and each department (commons and its registry) installed. See [deploying on a cluster](deployment.md).
* `kubectl` with a context that can read Deployments, Services and Secrets, port-forward, and (for the signing key) create a Secret and restart the composite in the exchange namespace. `--context` picks another context.
* Python 3 with a virtual environment:

```bash
cd agri-stack
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt     # cryptography, pyjwt, httpx
```

## Commands

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1 --dry-run
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

* **`-n`:** the exchange namespace (the composite and its commons).
* **`--registry <controller>=<namespace>`:** each registry and the namespace of the department install that serves it (repeatable). A registry the composite calls but that is not listed is reported and skipped.
* **`--dry-run`:** discover and plan with GETs only, and list the writes.
* Without `--dry-run`, every write is listed first and needs a typed `yes`; **`--yes`** skips the prompt.
* **`--new-key`:** a new composite key (new `kid`) instead of the saved one.
* **`--pm-client-id`, `--cm-client-id`:** the Keycloak admin clients (default PM's `PARTNER_MANAGER_AUTH_ADMIN_CLIENT_ID`, and `consent-manager`). Their secrets are read with kubectl into memory, never printed.

## Steps

| Step | What happens |
| --- | --- |
| **1. Discover** | The composite, PM, CM and Keycloak of the exchange and of each department, from the Deployments' environment; the receipt-trust check (exchange mode) |
| **2. Admin tokens** | Keycloak client credentials for each PM and CM; checks the admin roles |
| **3. Use cases** | The composite's published use cases (`GET /composite/v1/use-cases`) and the policy each registry needs |
| **4. Plan** | GETs only: the signing Secret, the composite in each PM, the bindings and policies in each department CM |
| **5. Apply** | After confirmation: PM requests raised and approved, CM bindings and policies, the Secret and the restart |

**Exit codes:** 0 ok, 1 error, 2 a decision is needed: a department CM does not trust the exchange's receipts, a CM policy waits for AWE approval (approve it in AWE, then rerun), a PM key conflicts (rerun with `--new-key`), or the writes were not confirmed.

## Where the key is stored

| What | Where |
| --- | --- |
| The composite's key | `~/.agri-stack-setup/<ns>/composite.p12` (0600) |
| Its `kid` and the `.p12` password | `~/.agri-stack-setup/<ns>/state.json` (0600) |
| The directory | mode 0700; `--state-dir` puts it elsewhere |

The cluster holds the same key in Secret `agri-composite-signing`; the local copy lets a rerun see that nothing changed.

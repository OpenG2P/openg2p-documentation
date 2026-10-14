---
description: >-
  One-time setup after installing Agri Stack: the partner portal's realm and
  users, and the Exchange setup script (the Composite's signing key, its key in
  each Partner Management, its bindings and policies in each department CM).
---

# After Install

Two steps the charts cannot do, run once by an operator after the [Exchange](exchange.md), the registries and the [Composite](composite.md) are installed. Partners (e.g. a bank) are **not** set up here: they onboard through Partner Management and the Consent Manager ([partner guide](../partner-guide.md)).

| Step | Needed for | Rerun |
| --- | --- | --- |
| [Partner portal realm and users](#partner-portal-realm-and-users) | Consent collected in the partner portal | For each new partner user |
| [Exchange setup](#exchange-setup) | Every query: without it no PM knows the Composite, partners cannot verify its answers and the registries refuse its calls | After adding a registry, or a use case with new data scopes or purposes |

## Partner portal realm and users

Partner users (e.g. bank staff) log in to the Consent Manager's partner portal through a Keycloak realm `partner`. The chart creates the realm and the portal's client; the roles, the `partner_id` attribute, its token mapper and the partner users need Keycloak's admin CLI. From the [consent-manager](https://github.com/OpenG2P/consent-manager) repository:

```bash
./deployment/scripts/setup-partner-realm.sh --namespace agrix --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

The user's password is in the Secret `partner-user-bank-a-operator` in the namespace. A user's `partner_id` (here `bank-a`) must be the partner's ID as bound in the Exchange CM. See [partner portal and consent evidence](../../consent-management/deployment/README.md#partner-portal-and-consent-evidence-optional).

## Exchange setup

[`scripts/setup_exchange.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/setup_exchange.py) does the operator setup for the Composite. It changes only what is missing, so a rerun is safe.

### What it sets up

| Where | What |
| --- | --- |
| Exchange namespace | Secret `agri-composite-signing` (a generated `.p12`), then a restart of the Composite. A Secret whose key the Exchange PM already serves is left alone |
| Exchange PM and each department PM | The Composite (`PARTNER_AGRI_COMPOSITE`) with its signing key: onboarded and approved, or the key added with a key-update request and approved. Each registry checks the Composite's signature at its **own** PM |
| Each department CM | A binding and policy for the Composite (audience `agri-composite`) per registry. **Scopes and purposes come from the Composite's published use cases**: per registry, the union of each use case's `consent_scopes` (required and optional) and their purposes. An existing policy is only widened, never narrowed |
| Each department CM and the Exchange CM (checked, not set) | That each department CM trusts the Exchange CM's consent tokens for the Composite (**Exchange Role** `department`), and that the Exchange CM issues them (**Exchange Role** `exchange`). These are form choices; the script names the missing one and stops |

### Prerequisites

* The Exchange (commons and the Composite) and each department (commons and its registry) installed.
* `kubectl` with a context that can read Deployments, Services and Secrets, port-forward, and (for the signing key) create a Secret and restart the Composite in the Exchange namespace. `--context` picks another context.
* **One cluster.** The script uses one kubectl context for the Exchange and every department. It reaches a department only in the Exchange's cluster, as when all three namespaces run on one cluster for testing. A department on its own cluster (the Crops Department in the [topology](README.md#topology)) is set up by hand: [Separate Clusters](separate-clusters.md#the-composite-in-a-department-on-another-cluster).
* Python 3 with a virtual environment:

```bash
cd agri-stack
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt     # cryptography, pyjwt, httpx
```

### Commands

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1 --dry-run
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

| Option | Meaning |
| --- | --- |
| `-n` | The Exchange namespace (the Composite and its commons) |
| `--registry <controller>=<namespace>` | Each registry and the namespace of the department install that serves it (repeatable). A registry the Composite calls but that is not listed is reported and skipped |
| `--dry-run` | Discover and plan with GETs only, and list the writes |
| `--yes` | Make the listed writes without the typed `yes` |
| `--new-key` | A new Composite key (new `kid`) instead of the saved one |
| `--pm-client-id`, `--cm-client-id` | The Keycloak admin clients (default PM's `PARTNER_MANAGER_AUTH_ADMIN_CLIENT_ID`, and `consent-manager`). Their secrets are read with kubectl into memory, never printed |
| `--state-dir` | Where the Composite's key is kept (below) |

### Steps

| Step | What happens |
| --- | --- |
| Discover | The Composite, PM, CM and Keycloak of the Exchange and of each department, from the Deployments' environment; the consent-token trust check |
| Admin tokens | Keycloak client credentials for each PM and CM; checks the admin roles |
| Use cases | The Composite's published use cases (`GET /composite/v1/use-cases`) and the policy each registry needs |
| Plan | GETs only: the signing Secret, the Composite in each PM, the bindings and policies in each department CM |
| Apply | After confirmation: PM requests raised and approved, CM bindings and policies, the Secret and the restart |

**Exit codes:** `0` ok; `1` error; `2` a decision is needed: a department CM does not trust the Exchange's consent tokens, a CM policy waits for AWE approval (approve it in AWE, then rerun), a PM key conflicts (rerun with `--new-key`), or the writes were not confirmed.

### Where the key is stored

| What | Where |
| --- | --- |
| The Composite's key | `~/.agri-stack-setup/<ns>/composite.p12` (0600) |
| Its `kid` and the `.p12` password | `~/.agri-stack-setup/<ns>/state.json` (0600) |
| The directory | Mode 0700; `--state-dir` puts it elsewhere |

The cluster holds the same key in the Secret `agri-composite-signing`; the local copy lets a rerun see that nothing changed. To use your own key instead of a generated one: [Composite: signing key](composite.md#signing-key).

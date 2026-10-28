---
description: >-
  One-time setup after installing the registries and the Exchange: partner
  portal users, and the Exchange setup (the Composite's signing key and its
  access in each Partner Management), by script or by hand.
---

# After Install

Step 3 of the [install order](README.md#install-order), run once by an operator. Partners themselves (e.g. a bank) are not set up here: they are onboarded in the Exchange's Partner Management ([Managing Partners](../managing-partners.md)).

| Step | Needed for | Rerun |
| --- | --- | --- |
| [Partner portal users](#partner-portal-users) | Consent collected in the partner portal | For each new partner user |
| [Exchange setup](#exchange-setup) | Every query | After adding a registry, or a use case with new data scopes or purposes |

## Partner portal users

Partner staff log in to the partner portal through the Keycloak realm `partner`. The chart creates the realm; this script adds its roles and the users. From the [consent-manager](https://github.com/OpenG2P/consent-manager) repository:

```bash
./deployment/scripts/setup-partner-realm.sh --namespace agrix --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

The user's password is in the Secret `partner-user-bank-a-operator`. The middle part (`bank-a`) is the partner's ID; its Partner Management entry is `PARTNER_BANK_A`. More: [partner portal and consent evidence](../../consent-management/deployment/README.md#partner-portal-and-consent-evidence-optional).

## Exchange setup

The Composite needs a signing key, and an entry with that key in the Exchange's and each department's Partner Management, with a scope policy per registry in the department (what that department releases to the Exchange). Until then queries fail with `signing_unavailable`.

### By script

[`scripts/setup_exchange.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/setup_exchange.py) does all of it when one `kubectl` context reaches every namespace (as in the [reference topology](README.md#topology)). It changes only what is missing, so a rerun is safe. From the [agri-stack](https://github.com/openg2p/agri-stack) repository:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1 --dry-run
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

| What it does | Where |
| --- | --- |
| Creates the Secret `agri-composite-signing` (a generated key) and restarts the Composite; keeps a Secret whose key the Exchange PM already serves | Exchange namespace |
| Onboards the Composite (`PARTNER_AGRI_COMPOSITE`) with its key, or adds the key; raises and approves the requests | Exchange PM and each department PM |
| Adds the Composite's scope policy for each registry, covering the scopes and purposes of all published use cases; only ever widens it | Each department PM |
| Checks that each department CM has **Exchange Role** `department` and the Exchange CM `exchange`; names the missing one and stops | All CMs |

| Option | Meaning |
| --- | --- |
| `-n` | The Exchange namespace |
| `--registry <controller>=<namespace>` | Each registry and its department's namespace (repeatable) |
| `--dry-run` | Plan with reads only, and list the writes |
| `--yes` | Make the writes without the typed `yes` |
| `--new-key` | A new Composite key (new `kid`) |
| `--context` | Another `kubectl` context |
| `--state-dir` | Where the key is kept locally (default `~/.agri-stack-setup/<ns>/`, mode 0700) |

Exit code `2` means a decision is needed: the message says which (a CM role, an open Partner Management request to approve or reject, a key conflict, or the writes not confirmed).

### By hand

When the script cannot reach a department (another cluster), or each organisation does its own part:

| # | Who | What |
| --- | --- | --- |
| 1 | Exchange | Create the Composite's key |
| 2 | Exchange | Onboard the Composite in the Exchange PM |
| 3 | Each department | Onboard the Composite in its PM, with a scope policy per registry |
| 4 | Exchange | Create the Secret and restart the Composite |

**1. Key.** An EC P-256 key in a password-protected `.p12`, and a `kid` you choose:

```bash
openssl ecparam -name prime256v1 -genkey -noout -out composite.key
openssl req -new -x509 -key composite.key -subj "/CN=agri-composite" -days 365 -out composite.crt
openssl pkcs12 -export -inkey composite.key -in composite.crt -name agri-composite -out composite.p12
openssl ec -in composite.key -pubout -out composite.pub.pem
```

Keep `composite.p12` and its password in your secrets store and delete `composite.key`.

**2. Exchange PM.** In `https://partner-management.agrix.openg2p.org`, **Onboard partner**: ID `PARTNER_AGRI_COMPOSITE`, the public key from `composite.pub.pem`, the `kid`, algorithm `ES256`, no policy. Approve it.

**3. Each department PM.** **Onboard partner** `PARTNER_AGRI_COMPOSITE` with the same key and `kid`, and a **scope policy** for each registry there:

| Field | Value |
| --- | --- |
| Data controller | The registry, e.g. `farmer-registry` |
| Data scopes | Every scope the published use cases read from it: `consent_scopes` in `GET /composite/v1/use-cases` |
| Purposes | Those use cases' purposes |
| Subject ID types | e.g. `FAYDA_FAN`, `FARMER_ID` |
| Signing algorithms | `ES256` |
| Maximum validity, Fetch type | e.g. `P90D`, `oneshot` |

Approve it. Steps in the portal: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md).

**4. Secret and restart.**

```bash
kubectl -n agrix create secret generic agri-composite-signing \
  --from-file=composite.p12=./composite.p12 --from-literal=password='<p12 password>' \
  --from-literal=kid=<kid> --from-literal=algorithm=auto
kubectl -n agrix rollout restart deploy/agri-composite-api
```

### Check

* Composite console, **Registries**: each registry reachable and the Composite's key served.
* A test partner's query: [Testing](testing.md).

### When use cases change

A new use case, or one that reads more scopes or another registry, needs each department's scope policy for the Composite widened: rerun the script, or **Edit** the policy in that department's PM (**Add policy** for a new registry). Until then the registry refuses what the policy does not cover. Narrowing is always done by hand.

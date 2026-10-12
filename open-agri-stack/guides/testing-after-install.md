---
description: >-
  Testing the composite once Agri Stack is installed: the one-time exchange
  setup, then a partner's query end to end, then a consent the farmer gave
  through the partner portal. In order, with the commands.
---

# Testing After Install

The order to follow once the exchange (e.g. `agrix`) and the department registries (e.g. `trial`, `dept1`) are installed ([deploying on a cluster](deployment.md)). Steps 1 and 2 are one-time operator setup; steps 3 and 4 are the test.

| # | Step | Who | Once or each test |
| --- | --- | --- | --- |
| 1 | [Exchange setup](#id-1.-exchange-setup) | Operator (kubectl) | Once, and after adding a registry or a use case with new scopes |
| 2 | [Partner portal realm](#id-2.-partner-portal-realm) (only to test consent through the portal) | Operator (kubectl) | Once |
| 3 | [Partner test](#id-3.-partner-test) | Anyone (public URLs) | Each test |
| 4 | [Consent through the partner portal](#id-4.-consent-through-the-partner-portal) (optional) | Partner user, CM staff | Each test |

Before starting, check that every pod in each namespace is running and the releases are `deployed` (not `failed`):

```bash
helm -n agrix list
```

```bash
kubectl -n agrix get pods
```

Prepare the scripts once:

```bash
cd agri-stack
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
```

## 1. Exchange setup

**Why:** the composite signs its calls to the registries and its answers to partners. The charts install the composite but cannot register its key with anyone, so until this step no Partner Management knows the composite: partners cannot verify its answers, and the registries refuse its calls. In an exchange deployment each department's Consent Manager must also accept the composite as the presenter of the exchange's consent receipts.

[`setup_exchange.py`](exchange-setup.md) does it with kubectl, idempotently: the composite's signing key (Secret and restart), the composite in the exchange PM and each department PM, a binding and policy for the composite in each department CM (scopes from the published use cases), and a check that each department CM trusts the exchange CM's receipts.

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1 --dry-run
```

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

The dry run lists what is missing; the second command makes the changes after a typed `yes`. Exit code 2 means a decision is needed (e.g. a department CM does not trust the exchange's receipts: the message names the Helm value to set).

## 2. Partner portal realm

**Why:** partner users (e.g. bank staff) log in to the Consent Manager's partner portal through a Keycloak realm `partner`. The chart creates the realm and the portal's client; the roles, the `partner_id` attribute, its token mapper and the partner users need Keycloak's admin CLI. Only needed for step 4.

```bash
./deployment/scripts/setup-partner-realm.sh --namespace agrix --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

Run it from the consent-manager repository. The user's password is in Secret `partner-user-bank-a-operator` in the namespace. See [partner portal and consent evidence](../../consent-management/deployment/README.md#partner-portal-and-consent-evidence-optional).

## 3. Partner test

**Why:** it does what a partner (here `bank-a`) does, through public URLs only: gets onboarded in PM, gets a binding and policy per registry in the CM, signs a consent and the request, calls the use case and checks the composite's signature. See [partner test](partner-test.md).

With the PM and CM admin credentials it needs no manual step (without them, it prints what a PM admin must onboard and waits):

```bash
export PM_ADMIN_CLIENT_SECRET=$(kubectl -n agrix get secret commons-services-staff-portal -o jsonpath='{.data.client_secret}' | base64 -d)
```

```bash
export CM_ADMIN_CLIENT_SECRET=$(kubectl -n agrix get secret consent-manager -o jsonpath='{.data.client_secret}' | base64 -d)
```

```bash
python scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a --auto-approve
```

**Success:** HTTP 200, each source `ok`, and the response signature verified. The farmer defaults to the sample farmer every demo install has (`--fan` for another).

## 4. Consent through the partner portal

**Why:** in step 3 the partner signs the consent itself. Here the farmer's consent is collected in person and verified by CM staff, and the query carries only its ID.

1. Partner portal (`https://consent-partner-portal.<base domain>`), as `bank-a-operator`: **New request** (or from the use case), the farmer's ID, upload the signed form, **Submit**.
2. CM console (`https://consent-manager.<base domain>`), **Consent verifications**: a staff user approves it. Note the consent ID.
3. Query with it:

```bash
python scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a --consent-id <consent ID>
```

## Where to look

* **Composite console** (`https://agri-composite-console.<base domain>`): each call, its partner, sources and status ([composite console](composite-console.md)).
* **CM console:** the decision log of each consent check.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| The partner test waits for PM approval and the PM portal shows no request | No `PM_ADMIN_CLIENT_SECRET`: the script raised no request, it waits for a PM admin to onboard the partner by hand | Set the credentials (step 3), or onboard `PARTNER_<ID>` in the PM portal with the printed key |
| Response signature not verified, or registries answer 401 | The composite is not in PM (step 1 not run) | Run step 1 |
| Sources `denied` for consent | The department CM has no binding or policy for the composite, or does not trust the exchange's receipts | Rerun step 1 and fix what it reports |
| The composite API restarts at start | A setting it cannot read (the log names it) | Check the release's values; see [composite configuration](composite-configuration.md) |

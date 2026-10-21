---
description: >-
  Testing Agri Stack once installed: the one-time setup, a partner's query end
  to end through public APIs (the partner test), then a consent the farmer gave
  through the partner portal. In order, with the commands and common failures.
---

# Testing

The order to follow once the Exchange (`agrix`) and the department registries (`trial`, `dept1`) are installed ([Deployment](README.md)). The first two steps are the one-time [After Install](after-install.md) setup; the last two are the test.

| # | Step | Who | Once or each test |
| --- | --- | --- | --- |
| 1 | [Exchange setup](#exchange-setup) | Operator (kubectl) | Once, and after adding a registry or a use case with new scopes |
| 2 | [Partner portal realm](#partner-portal-realm) (only to test consent through the portal) | Operator (kubectl) | Once |
| 3 | [Partner test](#partner-test-public-apis) | Anyone (public URLs) | Each test |
| 4 | [Consent through the partner portal](#consent-through-the-partner-portal) (optional) | Partner user, CM staff | Each test |

Before starting, check that every pod in each namespace is running and the releases are `deployed` (not `failed`):

```bash
helm -n agrix list
kubectl -n agrix get pods
```

Prepare the scripts once:

```bash
cd agri-stack
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
```

**In one shot:** [`scripts/exchange_test.sh`](https://github.com/openg2p/agri-stack/blob/develop/scripts/exchange_test.sh) runs step 1 (a rerun changes nothing already in place), reads the PM admin client secret from the cluster, and runs step 3 with `--auto-approve`:

```bash
./scripts/exchange_test.sh --namespace agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

The whole run is saved to `scripts/out/exchange-test-<namespace>-<time>.log` (git-ignored), next to the response JSON. `--dry-run` plans step 1 only; `--setup-only` / `--test-only` run one part; `--use-case <name>` and `--fan <ID>` pick the use case and farmer to test; `--consent-id <ID>` queries with a consent collected in the partner portal for that use case (step 4). If the run onboarded the partner or changed its policy, the query is retried for up to 90 s while the Composite and the Exchange CM still hold PM's earlier answer in their caches. The steps one by one follow.

## Exchange setup

The Composite signs its calls to the registries and its answers to partners. Until this step no Partner Management knows the Composite: partners cannot verify its answers, and the registries refuse its calls. Each department's PM must also hold the Composite's scope policy for its registry, and each department CM must accept the Composite as the presenter of the Exchange's consent tokens.

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1 --dry-run
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

The dry run lists what is missing; the second command makes the changes after a typed `yes`. Exit code 2 means a decision is needed (e.g. a department CM does not trust the Exchange's consent tokens: the message names the form field). Details: [Exchange setup](after-install.md#exchange-setup).

## Partner portal realm

Only needed for step 4. From the consent-manager repository:

```bash
./deployment/scripts/setup-partner-realm.sh --namespace agrix --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

The user's password is in the Secret `partner-user-bank-a-operator`. Details: [partner portal realm and users](after-install.md#partner-portal-realm-and-users).

## Partner test (public APIs)

[`scripts/partner_test.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/partner_test.py) does what a partner (here `bank-a`) does, using only the environment's public URLs: gets onboarded in the Exchange PM with a policy for the use case, signs a consent and the request, calls the use case and checks the Composite's signature. It runs from any machine that can reach those URLs, with no kubectl and no database.

With the PM admin credentials it needs no manual step:

```bash
export PM_ADMIN_CLIENT_SECRET=$(kubectl -n agrix get secret commons-services-staff-portal -o jsonpath='{.data.client_secret}' | base64 -d)
python scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a --auto-approve
```

**Success:** HTTP 200, each source `ok`, and the response signature verified.

| Option | Meaning |
| --- | --- |
| `--base-domain` | Every URL defaults to `https://<service>.<base domain>`: `agri-composite`, `partner-management-partner-api`, `pm-staff-portal` (PM's admin API), `partner-management` (PM's portal), and Keycloak's staff realm. Each can be overridden (`--composite-url`, `--pm-staff-url`, …) |
| `--partner` | The partner's ID, e.g. `bank-a` (in PM `PARTNER_BANK_A`). The script sets up its policy for the use case under test |
| `--fan` | The farmer's ID, as the farmer would give it to the bank (`--subject-type FARMER_ID` for a Farmer ID). Default `946053125409`: sample person `ETH-IND-0007` of the shipped Ethiopia country pack, who is sample farmer `FR-0007` with land in the Farmer Registry and crop seasons in the Crop Sown Registry of any install with sample data |
| `--consent-id` | Query with a consent the Exchange CM holds ([step 4](#consent-through-the-partner-portal)) |
| `--auto-approve` | Approve the PM requests with the same admin credentials |
| `--wait` | How long to wait for a manual approval (default 30 min) |

### Steps

| Step | What happens |
| --- | --- |
| Use case | GET the use case from the Composite: its `name@major` (e.g. `loan-profile@1`), purpose, inputs, the registries the consent must grant |
| Key | The partner's signing key (EC P-256), kept in `--state-dir` (default `~/.agri-partner-test/<base domain>`) and reused |
| Onboard | The partner in the Exchange's Partner Management: its key, and its policy for the use case in the same onboarding request. **With PM admin credentials:** the script raises the onboarding (or key-update) request and waits for a PM admin to approve it in the PM portal; `--auto-approve` approves it with the same credentials. **Without:** it prints the partner ID, the public key (also written to the state directory) and the policy for a PM admin to onboard and approve. Either way it waits until PM's public key API serves the key |
| Access | The partner's policy for the use case in the Exchange PM (one policy per use case). An already onboarded partner without it gets a policy request adding it (an existing one is only widened, never narrowed; other use cases' policies are untouched), approved as above; without PM admin credentials the script prints the policy for a PM admin. Either way it waits until PM's policy API serves it. [Access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies) |
| Consent and query | A consent for the farmer with a grant per registry, signed by the partner; the signed request is POSTed to the Composite's public URL |
| Result | The response signature is checked against the Composite's key served by PM; each source's status is printed, and the JSON is saved (git-ignored, owner-only) |

### Admin credentials

Keycloak client credentials of the staff realm, read from the environment so they never appear on a command line:

| Variable | Client (option) |
| --- | --- |
| `PM_ADMIN_CLIENT_SECRET` | `--pm-client-id`, default `commons-services-staff-portal` (role `partner_manager`) |

### What the operator sets up beforehand

The script covers only the partner's side. The rest is part of the install, and the query fails if it is missing: the Composite with its signing key onboarded in PM as `agri-composite`; the Composite's key and scope policy per registry in each department's PM; each department CM trusting the Exchange CM's consent tokens. The [Exchange setup](#exchange-setup) does all of it.

### Exit codes

`0` ok; `1` error; `2` a step was not completed (an approval timed out, or a conflict needs a decision); `3` the query failed or a source did not answer ok.

## Consent through the partner portal

In the partner test the partner signs the consent itself. Here the farmer's consent is collected in person and verified by CM staff, and the query carries only its ID.

1. Partner portal (`https://consent-partner-portal.<base domain>`), as `bank-a-operator`: **New request**, picking the use case to test (`loan-profile@1`; only use cases granted to `bank-a` in PM are offered), with the farmer's national ID (`FAYDA_FAN`, e.g. `946053125409`) and Farmer ID (e.g. `FR-0007`). On the request, **Authenticate with national ID**: the farmer logs in with eSignet in the popup (a one-time code to their registered phone). Upload the signed form, **Submit**.
2. CM console (`https://consent-manager.<base domain>`), **Consent verifications**: a staff user checks the form, that the person was authenticated, and the Farmer ID in the Farmer Registry (ticking that they did), and approves it. Note the consent ID. Back in the partner portal, the consent's **Download consent record** gives the bank its own copy (receipt, signed form and the CM's signed statement).
3. Query with it:

```bash
python scripts/partner_test.py --base-domain agrix.openg2p.org --partner bank-a --fan <the consent's FAN> --consent-id <consent ID>
```

The query then carries `message.consent_id`. The Exchange CM checks the consent (active, in its validity, obtained by this partner, about this farmer, made for this use case) and what it grants, and the registries get consent tokens as before. See [consent collection](../../consent-management/design/consent-collection.md).

## Where to look

* **Composite console** (`https://agri-composite-console.<base domain>`): each call, its partner, sources and status ([Composite console](../composite/console.md)).
* **CM console:** the decision log of each consent check.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| The partner test waits for PM approval and the PM portal shows no request | No `PM_ADMIN_CLIENT_SECRET`: the script raised no request, it waits for a PM admin to onboard the partner by hand | Set the credentials, or onboard `PARTNER_<ID>` in the PM portal with the printed key |
| Every query fails with `signing_unavailable` | The Composite has no signing key Secret | Run the [Exchange setup](#exchange-setup) |
| Response signature not verified, or registries answer 401 | The Composite is not in PM | Run the [Exchange setup](#exchange-setup) |
| The query fails with 403 `partner_not_allowed` | The partner has no policy for the use case (`name@major`) in the Exchange PM | Rerun the partner test with PM admin credentials, or **Add policy** for the use case on the partner in the PM portal |
| The query fails with 503 `partner_policy_unavailable` | The Composite cannot read Partner Management and has no cached answer | Check the Exchange PM's partner API |
| Sources `denied` for consent | The department PM has no scope policy for the Composite covering the use case, or the department CM does not trust the Exchange's consent tokens | Rerun the Exchange setup and fix what it reports |
| The Composite API restarts at start | A setting it cannot read (the log names it) | Check the release's values: [Composite](composite.md#environment-settings) |

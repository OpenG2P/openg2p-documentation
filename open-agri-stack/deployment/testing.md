---
description: A basic end-to-end sanity test.
---

# Testing

Step 4 of the [install steps](README.md#install-steps). [`scripts/test_install.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/test_install.py) (in the [agri-stack](https://github.com/openg2p/agri-stack) repository) is a **basic end-to-end sanity check**: one test partner makes one query for one farmer through every registry of a use case, and the script checks the answer and its signature. If it passes, the install is wired together.

It is not a tool for running Agri Stack: real partners, consents, policies and keys are handled by hand, by the administrators ([Administration](../administration/README.md)). To pass, it sets up what it needs for its own test partner; on an install that will go live, [clean up](#clean-up) after it.

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
cp scripts/test_install.yaml my-install.yaml       # then edit: your namespaces, domains, registries
python scripts/test_install.py --config my-install.yaml --dry-run
python scripts/test_install.py --config my-install.yaml
```

`--dry-run` checks the install and lists what the script would set up, writing nothing. **Success:** HTTP 200, each source `ok`, and the response signature verified. The answer is saved in `scripts/out/` (git-ignored, owner-only: it holds a farmer's data); `--print` also prints it.

It needs Python 3, the hostnames of the installs, and the admin credentials: read with `kubectl` from the Secrets the configuration names, or from environment variables.

## Configuration

[`scripts/test_install.yaml`](https://github.com/openg2p/agri-stack/blob/develop/scripts/test_install.yaml) is the reference install's file, with every field commented. Nothing about namespaces, releases or service names is fixed in the script.

| Section | What it names |
| --- | --- |
| `kube_context` | The `kubectl` context to read Secrets with; empty = the current one |
| `exchange` | The Exchange's `namespace` and `domain`; the Composite's URL and partner ID; its Partner Management's URLs and admin client; the partner portal's Keycloak (for the portal user) |
| `registries` | Each registry the use case reads: its data controller ID, and its department's `namespace` and `domain` (and Partner Management, as for the Exchange) |
| `test` | The test partner, the use case, the farmer (`subject`), the parameters, how the consent is given, and whether the script approves its own requests |

**Hostnames** default from each install's `domain`, as the charts name them: `agri-composite.<domain>`, `pm-staff-portal.<domain>` (Partner Management's admin API), `partner-management-partner-api.<domain>`, `keycloak.<domain>`. Set a URL only where yours differ.

**Credentials** are each a Secret (`secret`, `key`, and `namespace`, by default the section's) or an environment variable (`env`, used when set). Across clusters, where one `kubectl` context does not reach every install, use `env`. They are never printed.

| Credential | Default |
| --- | --- |
| Each Partner Management's admin client | Client `commons-services-staff-portal` (role `partner_manager`), secret in Secret `commons-services-staff-portal` key `client_secret` |
| The Exchange's Keycloak admin (portal user only) | User `admin`, password in Secret `commons-keycloak` key `admin-password` |

## What it does

| # | Step | What happens |
| --- | --- | --- |
| 1 | Install | Reads the use case from the Composite (its registries, scopes, purpose) and the Composite's public key; checks that each department's Partner Management serves that key. Read only |
| 2 | Departments | In each department the use case reads, makes sure the Composite's scope policy covers what the use case asks: raises a policy request if not (widening, never narrowing), approves it, waits until Partner Management serves it |
| 3 | Partner key | The test partner's signing key (EC P-256), kept in `test.state_dir` (default `~/.agri-stack-test/<Exchange domain>`) and reused |
| 4 | Partner | Onboards the test partner in the Exchange's Partner Management with its key and its policy for the use case (allowing partner-signed consents when the script signs one), or adds what is missing; approves; waits until served |
| 5 | Portal user | With `exchange.partner_portal.enabled`: user `<partner>-operator` in the realm `partner`, password kept in Secret `partner-user-<partner>-operator` |
| 6 | Query | A consent for the farmer with a grant per registry, the signed query to the Composite, and the response signature checked against the Composite's key served by Partner Management |

With `test.auto_approve: false`, the script raises the requests and waits (`test.wait_seconds`) for an administrator to approve them in Partner Management, as in production.

**Exit codes:** `0` ok; `1` error; `2` a step was not completed (an approval timed out, or a conflict needs a decision); `3` the query failed or a source did not answer ok.

## Sample data

The registries' sample data describe the same people: person `ETH-IND-0007` is farmer `FR-0007` with lands `LAND-0007-1`, `LAND-0007-2`…, and the Crop Sown Registry's sample crop seasons are for those farmers and plots, so a `loan-profile` query returns both for the same farmer. They match only by convention (`FR-<n>`, `LAND-<n>-<k>`): a change to either registry's sample IDs must be made in both. The mock identity system at the Exchange holds the same people, so a sample farmer can log in with their national ID in the partner portal. Details: [Farmer Registry](../../products/registry/farmer-registry/deployment/data-seeding.md#sample-data), [Crop Sown Registry](../../products/registry/crop-sown-registry/deployment/rancher.md#sample-data).

## A consent collected by hand

By default the script signs the consent as the test partner (`test.consent: sign`): the partner-signed path, the less common one, used because it needs no person ([two ways a consent reaches the Exchange](../architecture/consent.md#two-ways-a-consent-reaches-the-exchange)). `test.consent: lookup` tests the main path. That consent is sent with the query and stored by the Exchange CM, but it was not collected in the partner portal, so the portal's **Consents** list does not show it: its use is in the Exchange CM console under **Access Log** (role `CONSENT_MANAGER_ADMIN`; partner `bank-a`, one entry per registry, with the consent ID; open it from there). To test with a consent collected in the partner portal instead, first collect it ([Collecting a Consent](../administration/collecting-a-consent.md)), then run the script with `test.consent: lookup` (or `id:<consent ID>`) and `test.subject` that farmer.

## Where to look

* **Composite console** (`https://agri-composite-console.<Exchange domain>`): each call, its partner, sources and status ([Composite console](../composite/console.md)).
* **CM console:** the decision log of each consent check.

## Clean up

On an install that will go live, remove what the test created:

* The test partner in the Exchange's Partner Management (`test.partner`, e.g. `PARTNER_BANK_A`): **Disable** it ([Managing Partners](../administration/managing-partners.md#disable-a-partner)).
* Its partner portal user `<partner>-operator` in the realm `partner`, and the Secret `partner-user-<partner>-operator`.
* The test's widening of the departments' scope policies for the Composite, if wider than the departments agree to ([Releasing Registry Data to the Composite](../administration/releasing-data-to-the-composite.md#when-use-cases-change)).
* The test partner's local key (`test.state_dir`, default `~/.agri-stack-test/`) and the answers in `scripts/out/`.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| Step 1: the Composite does not serve `/.well-known/jwks.json` | A Composite chart older than the generated key | Upgrade the Composite |
| Step 1: the Composite serves no signing key | Its Secret is missing or unreadable | Check the Secret `agri-composite-signing` and the Composite's log |
| Step 1: a Partner Management does not serve `PARTNER_AGRI_COMPOSITE` | That install's Commons Services has no **Exchange Role**, or cannot reach the Composite's JWKS URL | [Farmer Registry: check](farmer-registry.md#check) |
| Step 1: a Partner Management serves other keys for `PARTNER_AGRI_COMPOSITE` | An install older than the generated key holds a key of its own | [Keys: an older install](../administration/keys.md#an-older-install) |
| Admin token: HTTP 401 | Wrong client secret, or a secret from another install | Check the credential in the configuration |
| The query fails with 403 `partner_not_allowed` | The partner has no policy for the use case (`name@major`) | Rerun; or **Add policy** for the use case on the partner |
| The query fails with 403 `consent_denied` (`partner_consent_not_accepted`) | The partner signed its own consent but its policy does not allow it | Rerun with `test.consent: sign` (the script then allows it), or tick **May present its own signed consents** on the policy |
| A source `denied` | The department's scope policy for the Composite does not cover the use case, or the department CM has no **Exchange Role** `department` | [Releasing Registry Data to the Composite](../administration/releasing-data-to-the-composite.md); the department's Commons Services |
| The query fails with 503 `partner_policy_unavailable` | The Composite cannot read Partner Management | Check the Exchange's Partner Management partner API |

---
description: >-
  Testing the composite end to end from a laptop with one script: it sets up a
  test partner in Partner Management and the Consent Manager, the composite's
  signing key, picks a farmer, calls loan-profile and checks the answer.
---

# End-to-End Test from a Laptop

[`composite/scripts/e2e.py`](https://github.com/openg2p/agri-stack/blob/develop/composite/scripts/e2e.py) tests the composite against a cluster namespace from your laptop. Using your current kubectl context, it reaches the services through `kubectl port-forward` (closed on exit), sets up a test partner and the composite's signing key, picks a farmer who has crop seasons, calls the `loan-profile` use case, verifies the composite's signature and saves the JSON answer.

## Prerequisites

* A namespace with Agri Stack deployed: commons (MDS with the agriculture domain and sample people, PM, CM, Keycloak, Postgres), the Farmer Registry and the Crop Sown Registry with sample data, and the composite. See [deploying on a cluster](deployment.md).
* `kubectl` with a context that can read Secrets and Deployments, `exec` into the Postgres pod, port-forward, and (for setup) create a Secret and restart the composite in that namespace. `--context` picks another context.
* Python 3 with a virtual environment:

```bash
cd agri-stack
python3 -m venv .venv && . .venv/bin/activate
pip install -r composite/scripts/requirements.txt     # cryptography, pyjwt, httpx
```

## The recommended commands

```bash
python composite/scripts/e2e.py -n <ns> --partner bank-a --yes    # first time: set up, then call
python composite/scripts/e2e.py -n <ns> --partner bank-a --call-only    # afterwards: call with the saved keys
```

* **`--partner` (required):** a partner the use case allows (`allowed_partners`); `loan-profile` allows `bank-a`. The script registers a **TEST** key for it in Partner Management (`PARTNER_BANK_A`), so use a partner ID that is a test partner in that environment. To test with another ID, add it to the use case's `allowed_partners` first (Rancher → Apps → Installed Apps → the composite release → **Edit YAML**, key `composite.useCases.<use case>`; pods reload the use case within about 30 s).
* **`--yes`:** make the listed writes without asking. Without it, the script lists every write and waits for a typed `yes`.
* **`--call-only`:** no setup; it signs with the saved keys and calls.

### Registries in other namespaces (exchange)

When the composite runs in the exchange namespace and the registries in department namespaces (see [Distributed Deployment Architecture](../design/distributed-deployment-architecture.md)):

```bash
python composite/scripts/e2e.py -n agrix --partner bank-a --fr-namespace trial --csr-namespace dept1 --yes
```

* **`--fr-namespace`, `--csr-namespace`:** where each registry, its PM, CM and Postgres run (default: `-n`).
* Each registry checks the composite's signature at **its own** PM and the consent at **its own** CM, so the script also sets those up:
  * **exchange mode** (composite `consent.mode: exchange`): the department PM gets the composite's key; the department CM gets a binding and policy for the composite (audience `agri-composite`) for its registry. The partner (`bank-a`) is set up only in the exchange.
  * **passthrough mode:** the department PM gets both keys, and the department CM a binding and policy for the partner.
* In exchange mode the script **checks, but does not set**, that the exchange CM issues receipts to the composite (`global.agriStackExchange.issuer`, `receiptPresenters`) and that each department CM trusts them (`global.agriStackExchange.trustedIssuer`: the exchange CM's issuer ID, its partner API JWKS URL, presenter `agri-composite`). If not, it stops with exit code 2 and names the missing setting.
* A registry that is not installed yet (no database) is reported; the script then picks a Farmer Registry farmer and that registry's sources do not answer ok.

## What each step does

| Step | What happens |
| --- | --- |
| **1. Discover** | Finds the composite, PM, CM, Keycloak and Postgres in the namespace, and PM, CM and Postgres in each registry's namespace (from the Deployments' environment), reads the use case's `allowed_partners` and purpose, and checks that the test partner is allowed (if not: print the Helm value change and stop, exit 2) |
| **2. Admin tokens** | Gets admin tokens from Keycloak with the PM and CM admin clients' secrets, read with kubectl and held in memory only (`--pm-client-id`, default PM's `PARTNER_MANAGER_AUTH_ADMIN_CLIENT_ID`; `--cm-client-id`, default `consent-manager`) |
| **3. Keys** | Loads or creates the test partner's key and the composite's `.p12` in the state directory (below) |
| **4. Plan** | With GETs only: what PM, CM and the signing Secret need |
| **5. Apply** | **(idempotent)** **PM:** onboard and approve the test partner and the composite, or add the key with a key-update request and approve it. **CM:** a binding and a policy per registry (`farmer-registry`, `crop-sown-registry`) for the test partner's audience. **Kubernetes:** Secret `agri-composite-signing`, then `rollout restart` of the composite. A signing Secret whose key PM already serves is left alone. |
| **6. Farmer** | `--fan`, or a FAN that is in the Farmer Registry and has crop seasons in the Crop Sown Registry, found with read-only `psql` in the Postgres pod of each registry's namespace (`--postgres-pod`, composite namespace only, default `commons-postgresql-0`; databases `--fr-db fr`, `--csr-db csr`) |
| **7. Call** | Builds a consent with both grants (valid one day), signs the envelope, posts it to the composite through a port-forward, checks the response signature against the composite's PM key, and prints a summary with each source's status |
| **8. Pre-signed request** | Only with `--emit-curl` / `--emit-postman` |

If the first call right after setup fails with 401 or a `denied`/`error` source, PM and CM caches may still hold the old state: the script waits `--settle` seconds (default 65) and retries once.

**Stops with exit code 2** when a decision is needed: the partner is not in the use case's `allowed_partners`, a CM policy is waiting for AWE approval (approve it in AWE, then rerun), a PM key conflicts (rerun with `--new-keys`), or the writes were not confirmed.

## Where keys are stored

| What | Where |
| --- | --- |
| Test partner's private key | `~/.agri-composite-e2e/<ns>/<partner>.key.pem` (file mode 0600) |
| Composite's key | `~/.agri-composite-e2e/<ns>/composite.p12` (0600) |
| Kids and the `.p12` password | `~/.agri-composite-e2e/<ns>/state.json`: `{"partners": {id: {"kid"}}, "composite": {"id", "kid", "p12_password"}}` |
| The directory | `~/.agri-composite-e2e/<ns>/`, mode 0700; `--state-dir` puts it elsewhere |
| Public keys | In PM (`PARTNER_<PARTNER>`, `PARTNER_AGRI_COMPOSITE`) |
| Composite's key in the cluster | Kubernetes Secret `agri-composite-signing` (`composite.p12`, `password`, `kid`, `algorithm`) |

Keys are reused across runs. `--new-keys` generates new test keys with new kids instead. In `--dry-run` nothing is written: missing keys are generated in memory only.

## Outputs

Each run writes two files to `composite/scripts/out/` (git-ignored, owner-only; they hold a farmer's personal data), with the same timestamp:

* the response JSON: `<use case>-<namespace>-<time>.json`, e.g. `loan-profile-trial-20261001-100000.json`;
* everything the script printed: `e2e-<namespace>-<time>.log`.

The screen shows the log and a summary with each source's status. `--print` also prints the JSON; `--out-dir` saves the files elsewhere. Logs mask the FAN; secrets are never printed.

## Other options

| Option | |
| --- | --- |
| `--dry-run` | Discover and plan with GETs and SELECTs only; prints the planned writes and probes the composite (`/ping`, describe). No writes. |
| `--setup-only` | Set up, don't call |
| `--fan <FAN>`, `--crop-year`, `--season` | Pick the farmer and the season (`SEASON_MEHER`, `SEASON_BELG`, `SEASON_IRRIGATION`) |
| `--emit-curl` | Print a pre-signed `curl`, for a port-forward and for the ingress |
| `--emit-postman FILE` | Write a Postman collection with the pre-signed request (owner-only; `*.postman.json` is git-ignored) |
| `--no-call` | With `--emit-*`: only emit the pre-signed request |
| `--purpose` | Consent purpose (default: the use case's) |
| `--composite-deployment`, `--pm-deployment`, `--cm-deployment` | Override discovery |
| `--insecure` | Skip TLS verification towards Keycloak |

{% hint style="warning" %}
A pre-signed request **expires about 5 minutes after signing**: `header.message_ts` and the consent's `issued_at` must be within 300 seconds of the server's clock.
{% endhint %}

```bash
python composite/scripts/e2e.py -n <ns> --partner bank-a --call-only --crop-year 2018 --season SEASON_MEHER \
    --emit-curl --emit-postman loan-profile.postman.json
```

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | OK |
| 1 | Error |
| 2 | A decision is needed (`allowed_partners`, AWE approval, a key conflict, writes not confirmed) |
| 3 | The call failed, the response signature did not verify, or a source did not answer `ok` / `no_record` |
| 130 | Interrupted |

Unit tests for the script's pure parts: `pytest composite/scripts/tests`.

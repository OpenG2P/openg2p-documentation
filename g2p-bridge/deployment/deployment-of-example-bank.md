---
description: The bundled Example Bank simulator and the digital-cash treasury account
---

# Example Bank & Treasury Account

The **Example Bank** is a reference simulator of a Sponsor Bank. It exists so the
**digital cash transfer** flow can be demonstrated end to end without a real
bank: the Bridge checks funds, blocks funds, initiates payments and reconciles
against this simulator.

It is **bundled into the single [`openg2p-bridge` chart](helm-charts.md)** — there
is no separate Example Bank chart or repository any more. Deploy or skip it with
one toggle.

## Enabling / disabling

| Value | Default | Description |
| --- | --- | --- |
| `exampleBank.enabled` | `true` | Deploy the Example Bank (API + Celery beat/worker). |
| `global.exampleBankHostname` | `example-bank.<namespace>.openg2p.org` | Example Bank API hostname. |

{% hint style="warning" %}
**Disable the Example Bank for production** (`exampleBank.enabled: false`) and
point the Bridge at a real sponsor bank connector instead. The Example Bank is a
simulator for demos and testing only.
{% endhint %}

## Digital cash needs no PBMS or Registry

For **pure digital cash transfer** (`global.g2pBridgeInKindEnabled: false`, the
default), the Bridge needs neither the PBMS database nor the Registry. Instead of
reading the sponsor-bank configuration from PBMS, the Bridge reads it directly
from Helm values. The Celery workers and beat tasks for geo/warehouse/agency
allocation are not scheduled at all in this mode.

In-kind benefits (goods/services) still require PBMS + Registry; enable them with
`global.g2pBridgeInKindEnabled: true`.

## One treasury account, two consumers

The sponsor/treasury account is defined **once** in Helm values and is the
**single source of truth** for both the Bridge and the Example Bank:

```yaml
global:
  g2pBridgeInKindEnabled: false      # digital cash mode
  seedTreasuryAccount: true          # seed the account into the Example Bank
  sponsorBankConfigurations:
    default:
      sponsor_bank_code: EXAMPLE
      program_account_number: "SPONSOR0001"
      program_account_branch_code: ""
      account_currency: USD
      available_balance: "10000000"   # opening balance
      account_holder_name: Program Treasury
```

* **The Bridge** uses `sponsor_bank_code` and `program_account_*` as the
  digital-cash sponsor configuration (replacing what would otherwise come from
  PBMS).
* **The Example Bank** uses `program_account_number`, `account_currency`,
  `available_balance` and `account_holder_name` to **seed a matching account**
  so the Bridge's calls against `SPONSOR0001` succeed.

`sponsorBankConfigurations` is keyed by `"<benefit_program_id>:<benefit_code_id>"`;
the `default` entry applies to all programs.

## How the seeding works

The Example Bank has **no account-creation API or UI**, so the account must be
seeded. When `seedTreasuryAccount: true`, the Example Bank API **self-seeds the
treasury account on its database migration at startup** — it creates the account
from the values above only if it does not already exist (idempotent; existing
balances are left untouched). This keeps Helm values as the single source of
truth, with no manual SQL step.

To verify after install, call `check_funds` on the Example Bank:

```bash
curl -s -X POST \
  https://example-bank.<namespace>.openg2p.org/api/example-bank/check_funds \
  -H 'Content-Type: application/json' \
  -d '{"account_number":"SPONSOR0001","account_currency":"USD","total_funds_needed":100}'
```

A response with `"has_sufficient_funds": true` confirms the account was seeded.

## Database

The Example Bank uses its own database (`example_bank_db`, user `bankuser`)
created via `postgres-init` inside the shared `commons-postgresql`, alongside the
Bridge database. Both are removed by the [uninstall script](teardown.md).

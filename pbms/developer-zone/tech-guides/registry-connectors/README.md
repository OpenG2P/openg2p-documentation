# Registry Connector

The registry connectors are how PBMS reads beneficiaries from a registry. They live in the
[`registry-adapters`](https://github.com/OpenG2P/pbms-connectors/tree/develop/extensions/registry-adapters)
extension of the [pbms-connectors](https://github.com/OpenG2P/pbms-connectors) repo, and are installed
into the Celery and staff portal API images.

## Overview

PBMS asks a register (`farmer`, `household`, `disability`) for eligible IDs, entitlement multipliers,
beneficiary records and beneficiary search. Each register can be read in one of two ways, chosen per
register at deploy time:

| Connector | Reads from | Use when |
| --------- | ---------- | -------- |
| `db` | The registry database, with SQL on the register's table or view (see the [Registry Database Contract](../registry-database-contract.md)) | PBMS can reach the registry database directly |
| `dci` | The registry's Partner API, with DCI sync search | The registry is a separate installation and only its Partner API is reachable |

Every register has its own connector and connection string, so registers can live in different
databases or different registry installations.

**Code:** [`RegistryInterface`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/interface/registry_interface.py) (the contract),
[`computations/_base.py`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/computations/_base.py) (the shared `RegistryDB` and `RegistryDCI` classes),
[`computations/farmer.py`](https://github.com/OpenG2P/pbms-connectors/blob/develop/extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/computations/farmer.py) (an example register).

## Configuration

Each register takes two settings. In the `openg2p-pbms` Helm chart they are
`global.registers.<register>.connector` and `global.registers.<register>.connectionString`, and Rancher
shows one group per register. The chart passes them to the Celery workers and the staff portal API as:

```bash
REGISTRY_ADAPTERS_<REGISTER>_CONNECTOR=db|dci
REGISTRY_ADAPTERS_<REGISTER>_CONNECTION_STRING=...
```

The connection string carries everything the connector needs:

| Connector | Connection string |
| --------- | ----------------- |
| `db` | `postgresql://user:pass@host:5432/dbname`. Percent-encode special characters in the password. The port defaults to `5432`. |
| `dci` | The full search URL of the Partner API: `http(s)://host[:port]/dci/registry/sync/search`. Optional query parameters: `reg_type`, `reg_record_type` (default to the register's own values), `timeout` (seconds, default `30`) and `ssl_verify` (default `true`). |

Examples:

```yaml
global:
  registers:
    farmer:
      connector: db
      connectionString: postgresql://farmer_registry_user:secret@commons-postgresql:5432/farmer_registry
    household:
      connector: dci
      connectionString: http://household-registry-partner-api/dci/registry/sync/search
    disability:
      connector: dci
      connectionString: https://partner-dr.example.org/dci/registry/sync/search?timeout=60&ssl_verify=true
```

A register with an empty connection string is unconfigured: only programs that target it fail, with
an error naming the register. An invalid connection string (unknown scheme, a DCI URL without the
search path, an unknown query parameter) fails the same way.

{% hint style="info" %}
The connection string is a secret when it holds a database password. Rancher shows it as a password
field.
{% endhint %}

## Registry requirements for the `dci` connector

PBMS calls the Partner API's DCI sync search **unsigned and without consent**. The registry must
accept that:

* Turn **partner signature validation off** (`global.partnerSignatureValidationEnabled: false` in the
  registry chart).
* Turn **consent enforcement off** (`global.consentEnforcementEnabled: false`).
* Allow searching on every field PBMS filters on: the register's DCI `fields` (see
  `computations/<register>.py`) must be in the registry's `REGISTRY_PARTNER_API_DCI_ALLOWED_SEARCH_FIELDS`.

{% hint style="warning" %}
With both switches off, the Partner API returns full records to any caller that can reach it. Keep
it reachable only from inside the cluster (or behind a gateway that admits PBMS), and turn the
switches back on once PBMS signs its requests.
{% endhint %}

## Registrant IDs depend on the connector

Beneficiary lists store one ID per registrant:

* `db` stores the record's `internal_record_id`.
* `dci` stores the register's DCI `match_field`: `foundational_id` for `farmer`, `functional_record_id`
  for `household` and `disability`.

So lists built with one connector cannot be searched or entitled with the other. Pick a register's
connector before programs use it, and rebuild the lists if you switch.

{% content-ref url="key-components.md" %}
[key-components.md](key-components.md)
{% endcontent-ref %}

{% content-ref url="example-implementation-workflow.md" %}
[example-implementation-workflow.md](example-implementation-workflow.md)
{% endcontent-ref %}

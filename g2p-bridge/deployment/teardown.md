---
description: Completely uninstalling a G2P Bridge release
---

# Teardown / Uninstall

`helm uninstall` removes the Bridge **workloads**, but it does **not** drop the
PostgreSQL database and role — those live inside the shared `commons-postgresql`
instance and are not owned by the Helm release, so they survive. A few
subchart hook Jobs (`postgres-init`, `keycloak-init`) and any retained PVs also
linger. The repository ships an **uninstall script** that cleans all of this up
safely.

Script: [`deployment/scripts/uninstall-bridge.sh`](https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/blob/develop/deployment/scripts/uninstall-bridge.sh)

## What it does

In order:

1. **`helm uninstall <release>`** — Bridge + bundled Example Bank workloads,
   services, Helm-owned secrets/configmaps, the Keycloak client K8s secret, etc.
2. **Deletes leftover hook Jobs and their Pods** (`postgres-init`,
   `keycloak-init` keep themselves around via `hook-delete-policy:
   before-hook-creation`).
3. **Sweeps leftover Secrets/ConfigMaps** labelled
   `app.kubernetes.io/instance=<release>`.
4. **Drops the Postgres databases and roles** for this release, by `kubectl exec`
   into the Postgres pod (it terminates connections, then `DROP DATABASE` /
   `DROP ROLE`).
5. **Deletes PVCs** labelled with the release.
6. **Deletes PVs** still bound to those PVCs (typically `Released` PVs created
   with `reclaimPolicy=Retain`).

### Databases dropped

Only the databases this chart's `postgres-init` created:

* `<release-with-underscores>` — e.g. `g2p_bridge`
* `example_bank_db` — the bundled Example Bank (skip with `--keep-example-bank-db`)

It does **not** drop `registry_db` or `pbms_db` — those belong to other
components.

## What it preserves

{% hint style="danger" %}
The script **never deletes the PostgreSQL pod/instance** (`commons-postgresql`).
It only `kubectl exec`s into it to drop the Bridge's own databases and roles.
Other databases (`registry_db`, `pbms_db`) and all other components are left
untouched.
{% endhint %}

It also leaves the **Keycloak realm/client** (`g2p-bridge`) intact — that lives
in Keycloak, not in the namespace. `keycloak-init` is idempotent, so a
re-install reuses it.

## Usage

```bash
cd g2p-bridge/deployment/scripts

# Always dry-run first — prints the full blast radius, changes nothing:
./uninstall-bridge.sh --namespace trial --dry-run

# For real (prompts you to type the release name to confirm):
./uninstall-bridge.sh --namespace trial

# Non-interactive (CI / scripted):
./uninstall-bridge.sh --namespace trial --yes
```

### Options

| Flag | Default | Description |
| --- | --- | --- |
| `--namespace`, `-n` | _(required)_ | Release namespace. |
| `--release` | `g2p-bridge` | Helm release name (determines the DB/role names). |
| `--postgres-release` | `commons-postgresql` | Postgres Helm release to exec into. |
| `--postgres-namespace` | same as `--namespace` | Namespace of the Postgres instance. |
| `--keep-example-bank-db` | off | Do **not** drop `example_bank_db` / `bankuser` (use when several Bridge releases share one Postgres). |
| `--keep-pvs` | off | Delete PVCs but keep the PVs. |
| `--drop-superset-ro` | off | Also drop the `superset_ro` analytics role and its Secret. Without it, they are left for a later reinstall. |
| `--dry-run` | off | Print actions, change nothing. |
| `--yes`, `-y` | off | Skip the interactive confirmation. |

Requires: `kubectl` (cluster admin), `helm`, and `bash` 4+.

{% hint style="info" %}
The Superset **dashboards** are not removed by this script — they live in
Superset's metadata DB. To remove them, run `remove_dashboards.py` in the Superset
pod. See [Dashboards (Superset) → Uninstalling](dashboards.md#uninstalling-clean-teardown).
{% endhint %}

{% hint style="warning" %}
`example_bank_db` / `bankuser` are **fixed** names (not release-scoped). If
multiple Bridge releases share one `commons-postgresql`, dropping them affects
all of them — pass `--keep-example-bank-db` in that case.
{% endhint %}

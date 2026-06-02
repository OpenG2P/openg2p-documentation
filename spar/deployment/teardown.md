---
description: Completely uninstalling a SPAR release
---

# Teardown / Uninstall

`helm uninstall` removes the SPAR **workloads**, but it does **not** drop the
PostgreSQL database and role — those live inside the shared `commons-postgresql`
instance and are not owned by the Helm release, so they survive. A few subchart
Jobs (`postgres-init`, `keycloak-init`) and any retained PVs also linger. The
repository ships an **uninstall script** that cleans all of this up safely.

Script: [`deployment/scripts/uninstall-spar.sh`](https://github.com/OpenG2P/openg2p-spar/blob/develop/deployment/scripts/uninstall-spar.sh)

## What it does

In order:

1. **`helm uninstall <release>`** — SPAR workloads, services, Helm-owned
   secrets/configmaps, istio virtualservices/gateways, etc.
2. **Deletes leftover subchart Jobs and their Pods** (`postgres-init`,
   `keycloak-init`).
3. **Sweeps leftover Secrets/ConfigMaps** labelled
   `app.kubernetes.io/instance=<release>` — **excluding** the `keycloak-init`
   client secret, which is preserved.
4. **Drops the Postgres database and role** for this release, by `kubectl exec`
   into the Postgres pod (it terminates connections, then `DROP DATABASE` /
   `DROP ROLE`).
5. **Deletes PVCs** labelled with the release.
6. **Deletes PVs** still bound to those PVCs (typically `Released` PVs created
   with `reclaimPolicy=Retain`).

### Database dropped

Only the database this chart's `postgres-init` created:

* `<release-with-underscores>` — e.g. release `spar` → database `spar`, role
  `spar_user`.

It does **not** drop databases owned by other components.

## What it preserves

{% hint style="danger" %}
The script **never deletes the PostgreSQL pod/instance** (`commons-postgresql`).
It only `kubectl exec`s into it to drop SPAR's own database and role. Other
databases and all other components are left untouched.
{% endhint %}

It also keeps the **Keycloak client secret** (`openg2p-spar`) intact by default —
that secret carries `helm.sh/resource-policy: keep` and is excluded from the
sweep, so a re-install reuses the same client password. The **Keycloak
realm/client** itself lives in Keycloak (not the namespace) and is likewise left
untouched; `keycloak-init` is idempotent. Pass `--purge-keycloak-secrets` to
delete the client secret as well.

## Usage

```bash
cd openg2p-spar/deployment/scripts

# Always dry-run first — prints the full blast radius, changes nothing:
./uninstall-spar.sh --namespace trial --dry-run

# For real (prompts you to type the release name to confirm):
./uninstall-spar.sh --namespace trial

# Non-interactive (CI / scripted):
./uninstall-spar.sh --namespace trial --yes
```

### Options

| Flag | Default | Description |
| --- | --- | --- |
| `--namespace`, `-n` | _(required)_ | Release namespace. |
| `--release` | `spar` | Helm release name (determines the DB/role names). |
| `--postgres-release` | `commons-postgresql` | Postgres Helm release to exec into. |
| `--postgres-namespace` | same as `--namespace` | Namespace of the Postgres instance. |
| `--purge-keycloak-secrets` | off | Also delete the `keycloak-init` client secret(s) (kept by default). |
| `--keep-pvs` | off | Delete PVCs but keep the PVs. |
| `--dry-run` | off | Print actions, change nothing. |
| `--yes`, `-y` | off | Skip the interactive confirmation. |

Requires: `kubectl` (cluster admin), `helm`, `jq`, and `bash` 4+.

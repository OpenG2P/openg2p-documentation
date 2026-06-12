# Dashboards (Superset)

The G2P Bridge ships a set of **read-only monitoring dashboards** for the platform
**Apache Superset** (`commons-services-superset`). They give operators a view of
disbursements, failures, reconciliation, SPAR mappings and the Example Bank —
without any custom UI.

Superset connects to the bridge / SPAR / Example-Bank databases as a **read-only
data source** and stores the dashboards in its own metadata database. The G2P
Bridge **Helm chart is not coupled to Superset** — the dashboards are uploaded
**manually by a Superset admin** (see [Why manual](#why-manual)).

## Dashboards offered

| Dashboard | Source DB | What it shows |
| --- | --- | --- |
| **Operations Overview** | `g2p_bridge` | totals, amount disbursed, by-stage, by-program, volume over time, recent disbursements |
| **Failures & Exceptions** | `g2p_bridge` | cancellations, FA / sponsor-dispatch error codes, distribution by current stage |
| **Reconciliation & Settlement** | `g2p_bridge` | reconciliation records, recon errors by reason, reversals |
| **SPAR — Mappings, Strategies & Parties** | `spar` | ID→FA mappings, strategy registry, banks registry |
| **Example Bank (Simulator)** | `example_bank_db` | accounts & balances, payment batches by status, transactions over time |

All five are read-only. The dashboards themselves are **release-agnostic** — table
names are identical across bridge releases; only the **database connection** is
environment-specific (set once, at import time).

## Prerequisite — the read-only DB role

Superset connects with a **SELECT-only** Postgres role (`superset_ro`) so SQL Lab
and the dashboards can read data but never modify it. This is **automated by the
bridge chart** — enable it once per environment:

```yaml
# values.yaml
supersetReadOnly:
  enabled: true     # default false
```

On install **and every upgrade** the chart then:

* creates the `superset_ro` role (read-only `SELECT` on `g2p_bridge`,
  `example_bank_db` and `spar`, including future tables), and
* publishes its generated password in a Secret named **`<release>-superset-ro`**
  (key `password`), kept stable across upgrades.

The database names are taken from chart values, not hard-coded: `global.bridgeDB`
(tracks the release name), `global.exampleBankDB`, and `global.sparDB` (surfaced
in Rancher as **“SPAR Database Name”**, default `spar`) — override `global.sparDB`
if SPAR's database is named differently in your environment.

**Read the password** (you'll paste it once during import):

```bash
kubectl -n <ns> get secret <release>-superset-ro \
  -o jsonpath='{.data.password}' | base64 -d; echo
```

> Not using the chart automation? Create the role manually with
> `deployment/superset/01-readonly-role.sql` from the g2p-bridge repo.

## Uploading the dashboards (admin steps)

After the bridge and Superset are both installed:

1. **Download the bundle** `g2p-bridge-dashboards.zip` — from the **GitHub Release
   assets** (recommended; no checkout needed) or from `deployment/superset/` in
   the g2p-bridge repo.
2. **Get the read-only password** from the `<release>-superset-ro` Secret (above).
3. In Superset: log in (SSO) → **Settings → Import Dashboards** →
   * upload `g2p-bridge-dashboards.zip`,
   * tick **“Overwrite existing”**,
   * when prompted, paste the **`superset_ro` password** for each connection.
4. Open the dashboards under **Dashboards**.

That's the whole flow: **download → upload → paste password once**. The export
masks passwords, so nothing secret is stored in the ZIP or the repo.

{% hint style="info" %}
**You only enter the password on the first import.** Superset matches connections
by UUID, so every later re-import **reuses the existing connection — no prompt**.
Day-to-day, updating dashboards is just *download → upload → Overwrite*.
{% endhint %}

## Re-importing / updating

Re-uploading the ZIP with **“Overwrite existing”** ticked **updates the dashboards
in place** (matched by UUID) — same dashboards, **same URLs**, content replaced.
It is not a delete-and-recreate, and it never creates duplicates. Note it is an
*update*, not a full sync: a chart removed in a newer bundle is not auto-deleted.

## Connection details

The imported connections point at host **`commons-postgresql`** and databases
**`g2p_bridge`**, **`spar`**, **`example_bank_db`**. If the bridge release was
**renamed** (e.g. `g2p-bridge2` → DB `g2p_bridge2`), edit that one connection's
database name during/after import — everything else is unchanged.

## Why manual

Superset and the bridge have **independent lifecycles** — you may run Superset
without the bridge, or the reverse. If Superset preloaded these dashboards, they
would point at databases/tables that may not exist (broken charts). So they are
loaded **only where the bridge data actually exists**, by an admin, against
whichever database the connection points at.

## Uninstalling — clean teardown

To remove **everything** (nothing left hanging; a later reinstall is fresh), run
these two commands, in order. Replace `<ns>` with your namespace.

**Step 1 — remove the dashboards from Superset:**

```bash
SP=$(kubectl -n <ns> get pods -o name | grep -E "superset-[0-9a-f]+-" | grep -v worker | grep -v init | head -1)
kubectl cp deployment/superset/remove_dashboards.py <ns>/${SP#pod/}:/tmp/
kubectl -n <ns> exec ${SP#pod/} -- python /tmp/remove_dashboards.py
```

**Step 2 — uninstall the bridge (DBs, roles, the `superset_ro` role + Secret, everything):**

```bash
deployment/scripts/uninstall-bridge.sh --namespace <ns> --drop-superset-ro --yes
```

Done — Superset has no bridge dashboards/connections, Postgres has no bridge DBs
or roles, and Kubernetes has no bridge workloads/secrets.

{% hint style="info" %}
If you uninstall the bridge **without** Step 1, the dashboards stay in Superset
but break (they point at the dropped database). They are harmless and reconnect
automatically if you reinstall. Step 1 simply removes them for good.
{% endhint %}

## Maintaining the bundle (for maintainers)

The dashboards are defined in code at `deployment/superset/provision_dashboards.py`
(idempotent). To regenerate the shareable ZIP after editing, run it inside the
Superset pod and re-export:

```bash
RO_PASS=$(kubectl -n <ns> get secret <release>-superset-ro -o jsonpath='{.data.password}' | base64 -d)
kubectl cp provision_dashboards.py <ns>/<superset-pod>:/tmp/
kubectl -n <ns> exec <superset-pod> -- env RO_PASS="$RO_PASS" python /tmp/provision_dashboards.py
kubectl -n <ns> exec <superset-pod> -- superset export-dashboards -f /tmp/d.zip
kubectl cp <ns>/<superset-pod>:/tmp/d.zip ./g2p-bridge-dashboards.zip
```

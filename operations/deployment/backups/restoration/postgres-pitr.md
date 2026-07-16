---
description: Restore PostgreSQL to a specific point in time using pgBackRest.
---

# Postgres PITR

Use this when you need to roll the database back to a specific moment — typically after a bad migration, an accidental destructive query, or data corruption you can date.

## Pre-flight

* Know the **target time** (ISO-8601, e.g. `'2026-04-26 14:00:00 IST'`) and the time zone.
* Know whether you want PITR (a specific moment) or just the latest backup (`--type=immediate`).
* Have the `pgbackrest.pass` passphrase from your keystore.

## Step 1 — Dry-run

Confirms the orchestrator can find the right backup and constructs the right command:

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component pg \
    --point-in-time '2026-04-26 14:00:00' \
    --dry-run
```

Reads the timestamp, prints the pgBackRest command, exits without touching anything.

## Step 2 — Staged restore

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component pg \
    --point-in-time '2026-04-26 14:00:00'
```

What this does:

1. Creates `/var/lib/openg2p-backup-restore/pg-<timestamp>/` on the storage node, owned by `postgres`.
2. Runs `pgbackrest --type=time --target=... --target-action=promote --pg1-path=<above> restore`.
3. Replays WAL up to the target time.
4. **Stops there.** Does not touch the live Postgres instance.

The staged Postgres data directory is a complete, valid `PGDATA` for the target time. You can start a temporary Postgres against it on a different port to inspect, dump tables, or verify before cutting over.

## Step 3 — Verify the restore

On the storage node, start a **temporary** Postgres against the staged `PGDATA`. On Ubuntu packaging, cluster config lives under `/etc/postgresql/…`, not inside `PGDATA`, so a bare `pg_ctl -D <staged>` often needs a few local files before it will start:

```bash
STAGED=/var/lib/openg2p-backup-restore/pg-<timestamp>

# Minimal config in the staged dir (Ubuntu keeps the real conf under /etc/postgresql).
sudo -u postgres tee "$STAGED/postgresql.conf" >/dev/null <<EOF
listen_addresses = ''
port = 55432
unix_socket_directories = '/tmp'
max_connections = 100
shared_buffers = 128MB
EOF
# Raise max_connections to at least the live primary's value if recovery complains.
sudo -u postgres touch "$STAGED/pg_ident.conf"
# If recovery needs archive-get, set restore_command to the real pgBackRest
# archive-get (empty restore_command will stall if local WAL is incomplete).

sudo -u postgres /usr/lib/postgresql/16/bin/pg_ctl \
    -D "$STAGED" \
    -o '-p 55432' \
    -l "$STAGED/pg.log" start

# Prefer -h /tmp so psql uses the unix socket you configured.
sudo -u postgres psql -h /tmp -p 55432 -d postgres -c '\l'
sudo -u postgres psql -h /tmp -p 55432 -d <db> -c 'SELECT now();'
sudo -u postgres psql -h /tmp -p 55432 -d <db> -c 'SELECT count(*) FROM <some_table>;'

sudo -u postgres /usr/lib/postgresql/16/bin/pg_ctl -D "$STAGED" stop
```

`pgBackRest` path-mismatch warnings (`[032]`) during recovery are often noisy but harmless if archive recovery still completes.

## Step 4 — Cutover (live PG replacement)

This is the destructive step. **Read it, plan a maintenance window, then do it.**

Two options:

### Option A — full replace (simpler, more downtime)

```bash
# On storage node, with workloads paused or tolerant of DB outage:
sudo systemctl stop postgresql@16-main

# Move live datadir aside (DON'T DELETE — keep until verified).
sudo mv /var/lib/postgresql/16/main /var/lib/postgresql/16/main.precrash

# Move the staged restore into place.
sudo mv /var/lib/openg2p-backup-restore/pg-<timestamp> /var/lib/postgresql/16/main
sudo chown -R postgres:postgres /var/lib/postgresql/16/main

# Start PG.
sudo systemctl start postgresql@16-main

# Verify.
sudo -u postgres psql -d postgres -c '\l'

# Re-create the pgBackRest stanza so future backups continue.
sudo -u postgres pgbackrest --stanza=openg2p stanza-create
sudo -u postgres pgbackrest --stanza=openg2p check
```

After at least one successful subsequent backup, you can `rm -rf /var/lib/postgresql/16/main.precrash`.

### Option B — selective table restore (less downtime, more skill)

If only some tables are affected:

```bash
# Start the staged PG on a different port (Step 3 above).
# Dump the affected tables.
sudo -u postgres pg_dump -h /tmp -p 55432 -d <db> -t <schema>.<table> -F c -f /tmp/restore.pgdump

# On live PG, drop or truncate the bad data, then restore.
sudo -u postgres pg_restore -d <db> -t <table> /tmp/restore.pgdump

sudo -u postgres /usr/lib/postgresql/16/bin/pg_ctl \
    -D /var/lib/openg2p-backup-restore/pg-<timestamp> stop
```

Use this when only one or two tables are corrupt and the rest of the database has activity you don't want to lose.

## Restore failed mid-way

pgBackRest's restore is atomic at the dataset level — if it fails, the staged dir is incomplete but the live PG is untouched. Read the error, fix (out of disk? wrong target time format?), and re-run.

## Upstream reference

The full pgBackRest user guide covers restore variants in detail:

* [PITR](https://pgbackrest.org/user-guide.html#pitr)
* [Restore](https://pgbackrest.org/command.html#command-restore)
* [Recovery options](https://pgbackrest.org/configuration.html#section-restore)

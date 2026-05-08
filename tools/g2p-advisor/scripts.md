# Scripts

Utility scripts under `scripts/` in the [advisor repo](https://github.com/openg2p/g2p-advisor). All are TypeScript, run via `tsx`, and pick up environment from `.env`.

## `npm run migrate`

Apply every SQL file under `migrations/` in lexical order, idempotently. Each migration runs inside a transaction. The `schema_migrations` table tracks which files have been applied so re-runs are safe.

Run after pulling new commits if the repo's `migrations/` directory has new files.

## `npm run seed:phase2`

Stuff a known-good Phase 2 input set into a project's `working_case`. Bypasses the (planned) Phase 2 chat handler — use it during development to test the build pipeline without going through the conversational input-collection flow.

```bash
npm run seed:phase2 -- \
  --project <project-uuid> \
  --gitlab-handle <your-gitlab-username> \
  --gitlab-email <your-email> \
  [--mnemonic health-worker] \
  [--org-mnemonic openg2p] \
  [--advance-phase] \
  [--dry-run]
```

Seeds: a single Register called "Health Workers Register" with 5 simple columns, an `HW-` Functional ID prefix, sandbox + production hostnames, `small` Helm resource profile, your GitLab credentials. Clears Phase 1 conditional triggers (`notification_triggering_events`, `existing_system_to_replace`) so Phase 2's conditional checks don't fire.

`--mnemonic` drives the registry's repo + Python package names. `--org-mnemonic` is the implementing organisation's stamp on every Docker image name (`<org>-<mnemonic>-<service>:develop`).

## `npm run cleanup:phase2`

Full Phase 2 cleanup for one project. Leaves Phase 1 state intact.

```bash
npm run cleanup:phase2 -- --project <project-uuid> \
  [--keep-gitlab-repos] [--keep-workspace] [--keep-current-phase] \
  [--clear-messages] [--dry-run]
```

What it does (in order):

1. `TRUNCATE build_jobs + build_job_events` — kills every build job + event row in the DB.
2. Strips every Phase 2 `working_case` key from this project; rolls `current_phase` back to 2 (Phase 1 stays approved).
3. *(optional, `--clear-messages`)* — `DELETE FROM project_messages WHERE project_id = …`. Wipes the chat history for this project so stale LLM hallucinations don't get replayed into the next conversation. Captured Phase 1 facts in `working_case` are NOT touched — only the message thread.
4. `rm -rf <WORKSPACE_PATH>/<project-dir>/` — clears the local generated trees and reference clone.
5. `DELETE` the project's GitLab repos: `<mnemonic>-extension` and `<mnemonic>-deployment`.

What it doesn't touch: the project row itself, Phase 1 working_case keys, approved Phase 1 reports, the user's GitLab subgroup, other projects' workspaces. `project_messages` only deleted with `--clear-messages`.

`--dry-run` previews everything without applying.

## `npm run db:up` / `npm run db:down`

Start / stop the local Postgres container defined at `docker/docker-compose.yml`. Used during dev so you don't need a local Postgres install.

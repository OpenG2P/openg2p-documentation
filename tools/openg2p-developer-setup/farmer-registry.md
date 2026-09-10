# Farmer Registry

Farmer Registry = Registry Gen2 + `farmer-extension` (farmers, land, crops, livestock).

| Item                 | Farmer value                                  |
| -------------------- | --------------------------------------------- |
| Setup profile        | `PROFILE=farmer-registry` or `registry`       |
| Bootstrap            | `make farmer-setup`                           |
| Run                  | `make farmer-registry-run`                    |
| Staff UI port        | **3001** (`FARMER_REGISTRY_UI_PORT`)          |
| Staff API            | **8001**                                      |
| Partner API          | **8006**                                      |
| Master Data (Docker) | **8042**                                      |
| Celery queue         | `farmer_registry_worker_queue`                |
| Databases            | `farmer_registry_db`, `farmer_master_data_db` |
| Keycloak client      | `farmer-registry-staff-portal`                |
| Extension install    | `VARIANT=farmer-registry`                     |
| Generated env        | `generated/farmer-registry/`                  |
| Docker up            | `make docker-farmer-up`                       |

Hub UI stays on **3000** (common). ID Generator / IAM / AWE ports are common (`8040` / `8020` / `8030`).

### Commands

```bash
cp .env.example .env
make setup PROFILE=farmer-registry   # or make setup with SETUP_PROFILE=farmer-registry
make farmer-setup                    # starts infra if needed + IAM/AWE + migrate + config seed
LOAD_SAMPLE_DATA=true make farmer-registry-seed   # optional
make farmer-registry-run
```

Manual (if not using `farmer-setup`):

```bash
make infra-up
make install-registry-extension VARIANT=farmer-registry
make install-registry-ui
make install-iam && make iam-init
make install-awe && make awe-init
make farmer-registry-init
```

Docker-only (includes Common):

```bash
# USE_EXTERNAL_REDIS=false in .env; docker login   (Docker Hub)
make sync-images && make docker-farmer-up
```

### Native processes (Farmer-specific env)

| Process              | Env file                                                           |
| -------------------- | ------------------------------------------------------------------ |
| Farmer staff API     | `generated/farmer-registry/staff-portal-api.env`                   |
| Celery worker / beat | `generated/farmer-registry/celery-workers.env` / `celery-beat.env` |
| Staff UI             | `generated/farmer-registry/staff-portal-ui.env`                    |

Plus common AWE + IAM env under `generated/awe/` and `generated/iam/`.

### Sample data

SQL under `farmer-extension/.../sample_data/`:

```bash
LOAD_SAMPLE_DATA=true make farmer-registry-seed
# or after migrate: LOAD_SAMPLE_DATA=true make up-farmer-registry-seed
```

### Repos (beyond common workspace)

| Repo                 | Purpose                    |
| -------------------- | -------------------------- |
| `farmer-registry`    | Domain extension + db-seed |
| `registry-platform`  | Shared platform (common)   |
| `iam-service`, `awe` | Common SSO / approvals     |

UI path default: `registry-platform/ui/staff-portal-ui` (`FARMER_REGISTRY_UI_PATH`).

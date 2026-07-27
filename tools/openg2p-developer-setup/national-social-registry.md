# National Social Registry

NSR = Registry Gen2 + `nsr-extension` (national social-protection registers).

| Item                    | NSR value                                        |
| ----------------------- | ------------------------------------------------ |
| Setup profile           | `PROFILE=national-social-registry` or `registry` |
| Bootstrap               | `make nsr-setup`                                 |
| Run                     | `make nsr-registry-run`                          |
| Staff UI port           | **3002** (`NSR_REGISTRY_UI_PORT`)                |
| Staff API               | **8011**                                         |
| Partner API             | **8012**                                         |
| Master Data (Docker)    | **8043**                                         |
| Celery queue            | `nsr_registry_worker_queue`                      |
| Databases               | `nsr_registry_db`, `nsr_master_data_db`          |
| Keycloak client         | `nsr-registry-staff-portal`                      |
| Extension install       | `VARIANT=national-social-registry`               |
| Generated env           | `generated/national-social-registry/`            |
| Extra clone for samples | `openg2p-data`                                   |
| Docker up               | `make docker-nsr-up`                             |

**Individual** and **Household** registers require functional IDs via Celery + common ID Generator (`:8040`).

### Commands

```bash
cp .env.example .env
make setup PROFILE=national-social-registry
make nsr-setup
LOAD_SAMPLE_DATA=true make nsr-registry-seed   # needs openg2p-data
make nsr-registry-run
```

Manual:

```bash
make infra-up
make install-registry-extension VARIANT=national-social-registry
make install-registry-ui
make install-iam && make iam-init
make install-awe && make awe-init
make nsr-registry-init
```

Docker-only:

```bash
make sync-images && make docker-nsr-up
```

### Native processes (NSR-specific env)

| Process              | Env file                                                  |
| -------------------- | --------------------------------------------------------- |
| NSR staff API        | `generated/national-social-registry/staff-portal-api.env` |
| Celery worker / beat | `…/celery-workers.env` / `celery-beat.env`                |
| Staff UI             | `…/staff-portal-ui.env`                                   |

AWE approvals (common engine): bind policies under **Configuration → AWE Policy Configuration** or AWE Admin UI (`:8031`).

### Sample data

Uses `openg2p-data` demography JSON (+ product seed files):

```bash
LOAD_SAMPLE_DATA=true make nsr-registry-seed
LOAD_SAMPLE_DATA=true LOAD_TEMPLATES=true LOAD_IMAGES=true make nsr-registry-seed
```

### Repos (beyond common)

| Repo                       | Purpose             |
| -------------------------- | ------------------- |
| `national-social-registry` | Extension + db-seed |
| `openg2p-data`             | Sample demography   |

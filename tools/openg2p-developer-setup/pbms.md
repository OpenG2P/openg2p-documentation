# PBMS

| Item            | PBMS value                            |
| --------------- | ------------------------------------- |
| Clone profile   | `PROFILE=pbms`                        |
| Bootstrap       | `make pbms-setup`                     |
| Run             | `make pbms-run`                       |
| Odoo            | **8069**                              |
| PBMS staff API  | **8050** (not registry `:8001`)       |
| Celery queue    | `bg_task_worker_queue`                |
| Redis DB        | `PBMS_REDIS_DB=1` (registry uses `0`) |
| DBs             | `pbmsdb`, `bgtaskdb` (+ registry DB)  |
| Keycloak client | `openg2p-pbms-local` (optional)       |

`make pbms-run` still starts common infra + a registry (default Farmer) for beneficiary search.

### Commands

```bash
cp .env.example .env
make pbms-setup
make pbms-run
```

Manual:

```bash
make setup PROFILE=pbms
make install-odoo && make install-pbms-bg-tasks
make infra-up
make farmer-setup          # or nsr-setup — registry for search
make pbms-init && make init-pbms-bg-tasks
make pbms-run
```

### PBMS-specific `.env`

| Variable                | Default           | Purpose                                                       |
| ----------------------- | ----------------- | ------------------------------------------------------------- |
| `PBMS_REGISTRY_VARIANT` | `farmer-registry` | Registry DB for bg tasks (`national-social-registry` for NSR) |
| `PBMS_WITH_REGISTRY`    | `true`            | `false` = Odoo + bg tasks only                                |
| `PBMS_STAFF_API_PORT`   | `8050`            |                                                               |
| `USE_EXTERNAL_REDIS`    | `true`            | Set `false` for Docker Redis (common)                         |

Odoo must call the **PBMS** bg-task API, which reads the registry **DB** directly. `make pbms-run` sets this automatically.

### Beneficiary search

Empty until PBMS Celery finishes eligibility (`beneficiary_list_worker` in logs).

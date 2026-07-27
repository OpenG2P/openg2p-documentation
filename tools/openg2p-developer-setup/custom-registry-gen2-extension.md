# Custom Registry Gen2 extension

You choose a slug (example: `disability-registry`). That drives DB names, ports, Keycloak client, and image names - everything else (Postgres, Keycloak realm, IAM, AWE, ID Generator, Celery pattern) is common.

| Item             | Example (`disability-registry`)                       |
| ---------------- | ----------------------------------------------------- |
| Package          | `make extension-package NAME=disability-registry`     |
| Bootstrap        | `make extension-setup NAME=…`                         |
| Run              | `make extension-run NAME=…`                           |
| Extension folder | `disability-extension`                                |
| Python module    | `openg2p_registry_disability_extension`               |
| DBs              | `disability_registry_db`, `disability_master_data_db` |
| Keycloak client  | `disability-registry-staff-portal`                    |
| Default ports    | API `8041`, UI `3020` (auto-increment if taken)       |
| Generated env    | `generated/<NAME>/`                                   |

### Commands

```bash
cp .env.example .env
make setup && make infra-up          # common
make extension-package NAME=disability-registry
make extension-setup NAME=disability-registry
make extension-run NAME=disability-registry
```

Options:

```bash
make extension-package                                    # interactive
make extension-package NAME=… REPO_URL=https://github.com/you/….git
make extension-package NAME=… SETUP=1                     # package + setup
```

### Scaffold layout

```
disability-registry/
├── docker/          # staff API, celery, partner, UI, db-seed, scripts/build.sh
├── helm/openg2p-disability-registry/
└── disability-extension/src/openg2p_registry_disability_extension/
```

### Docker images / Helm (product repo)

```bash
chmod +x docker/scripts/build.sh
./docker/scripts/build.sh
PUSH=1 ./docker/scripts/build.sh --push staff-portal-api/develop.txt
```

```bash
cd ../openg2p-workspace/disability-registry/helm/openg2p-disability-registry
helm dependency update
helm install disability-registry . --namespace openg2p-disability-registry --create-namespace
```

Add `id_types` in openg2p-developer `config/id-generator/default.yaml` if functional IDs are required; restart id-generator.

### Makefile

| Target                                                    | Purpose                               |
| --------------------------------------------------------- | ------------------------------------- |
| `extension-package`                                       | Scaffold                              |
| `extension-setup`                                         | IAM/AWE/migrate/seed (like nsr-setup) |
| `extension-run`                                           | API + Celery + IAM + AWE + UI         |
| `extension-migrate` / `extension-seed` / `extension-init` | Schema / SQL / both                   |

Login still uses common `staff` / `staff`. Re-run `make keycloak-init` if the client was added after first infra start.

---
description: >-
  Shared setup for all local stacks. Module pages only document what differs
  (ports, DBs, commands).
---

# OpenG2P Developer Setup

**Repository:** [https://github.com/OpenG2P/openg2p-developer](https://github.com/OpenG2P/openg2p-developer)

### Quick start

```bash
git clone https://github.com/OpenG2P/openg2p-developer.git
cd openg2p-developer
cp .env.example .env
make setup && make infra-up
```

Then open a module page (e.g. Farmer: `make farmer-setup && make farmer-registry-run`).

Docker Farmer (includes this common stack):

```bash
sed -i 's/^USE_EXTERNAL_REDIS=.*/USE_EXTERNAL_REDIS=false/' .env
docker login   (Docker Hub)
make sync-images && make docker-farmer-up
```

Default login: `staff` / `staff`.

***

### Prerequisites

#### Checklist

* Docker Engine + Compose v2, Git, Make
* Python 3.10+ (3.11+ for AWE/SPAR)
* Node.js 18+ (native staff UI)
* \~20 GB disk; 16 GB+ RAM with Odoo
* GitHub + PyPI + npm access; `docker login   (Docker Hub)` for AWE/Master Data images

#### Hardware / OS

| Resource | Minimum    | Recommended |
| -------- | ---------- | ----------- |
| CPU      | 4 cores    | 8+          |
| RAM      | 8 GB       | 16 GB+      |
| Disk     | 15 GB free | 30 GB+      |

| OS      | Supported                                                        |
| ------- | ---------------------------------------------------------------- |
| macOS   | Yes (`linux/amd64` for Keycloak / ID Generator on Apple Silicon) |
| Linux   | Yes                                                              |
| Windows | WSL2 + Docker Desktop                                            |

Optional macOS: `brew install libpq openssl`.

#### Port check

```bash
for p in 5433 6379 8080 3000 3001 3002 8001 8006 8011 8012 8020 8030 8031 8040 8042 8043 8050 8069; do
  lsof -i tcp:$p >/dev/null 2>&1 && echo "IN USE: $p" || echo "free:   $p"
done
```

***

### Shared infrastructure (`make infra-up`)

| Service      | Port (`.env.example`) | Credentials                                                               |
| ------------ | --------------------- | ------------------------------------------------------------------------- |
| Postgres     | **5433**              | `postgres` / `postgres`                                                   |
| Redis        | 6379                  | none (`USE_EXTERNAL_REDIS=true` by default; set `false` for Docker Redis) |
| MinIO        | 9000 / console 9001   | `admin` / `adminsecret`                                                   |
| Keycloak     | 8080                  | `admin` / `admin`                                                         |
| ID Generator | 8040                  | none                                                                      |

Also used by most app stacks:

| Service              | Port        | Role                             |
| -------------------- | ----------- | -------------------------------- |
| Staff Portal hub     | 3000        | App launcher (Docker Farmer/NSR) |
| IAM Staff Portal API | 8020        | SSO broker                       |
| AWE API / Admin UI   | 8030 / 8031 | Approvals / policies             |

IAM + AWE come with `make *-setup` / `make pbms-setup`, or: `make install-iam && make iam-init`, `make install-awe && make awe-init`.

Full port map (module-specific ports belong on module pages): see `.env.example`.

***

### Users (Keycloak `staff` realm)

| User          | Password | Use                             |
| ------------- | -------- | ------------------------------- |
| `staff`       | `staff`  | Staff UI / Registry / AWE admin |
| `alex.carter` | `pass`   | AWE Stage 1                     |
| `nina.patel`  | `pass`   | AWE Stage 2                     |
| `admin`       | `admin`  | Keycloak console                |

### Auth flow

```
Browser → Staff UI → IAM (:8020) → Keycloak (:8080) → IAM callback → Staff UI
```

Do not refresh `/auth/callback`. IAM + Redis required (OAuth state \~5 min).

### Keycloak

`make infra-up` / `make keycloak-init` creates realm `staff`, users above, and OIDC clients (`iam-staff-portal`, farmer/NSR portal clients, AWE, Bridge, SPAR, PBMS). IAM secret default: `dev-iam-staff-secret`.

```bash
curl -s http://localhost:8080/realms/staff/.well-known/openid-configuration | head
make clean && make infra-up && make iam-init   # reset volumes
```

### Workspace

```
openg2p-developer/         ← this repo
../openg2p-workspace/      ← clones (OPENG2P_WORKSPACE)
generated/                 ← env files
```

```bash
cp .env.example .env
# edit POSTGRES_PORT, OPENG2P_WORKSPACE, …
make generate              # after any .env change
```

### Registry Gen2 (shared)

```
registry-platform/     ← APIs, Celery beat + worker, staff UI
<domain>-extension/    ← Farmer / NSR / custom
```

Celery: beat producers + worker; env under `generated/<variant>/celery-*.env` (queues must match). Functional IDs need ID Generator + `config/id-generator/default.yaml`.

### Common make targets

```bash
make help
make setup / make clone / make generate
make infra-up / make infra-down / make keycloak-init
make sync-images
make status / make logs
make docker-down / make docker-clean
make clean                 # remove volumes
```

Docker Farmer/NSR always start this common stack; variant UI/API ports are on the Farmer / NSR pages (`make docker-farmer-up` / `make docker-nsr-up`).

### Updating versions

Pins live in two places. Do **not** hand-edit the `# BEGIN IMAGE PINS` … `# END IMAGE PINS` block in `.env`  - that block is overwritten by `make sync-images`.

#### 1. Docker images (Compose / `docker-*-up`)

Source of truth: `versions.yaml` → `images:`.

```yaml
# versions.yaml (excerpt)
images:
  farmer_registry_staff_api: openg2p/openg2p-farmer-registry-staff-api:1.2.0
  awe_api: registry.gitlab.com/openg2p/awe/openg2p-awe:0.0.0-develop.67
  # …
```

**Update flow:**

1. Edit the tag(s) under `images:` in `versions.yaml`.
2.  Sync into `.env` / `.env.example`:

    ```bash
    make sync-images
    ```
3.  Recreate the stack so Compose pulls the new tags:

    ```bash
    make docker-farmer-up    # or docker-nsr-up / docker-farmer-continue
    # or: docker compose … up -d --pull always <service>
    ```

For GitLab images (AWE, Master Data), run `docker login   (Docker Hub)` first.

#### 2. Git repo refs (native clone / `make setup`)

Defaults are in `versions.yaml` → `repos.*.ref`. Override per machine in `.env` without editing `versions.yaml`:

| `.env` variable       | Controls                   |
| --------------------- | -------------------------- |
| `REGISTRY_REF`        | `registry-platform`        |
| `IAM_REF`             | `iam-service`              |
| `FARMER_REGISTRY_REF` | `farmer-registry`          |
| `NSR_REF`             | `national-social-registry` |
| `AWE_REF`             | `awe`                      |
| `PBMS_REF`            | `pbms`                     |
| `G2P_BRIDGE_REF`      | `g2p-bridge`               |
| `SPAR_REF`            | `spar`                     |
| `ODOO_REF`            | `odoo17` (usually `17.0`)  |

**Update flow:**

1. Set the ref in `.env` (branch, tag, or commit), e.g. `FARMER_REGISTRY_REF=1.2.0` or `develop`.
2.  Re-clone or pull that profile:

    ```bash
    make clone PROFILE=farmer-registry   # or setup / your PROFILE
    # or manually: cd ../openg2p-workspace/<repo> && git fetch && git checkout <ref>
    ```
3.  Reinstall / regenerate as needed:

    ```bash
    make generate
    make install-registry-extension VARIANT=farmer-registry   # when platform/extension code changed
    make farmer-setup   # or nsr-setup / pbms-setup — only if schema/seed must re-run
    ```

`make clone` uses the `*_REF` values from `.env` when present; otherwise it uses `versions.yaml`.

#### 3. Keep images and git refs aligned

| Mode                                  | What to bump                                                    |
| ------------------------------------- | --------------------------------------------------------------- |
| Docker-only (`make docker-farmer-up`) | `versions.yaml` `images:` + `make sync-images`                  |
| Native (`make farmer-registry-run`)   | `*_REF` in `.env` (and matching extension install)              |
| Both                                  | Update both so UI/API/Celery tags match the git code you expect |

After changing pins, prefer recreating app containers rather than only restarting, so Docker actually pulls new digests.

### Hybrid cluster

Port-forward shared cluster services instead of local infra:

```bash
kubectl port-forward svc/commons-postgresql 5432:5432 -n dev
kubectl port-forward svc/minio 9000:9000 -n dev
kubectl port-forward svc/keycloak 8080:8080 -n dev
```

Then fix hosts/ports in `.env` and `make generate`.

### Multi-module smoke test

```bash
make setup && make infra-up
make farmer-setup && make nsr-setup && make install-odoo
# separate terminals:
make farmer-registry-run
make nsr-registry-run
make pbms-run
make bridge-run
make spar-run
# or best-effort: make up-full
```

### Troubleshooting

| Symptom                          | Fix                                                                   |
| -------------------------------- | --------------------------------------------------------------------- |
| Postgres bind conflict           | Set `POSTGRES_PORT` in `.env`, `make generate`                        |
| Keycloak on Apple Silicon        | Compose uses `platform: linux/amd64`; update Docker Desktop           |
| UI `/api/login` 500              | Use `make *-registry-run` (copies UI env)                             |
| `Login Provider Id not received` | Restart login from UI; don’t refresh callback                         |
| `AWE-ERR-008` on task stats      | Expected with `REGISTRY_AUTH_ENABLED=false`                           |
| Dashboard login loop             | `make generate` then `make *-registry-run`                            |
| `keycloak-init` JSON parse error | Current `keycloak-init.sh` (attributes as JSON); `make keycloak-init` |
| Functional IDs PENDING           | Beat + worker + matching queues + ID type in `default.yaml`           |
| Celery beat not ready            | `make install-registry-extension VARIANT=…`                           |
| `psycopg2-binary` on Python 3.14 | Use ≥2.9.12 or `OPENG2P_PYTHON=python3.13`                            |
| PBMS search empty                | Wait for `beneficiary_list_worker`                                    |
| Bridge mapper fails              | `make seed-spar-farmer-links`; check `spardb.id_fa_mappings`          |
| Bridge/SPAR ports busy           | `bash scripts/free-bridge-spar-ports.sh`                              |

```bash
make clean && make infra-up
```

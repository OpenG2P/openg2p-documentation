# SPAR

| Item             | SPAR value                                           |
| ---------------- | ---------------------------------------------------- |
| Clone            | `make clone PROFILE=spar` (or via `pbms-full-setup`) |
| Run              | `make spar-run`                                      |
| Mapper API       | **8004**                                             |
| Bene portal API  | **8005**                                             |
| DB               | `spardb` / user `sparuser` / `password`              |
| Keycloak clients | `spar-mapper`, `spar-bene-portal`                    |

### Commands

```bash
cp .env.example .env
make setup && make infra-up        # common

cd ../openg2p-workspace/spar/core/mapper-partner-api
virtualenv venv --python=python3 && source venv/bin/activate
pip install -r ../test-requirements.txt greenlet
pip install -e ../models -e ../mapper-core -e .
set -a && source ../../../openg2p-developer/generated/spar/mapper-partner-api.env && set +a
python main.py migrate

cd ../../../openg2p-developer
make spar-run
```

Repeat install/migrate for `core/bene-portal-api` if needed.

SPAR Docker profiles are optional; prefer native above. For ID→bank seeding with Farmer: `make seed-spar-farmer-links` (see PBMS + SPAR + Bridge).

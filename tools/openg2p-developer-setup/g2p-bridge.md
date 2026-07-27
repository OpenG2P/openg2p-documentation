# G2P Bridge

| Item            | Bridge value                              |
| --------------- | ----------------------------------------- |
| Clone           | `make clone PROFILE=bridge`               |
| Run             | `make bridge-run`                         |
| Partner API     | **8002**                                  |
| Example bank    | **8003**                                  |
| Redis DB        | `G2P_BRIDGE_REDIS_DB=2`, example bank `3` |
| DBs             | `g2pbridgedb`, `examplebankdb`            |
| Keycloak client | `g2p-bridge`                              |

### Commands (with PBMS)

```bash
make setup PROFILE=pbms
make clone PROFILE=bridge
make generate && make infra-up     # common
make bridge-run                    # terminal 2
make install-odoo && make pbms-init && make pbms-run   # terminal 3
```

Point PBMS payment / bridge URL at `http://localhost:8002`.

Containers: `make up-bridge` (and `make up-pbms` if needed).

Full eligibility→pay flow: PBMS + SPAR + Bridge.

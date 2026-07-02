# Testing

## Automated tests

The API ships a pytest suite (`core/api/tests`) that runs against SQLite (no
Postgres required) and is executed by the `test` GitHub workflow.

```bash
pip install -e core/api pytest aiosqlite greenlet
# plus the three openg2p-fastapi-common packages (see the workflow / Dockerfile)
pytest -q core/api/tests
```

Coverage:

* **Key service** — algorithm inference (RS256/ES256/EdDSA), kid defaulting to
  the fingerprint, and rejection of private keys, weak RSA, algorithm mismatch,
  and malformed input; JWKS rendering.
* **Lifecycle** — onboarding → `created` (keys not served) → approve → `active`
  (keys served); fetch by `kid`; JWKS; duplicate-onboarding rejection.
* **Rotation** — add a new key + revoke an old one; the revoked key is retained
  but no longer served.
* **Disable/enable** — disabled partners fail-closed on both fetch and JWKS.
* **Reject** — rejected onboarding is never served, and a decided request cannot
  be approved.

## Manual smoke test (no Keycloak)

Run the API with auth disabled to exercise the flow locally:

```bash
cd core/api
cp .env.example .env
# set: COMMON_AUTH_ENABLED=false
#      PARTNER_MANAGER_DB_DATASOURCE=sqlite+aiosqlite:///./pm.db
python -m openg2p_partner_management_api.main migrate
python -m openg2p_partner_management_api.main run
```

Then, against `http://localhost:8000`:

1. `POST /partners/requests/onboarding` with a PEM public key.
2. `GET /keys/<partner_id>` → `404` (not yet approved).
3. `POST /partners/requests/<id>/approve`.
4. `GET /keys/<partner_id>` → `200` with the key; `GET /keys/<partner_id>/jwks.json`.
5. `POST /partners/<partner_id>/disable` → fetch returns `404` again.

## UI

```bash
cd ui && npm install && npm run build   # type-checks and compiles all routes
npm run dev                             # requires IAM_URL + PARTNER_MANAGEMENT_API_URL
```

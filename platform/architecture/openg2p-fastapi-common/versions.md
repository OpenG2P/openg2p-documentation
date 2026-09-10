---
description: Version history of the OpenG2P FastAPI Common framework packages.
---

# Versions

The framework lives in the single repository
[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common) and
publishes installable packages (`openg2p-fastapi-common`, `openg2p-fastapi-auth`,
`openg2p-fastapi-auth-models`, `openg2p-fastapi-partner-auth`). Services install
them from a git ref — the `develop` branch by default, pinnable to a tag via each
service's `FASTAPI_COMMON_REF` build-arg.

<!-- MAINTAINER NOTE: When you add a NEW version row, its Comments cell must
     briefly summarise the differences/additions relative to the PREVIOUS row
     (the older row below — not a full description). Keep it terse. The oldest
     row keeps "Initial tagged release." This table is the single source of
     truth — do not duplicate it on README.md. -->

| Version | Packages | Last Modified | Comments |
| ------- | -------- | ------------- | -------- |
| [develop](https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 09-Sep-2026 | **PgBouncer / asyncpg** — disable the prepared-statement cache when the datasource is `postgresql+asyncpg`, so transaction pooling works. |
| [1.2.1](https://github.com/OpenG2P/openg2p-fastapi-common/tree/1.2.1) | openg2p-fastapi-common | 04-Sep-2026 | **Shared `async_sessionmaker`** — ORM helpers and crypto modules use one session factory instead of creating a sessionmaker per call. Configurable `pool_size` / `max_overflow` on the DB engine. |
| [1.2.0](https://github.com/OpenG2P/openg2p-fastapi-common/tree/1.2.0) | openg2p-fastapi-common | 01-Sep-2026 | **`partner-mgmt` crypto backend** — verify partner JWS by fetching keys from Partner Management, with in-process caching. **`local` crypto backend** — in-process PyJWT; sign from a PKCS#12 keystore, verify against a seeded `partner_keys` table. **DB pool health** — `pool_pre_ping` and `pool_recycle` on by default. **Removed `openg2p-fastapi-partner-auth`** — crypto centralized in `openg2p-fastapi-common`; auth and auth-models packages are not on this release line. **Novu notifications** — notification factory and Novu implementation in-tree. |
| [v1.1.7](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.7) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 19-Jun-2026 | Package version bump — all four packages aligned to 1.1.7. |
| [v1.1.6](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.6) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 06-Apr-2026 | **Security headers middleware** on API responses (toggleable). |
| [v1.1.5](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.5) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 02-Feb-2026 | Refactored application host and port settings. |
| [v1.1.4](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.4) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 03-Nov-2025 | **`openg2p-fastapi-auth-models`** package and `AuthInterface` with staff / beneficiary / agency Keycloak implementations. Shared Pydantic request/response schemas. |
| [v1.1.3](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.3) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth | 19-Aug-2025 | Keymanager helper for remote sign/verify. OAuth / PKCE and login-provider auth fixes. |
| [v1.1.2](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.2) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth | 30-Apr-2025 | Tagging / CI workflow fixes. |
| [v1.1.1](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.1) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth | 02-Dec-2024 | PKCE enable flag and OAuth callback token handling. Login-provider lookup error handling. |
| [v1.1.0](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.1.0) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth | 21-Jun-2024 | First 1.1 line. |
| [v1.0.0](https://github.com/OpenG2P/openg2p-fastapi-common/tree/v1.0.0) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth | 01-May-2024 | Initial tagged release. |

{% hint style="info" %}
The **Last Modified** date for the in-progress `develop` row is updated as work
continues. Tagged package releases carry the date of their git tag.
{% endhint %}

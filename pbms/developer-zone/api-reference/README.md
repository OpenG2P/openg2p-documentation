# API Reference

The OpenG2P PBMS backend exposes its functionality through two FastAPI micro-services. Both are built on the `openg2p-fastapi-common` framework, wrap every call in the standard G2P request/response envelope, and publish an interactive Swagger UI (at `/docs`) and OpenAPI JSON (at `/openapi.json`) that is the authoritative, always-current specification for each service.

The two portal API services are:

| Service | Purpose | Documentation |
| --- | --- | --- |
| Beneficiary Portal API | Powers the beneficiary-facing self-service portal. Serves a beneficiary's benefit programs and program details. Endpoints are authenticated (OIDC / JWT). | [Beneficiary portal APIs](beneficiary-portal-apis.md) |
| Staff Portal API | Backs the Odoo staff UI. Serves the eligibility summary, disbursement envelope/batch views, and beneficiary search. | [Staff portal APIs (for Odoo)](staff-portal-apis-for-odoo.md) |

Both services:

* Run the database migration on container start (`python3 -m <module>.main migrate`) and then serve the app under Gunicorn with the `uvicorn.workers.UvicornWorker` worker class, listening on port `8000` inside the container.
* Share a common request/response envelope defined in `openg2p_fastapi_common.schemas` (see the individual pages for details).

> **Note:** There is no separate "agency app" API service in the PBMS codebase. Agency-facing views are served through the Staff Portal API and the Odoo application; there is no standalone agency-app service to document.

---
description: >-
  The first version of the use-case composite as built: one stateless service,
  its partner API, what it does per request, scaling, audit, and what is not
  built yet.
---

# Composite as Built

{% hint style="info" %}
**Source code:** [github.com/openg2p/agri-stack/tree/develop/composite](https://github.com/openg2p/agri-stack/tree/develop/composite) — the service ([`backend/`](https://github.com/openg2p/agri-stack/tree/develop/composite/backend)), Helm chart ([`deployment/`](https://github.com/openg2p/agri-stack/tree/develop/composite/deployment)), use cases ([`use-cases/`](https://github.com/openg2p/agri-stack/tree/develop/composite/use-cases)) and console ([`ui/`](https://github.com/openg2p/agri-stack/tree/develop/composite/ui)); test and uninstall scripts in the repository's [`scripts/`](https://github.com/openg2p/agri-stack/tree/develop/scripts). Built October 2026.
{% endhint %}

The design is on the [use-case composite](../design/use-case-composite.md) page. This page says what the first version does. How to call it is in the [partner guide](../guides/partner-guide.md); how to configure it in the [composite configuration guide](../guides/composite-configuration.md).

## Service

* One FastAPI service, `openg2p-agri-composite` (image `openg2p/openg2p-agri-composite-api`), built on [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common). The partner API is stateless; a database is used only by the optional [console](../guides/composite-console.md) (its call log).
* **Use cases are YAML files** in a Helm-managed ConfigMap (edited in Rancher's YAML values editor), validated strictly at load and reloaded within 30 seconds of a change; only `published` ones are served.
* **Registries are configured as `controller → DCI search URL`** (`composite.registries` in Helm, `AGRI_COMPOSITE_REGISTRIES` in the environment), because Partner Management holds no registry endpoints yet. Nothing about a registry is hard-coded.
* **Its own identity:** partner ID `agri-composite` in PM (`PARTNER_AGRI_COMPOSITE`), with its signing key in the Kubernetes Secret `agri-composite-signing` (a `.p12`).

## Partner API

`POST /composite/v1/use-cases/{use_case}[@major]/query` with a signed envelope (detached JWS over `{header, message}`, the partner's PM key, as for registry DCI searches):

* `message.subject` (type and value), `message.parameters`, and `message.consent_jws`: **one consent with a grant per registry** (see [consent model](../architecture/consent-model.md)).
* `GET /composite/v1/use-cases` and `/{use_case}` describe the published use cases (input, parameters, sources, output fields, the consent grants needed).
* `GET /ping`: health check.

The full request and response, with examples, are in the [partner guide](../guides/partner-guide.md).

## What it does per request

1. Verifies the partner's signature against PM (key `PARTNER_<SENDER_ID>`); checks the message is fresh (`header.message_ts` within 300 seconds) and addressed to the composite.
2. Checks the partner is in the use case's `allowed_partners` (a stand-in for the PM policy association, which PM doesn't have yet).
3. Validates the input (subject type, parameters) and applies a per-partner rate limit.
4. Verifies the consent: the partner's signature on it, the subject is the one asked about, its validity window, and a grant with the use case's required [data scopes](../guides/composite-configuration.md#data-scopes) for every mandatory source. An optional source without them is reported `denied` and not called.
5. Calls the sources in dependency order (`depends_on`), in parallel within a level, each a DCI sync search signed with the **composite's own PM key**, carrying the partner's consent unchanged and the partner's ID in `header.meta.on_behalf_of`. Per-source timeout and retries; overall timeout.
6. Maps the results (JSONPath), computes derived fields (`sum`, `count`, `min`, `max`, `first`, `round`), and returns a response signed by the composite, with a status per source (`ok`, `no_record`, `denied`, `unavailable`, `error`).
7. Sends audit events (request, each source call, response; no data and no subject identifiers) to the [Audit Manager](../../platform/platform-services/audit-manager/README.md) as CloudEvents, without ever blocking the request.

**Each registry still decides.** It verifies the composite's signature, validates its own grant in the consent with CM, checks that the consent's subject is the person searched (directly, or through its own data, e.g. a farmer ID recorded with the farmer's FAN), and clamps the record to the effective scopes.

No partner data is stored. Logs carry the request ID, use case, partner, statuses and timings only; with the console on, the same (never the subject, the consent or any data) goes to its call log.

## Sample use case: `loan-profile`

By Fayda FAN or farmer ID; optional crop year and season.

* **Sources:** the farmer (Farmer Registry, mandatory), then the farmer's season summaries and crop seasons (Crop Sown Registry, optional, both depending on the farmer).
* **Returns:** the farmer's identity and location, land parcels and total land, declared main crops, crop seasons, season summaries and total area sown.

The file and its settings are explained in the [composite configuration guide](../guides/composite-configuration.md#the-loan-profile-use-case).

## Scaling

* Stateless pods behind a CPU-based autoscaler (1–5 pods at 70% CPU by default); memory-based autoscaling is off on purpose (Python's memory does not shrink, so it would never scale back down).
* A pooled HTTP client per worker (2 gunicorn workers per pod by default); partner keys cached per pod (soft TTL 300 s, last-known-good for 6 hours during a PM outage).
* No database; startup never calls a registry.
* Rate limits are per pod and worker: with N pods and W workers the effective ceiling is up to N × W times the configured rate. Limits across pods and daily quotas need shared counters (to do).
* The image runs as uid 1001 with a read-only root filesystem.

## Audit

With `AGRI_COMPOSITE_AUDIT_MANAGER_URL` set (the chart sets `http://commons-services-auditmanager:80`), the composite posts CloudEvents to `/v1/auditmanager/events`:

| Event | When | Context |
| --- | --- | --- |
| `request` | The request is accepted, or rejected before any source is called | Outcome (`success`, `denied`, `failure`) and reason code |
| `source_call` | Each registry call | Source, controller, status, attempts, duration |
| `response` | Every response | HTTP status, duration, status per source |

Events are linked by the request ID. They are sent in the background; failures are logged and never fail the request. A use case can limit which events it sends (`audit.events`).

## Not built yet

* the checks when a use case is published (against PM policies, which PM doesn't hold yet);
* data-blind mode;
* daily quotas and rate limits across pods (shared counters);
* registry endpoints and policies held in PM rather than in configuration;
* calling the crop sources in parallel with the farmer when the partner already sends a farmer ID;
* a configuration UI;
* a machine-readable response schema per use case (a JSON Schema endpoint); the describe endpoint lists output field names only.

These are tracked in [TODOs and open items](../open-items/README.md#composite).

---
description: >-
  The Composite as built and configured for Agri Stack: the service,
  its identity, the registries it calls, the consent mode, the loan-profile use
  case, audit, scaling, and what is not built yet.
---

# Composite

{% hint style="info" %}
**Source code:** [github.com/openg2p/agri-stack/tree/develop/composite](https://github.com/openg2p/agri-stack/tree/develop/composite): the service ([`backend/`](https://github.com/openg2p/agri-stack/tree/develop/composite/backend)), Helm chart ([`charts/`](https://github.com/openg2p/agri-stack/tree/develop/composite/charts)), use cases ([`use-cases/`](https://github.com/openg2p/agri-stack/tree/develop/composite/use-cases)) and console ([`ui/`](https://github.com/openg2p/agri-stack/tree/develop/composite/ui)); the partner test, Exchange setup and uninstall scripts are in [`scripts/`](https://github.com/openg2p/agri-stack/tree/develop/scripts).
{% endhint %}

The Composite is the partners' entry point. It serves approved use cases (e.g. `loan-profile@1`) by querying several registries with one consent and returning one signed response. It runs in the [Exchange](exchange.md).

The design is on the [Composite](../design/composite.md) page. Every setting, the use-case file format and the error codes are in the [Composite configuration guide](../guides/composite-configuration.md); how partners call it is in the [partner guide](../guides/partner-guide.md). This page says what is built and what Agri Stack sets.

## Service

* One FastAPI service, `openg2p-agri-composite` (image `openg2p/openg2p-agri-composite-api`), built on [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common). The partner API is stateless. A database is used only by the optional [console](../guides/composite-console.md), for its call log.
* **Use cases are YAML files** in a Helm-managed ConfigMap (edited in Rancher's YAML values editor), validated strictly at load and reloaded within 30 seconds of a change. Only `published` ones are served.
* **Registries are configured as controller → DCI search URL** (`composite.registries`), because Partner Management holds no registry endpoints yet. Nothing about a registry is hard-coded.
* **No partner data is stored.** Logs carry the request ID, use case, partner, statuses and timings only. The console's call log holds the same, never the subject, the consent or any data.

## What Agri Stack sets

| Setting | Value | Default? |
| --- | --- | --- |
| Composite partner ID (`global.compositePartnerId`) | `agri-composite`, in PM as `PARTNER_AGRI_COMPOSITE` | Yes |
| Signing key | Secret `agri-composite-signing` (a `.p12`, its `kid` registered in each PM), created by the [Exchange setup](../guides/exchange-setup.md) | Secret name is the default |
| Consent mode (`composite.consent.mode`) | `exchange` | Yes |
| Exchange CM URL | `http://commons-services-cm-partner-api` (the Exchange's own CM) | Yes |
| `composite.registries.farmer-registry.url` | The Farmer Registry's partner API, e.g. `https://partner-fr.trial.openg2p.org/dci/registry/sync/search` | No default: set at install |
| `composite.registries.crop-sown-registry.url` | The Crop Sown Registry's, e.g. `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search` | No default: set at install |
| Allowed browser origins | The partner portal, `https://consent-partner-portal.<namespace>.openg2p.org` | Yes |
| Audit Manager URL | `http://commons-services-auditmanager:80` | Yes |
| Console | On, database `agri_composite` in the commons Postgres | Yes |

The form fields are listed in [deploying on a cluster](../guides/deployment.md#use-case-composite) and the full values in [Composite configuration](../guides/composite-configuration.md#helm-values).

## Consent mode

The consent mode is `exchange` (the default). The partner is onboarded and bound only at the Exchange. The Composite presents the partner's consent, or the ID of a consent the Exchange CM holds (`consent_id`), to the Exchange CM with `issue_receipts: true` and the use case's scopes. The Exchange CM returns one signed **consent token** per registry. The Composite sends each registry only its own consent token, which the registry validates at its own department CM.

In addition:

* the Composite signs each registry call with its own key and names the partner in `header.meta.on_behalf_of`;
* a partner-signed consent must have been issued within the CM's freshness window (300 seconds by default), so partners sign a fresh consent for each request.

Request and response details: [Composite configuration](../guides/composite-configuration.md#consent-mode).

## What it does per request

1. Verifies the partner's signature against PM (key `PARTNER_<SENDER_ID>`). Checks the message is fresh (`header.message_ts` within 300 seconds) and addressed to the Composite.
2. Checks the partner is in the use case's `allowed_partners`.
3. Validates the input (subject type, parameters) and applies a per-partner rate limit.
4. Checks the consent. For a `consent_jws`: the partner's signature, the subject, the validity window, and a grant with the use case's required [data scopes](../guides/composite-configuration.md#data-scopes) for every mandatory source. A `consent_id` is checked by the Exchange CM (active, in its validity, obtained by this partner, about this subject).
5. Gets a consent token per registry from the Exchange CM. A deny fails the request; a mandatory source without a consent token fails it too; an optional one is reported `unavailable`.
6. Calls the sources in dependency order (`depends_on`), in parallel within a level, each a DCI sync search signed with the Composite's key and carrying that registry's consent token. Per-source timeout and retries; overall timeout.
7. Maps the results, computes derived fields, and returns a response signed by the Composite, with a status per source (`ok`, `no_record`, `denied`, `unavailable`, `error`).
8. Sends audit events to the Audit Manager, without ever blocking the request.

**Each registry still decides.** It verifies the Composite's signature at its own PM, validates its consent token at its own CM (with its standing policy for the Composite), checks that the consent's subject is the person searched, and cuts the record down to the effective scopes.

## Use cases

One use case ships, `loan-profile` (version `1.0.0`, purpose `credit-assessment`).

| | |
| --- | --- |
| **Input** | A farmer by `FAYDA_FAN` or `FARMER_ID`; optional `crop_year` and `season` |
| **Sources** | `farmer` (Farmer Registry, mandatory); then `season_summaries` and `crop_seasons` (Crop Sown Registry, optional, both depending on `farmer`) |
| **Returns** | The farmer's identity and location, land parcels and total land, declared main crops, crop seasons, season summaries and total area sown |
| **Allowed partners** | `[bank-a]`, the test partner. Edit `composite.useCases` in **Edit YAML** to add real partners |

The scopes it needs from each registry are on the [Farmer Registry](farmer-registry.md#what-agri-stack-reads) and [Crop Sown Registry](crop-sown-registry.md#what-agri-stack-reads) pages. The file, setting by setting: [the `loan-profile` use case](../guides/composite-configuration.md#the-loan-profile-use-case). Adding a registry: [adding a data source](../guides/adding-a-data-source.md).

## Audit

The Composite posts CloudEvents to the Audit Manager's `/v1/auditmanager/events`. Events carry no data and no subject identifiers, and are linked by the request ID.

| Event | When | Context |
| --- | --- | --- |
| `request` | The request is accepted, or rejected before any source is called | Outcome (`success`, `denied`, `failure`) and reason code |
| `source_call` | Each registry call | Source, controller, status, attempts, duration |
| `response` | Every response | HTTP status, duration, status per source |

Events are sent in the background; a failure is logged and never fails the request. A use case can limit which events it sends (`audit.events`).

## Scaling

* Stateless pods, one replica by default. A CPU-based autoscaler is opt-in (1–5 pods at 70% CPU). Memory-based autoscaling is off on purpose: Python's memory does not shrink, so it would never scale back down.
* Two gunicorn workers per pod by default, each with a pooled HTTP client. Partner keys are cached per pod (300 seconds, last-known-good for 6 hours during a PM outage).
* Rate limits are per pod and worker: with N pods and W workers the effective ceiling is up to N × W times the configured rate.
* The image runs as uid 1001 with a read-only root filesystem. Startup never calls a registry.

## Not built yet

* Checks when a use case is published (against PM policies, which PM does not hold yet).
* Data-blind mode.
* Daily quotas and rate limits across pods (shared counters).
* Registry endpoints and policies held in PM rather than in configuration.
* Calling the crop sources in parallel with the farmer when the partner already sends a Farmer ID.
* A configuration UI.
* A machine-readable response schema per use case. The describe endpoint lists output field names only.

These are tracked in [TODOs and open items](../open-items/README.md#composite).

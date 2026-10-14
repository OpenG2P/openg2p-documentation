---
description: >-
  Proposal: registries sharing data with each other (registry to registry),
  using the registry platform's outgestion and ingestion. Reference design:
  crop activity from the Crop Sown Registry kept in the Farmer Registry; the
  gaps to close; how it would be set up; mirrors the other way.
---

# Registry Data Sync

{% hint style="warning" %}
**Status: proposal, not in use.** Registries do not share data with each other today. This page is the reference design, the gaps, and [how it would be set up](#how-it-would-be-set-up). The relay it needs is not built.
{% endhint %}

## The need

Registries are owned by different departments, and some data recorded in one is needed in another. Two directions come up:

* **Into the Farmer Registry (FR).** The FR is the farmer's single record, the one most services ask first, e.g. "is this an active farmer?". Facts recorded elsewhere, such as what the farmer sowed last season, are worth keeping on that record, read-only, with the other registry staying their source of truth.
* **Out of the Farmer Registry.** The Crop Sown Registry (CSR), and later Livestock and others, need basic farmer details (demographics, household size) to search, filter and link their own records, and to keep working when the FR is slow or briefly down (see [mirrors](#the-other-direction-mirrors-of-farmer-data)).

This is a department operating on another department's data, not a partner asking for one farmer's data: that is the [Composite](../composite/README.md)'s job. In the [architecture](../architecture/README.md#components-and-who-talks-to-whom) it is **path C**: one registry is simply a partner of the other.

## Reference design: crop activity in the Farmer Registry

The showcase for an Agri Stack install: the FR keeps a read-only **Crop activity** section on each farmer, fed by the CSR.

| FR field (section "Crop activity, from the Crop Sown Registry") | From the CSR | Kept up to date |
| --- | --- | --- |
| Last reported season (crop year, season) | the latest crop sown record of the farmer | on each approved CSR record |
| Crops sown that season | that record | on each approved CSR record |
| Area sown that season (ha) | the farmer's season summary | nightly |
| Cluster | the farmer's cluster membership | on each approved CSR record |
| Active farmer (sowed in the last 2 seasons) | the farmer's season summaries | nightly |
| Updated at, CSR record ID | the event | with each update |

The CSR stays the source of truth for these facts; the FR shows them because they describe the farmer. The section is read-only in the FR: no staff edits, no change requests other than the sync's.

### How the data flows

1. **On a trigger.** A crop sown record is approved in the CSR. The CSR's **outgestion** renders it with a template into a small event (Farmer ID, season, crops, cluster, record ID, version) and publishes it to a WebSub topic for the register. A **relay** subscribed to that topic checks the hub's signature, signs the event as the partner `crop-sown-registry`, and posts it to the FR's **ingestion** API (`/partner/ingest_data`). The FR classifies it as an **update** of the farmer with that Farmer ID, applies its template to the Crop activity section, and the change request is approved automatically (the section allows it for partners). Within seconds, idempotent by the CSR record's version.
2. **Periodically.** Each night the relay searches the CSR's partner API (DCI) for season summaries changed since its last run, as a partner of the CSR, and ingests them the same way. This fills the totals and the active flag, which one record cannot give, and catches anything missed while a service was down, including records the CSR loaded without a change request (sample data, bulk loads), which outgestion does not publish.

```
CSR: record approved ─► outgestion (template) ─► WebSub hub ─► relay ─► FR /partner/ingest_data ─► change request (auto) ─► Crop activity
CSR partner API (DCI search, nightly) ◄──────────────────────── relay ─┘
```

### Who allows it

A department-level agreement, not each farmer's consent: the CSR shares these fields with the FR for one purpose (keeping the farmer record), and the FR accepts them only from the CSR.

* **The FR's Partner Management** holds the CSR as a partner (its key). The FR's ingestion accepts only signed events from an active partner.
* **The CSR's Partner Management and Consent Manager** hold the relay (acting for the FR) as a partner with a policy for the nightly search: these scopes only, this purpose.
* The Consent Manager has no rule yet for sharing on a standing permission instead of a consent: the [standing permission for a purpose](../open-items/README.md) open item. Until then the nightly search needs that rule, and the trigger path rests on the CSR's outgestion configuration (the topic and its template decide what leaves).

## What has to be built

**The relay** (in Agri Stack, a small service with its own chart; off by default). It subscribes to the CSR's topic, verifies the hub's signature, signs and forwards events to the FR's ingestion, and runs the nightly search. It stays configuration-driven: source topic, target ingestion URL, partner ID and key, schedule.

**Gaps in the registry platform** (so that the relay is not needed, or is thinner):

| Gap | Today | Needed |
| --- | --- | --- |
| A WebSub subscriber in ingestion | Ingestion is a signed partner API only; nothing answers the hub's subscription check or accepts its deliveries | An ingestion endpoint that subscribes to a topic, verifies the hub's signature and maps the subscription to a partner |
| Or: outgestion that delivers to a partner | Outgestion publishes to a hub, unsigned | A "deliver to partner" topic that signs with the registry's key and posts to the partner's ingestion directly |
| Update-only ingestion | Classification picks add or update by whether the record exists | A data model that can only update: an unknown Farmer ID is rejected, never creates a farmer (configure no intake form for it until then) |
| Versioned, idempotent updates | Each event becomes a change request | Skip events older than the record's last applied version |
| Scheduled pulls | None | A scheduled DCI search of another registry, ingested like an event |
| Scope filtering on outgoing events | Applies to DCI search only; the template decides what leaves | Filter events by the agreed data scopes |
| Monitoring | Per-stage statuses in tables | Lag and failed events per subscription |

**In the Consent Manager:** the standing permission for a purpose (see above).

With the first two rows in the platform, registry-to-registry sync becomes configuration on both sides: a topic and template in the source, a data model and template in the target, and partner entries in both.

## How it would be set up

The steps for the reference design, once the relay exists. Field names are illustrative; map them from your registers' actual fields. Both registries already have what they need (outgestion in the CSR, ingestion in the FR); the relay between them is not built.

| Step | Where | What |
| --- | --- | --- |
| 1 | CSR's install | WebSub hub; an outgestion template and topic for crop sown records |
| 2 | FR's install | The Crop activity section; the CSR as a partner; an update-only ingestion data model and template |
| 3 | Relay | Subscribe to the CSR's topic; sign and forward to the FR |
| 4 | CSR's install | The relay as a partner of the CSR, for the nightly search |
| 5 | Both | Check |

### Crop Sown Registry: publish crop sown records

**WebSub hub.** The CSR's commons-services must have **Install WebSub?** on (the default for a department install), and the CSR pointed at its hub.

**Outgestion template.** In the CSR staff portal, **Configuration → Outgest configurations → Templates**: a Jinja template for the crop sown register that turns an approved record into the event the FR will ingest. Only what the FR may receive leaves; the template is the filter.

```jinja
{
  "header": {
    "message_id": "{{ change_request_id }}",
    "message_ts": "{{ approved_at }}",
    "sender_id": "crop-sown-registry",
    "action": "crop-activity"
  },
  "message": {
    "farmer_id": "{{ record.farmer_reference.farmer_id }}",
    "crop_activity": {
      "crop_year": {{ record.crop_season.crop_year }},
      "season": "{{ record.crop_season.season }}",
      "crops": {{ record.crops | map(attribute="crop_code") | list | tojson }},
      "cluster_id": "{{ record.cluster_id }}",
      "source_record_id": "{{ internal_record_id }}",
      "source_version": {{ record_version }}
    }
  }
}
```

**Topic.** **Configuration → Outgest configurations → Topics**: a `REGISTER` topic for the crop sown register and this data model, e.g. `csr.crop-activity`. It registers itself with the hub and becomes active; from then on every approved crop sown record is rendered and published.

### Farmer Registry: accept crop activity

**The section.** Add a **Crop activity** section to the Farmer register (last reported season, crops, area sown, cluster, active farmer, updated at, CSR record ID), read-only for staff. Set the section's **auto-approve for partner** (`cr_auto_approve_for_partner`), so the sync's change requests are applied without a staff step; staff never edit this section.

**The CSR as a partner.** In the FR's Partner Management, onboard `PARTNER_CROP_SOWN_REGISTRY` with the relay's signing key. The FR's ingestion accepts only signed messages from an active partner.

**Ingestion configuration** (the FR's ingestion tables):

| Table | Setting |
| --- | --- |
| `data_models` | `crop_activity_v1`, identified by `header.action = crop-activity` |
| `incoming_model_key_paths` | message ID `$.body.header.message_id`, sender `$.body.header.sender_id`, signature `$.body.signature`, signed payload `$.body.message` |
| `incoming_model_register_semantic_patterns` | register Farmer; record identifier `$.body.message.farmer_id` (the Farmer ID) |
| `incoming_model_semantic_patterns` | **section** Crop activity (update), business payload `$.body.message.crop_activity`; **no intake form** |
| `incoming_templates` | Jinja from `crop_activity` to the section's fields |

{% hint style="danger" %}
Configure **no intake form** for this data model. Ingestion picks add or update by whether the farmer exists; with an intake form, an event for an unknown Farmer ID would create a farmer. Without one, it is rejected. (An update-only data model is one of the [platform gaps](#what-has-to-be-built).)
{% endhint %}

### Relay: from the CSR's hub to the FR's ingestion

*Not built yet.* Its configuration would be:

| Setting | Example |
| --- | --- |
| Hub and topic | the CSR's WebSub hub, `csr.crop-activity`; the relay subscribes with a secret |
| Target | the FR's ingestion, `https://partner-fr.<department domain>/partner/ingest_data?data_model=CROP_ACTIVITY_V1` |
| Sign as | partner `crop-sown-registry`, with the key onboarded in the FR (detached JWS over `message`) |
| Nightly search | the CSR's partner API, season summaries changed since the last run; schedule e.g. 02:00 |

It retries on failure and skips events older than the farmer's last applied `source_version` (what it does is in [how the data flows](#how-the-data-flows)).

### Crop Sown Registry: allow the nightly search

The nightly search is a partner's search like any other: in the **CSR's** Partner Management, onboard the relay (acting for the FR, e.g. `PARTNER_FARMER_REGISTRY_SYNC`); in the **CSR's** Consent Manager, a binding and policy for it with only the season summary scopes and the purpose "farmer record maintenance". It rests on the standing permission described in [who allows it](#who-allows-it), not built yet.

### Check

1. Approve a crop sown record in the CSR for a farmer that exists in the FR (e.g. `FR-0007`).
2. In the CSR's outgoing messages, the record is transformed and published.
3. In the FR, a change request from the partner appears for that farmer, approved; the Crop activity section shows the season.
4. Repeat with a Farmer ID unknown to the FR: the FR rejects it; no farmer is created.
5. After the nightly run, area sown and the active flag are filled.

## The other direction: mirrors of farmer data

The earlier proposal, out of the FR: the CSR (and others) keep a read-only **mirror register** of farmer details from the FR, fed the same way (FR outgestion → CSR ingestion), filtered to the agreed [data scopes](../../products/registry/registry/design/data-scopes.md), upserted by the FR's Farmer ID and version, and retired (marked inactive, never deleted) when the FR retires the farmer. A new subscriber first loads a snapshot with a paged search, then follows the stream. It needs, besides the gaps above, a **mirror register** type in the platform (read-only, sourced from another registry).

| Option considered | Why not (for now) |
| --- | --- |
| Shared database or read replica | Couples the registries; registries share data, never code |
| Query through the Composite | Good for one farmer; a department cannot search or filter locally |
| Database change capture (e.g. Debezium) | Heavy; subscribers become coupled to the source's tables |
| Raw Kafka feed | Kafka is in commons and could replace WebSub as the transport later; the design stays the same |

## Open questions

* How fresh must the data be: seconds (trigger), or is nightly enough?
* How many farmers and records, and how often do they change?
* Which other facts belong on the FR record (e.g. livestock holdings once a Livestock registry exists)?
* Can a registry add its own fields to a mirrored record, or must those always live in its own registers?

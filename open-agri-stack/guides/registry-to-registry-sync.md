---
description: >-
  How to set up one registry feeding another with the registry platform's
  outgestion and ingestion: crop activity from the Crop Sown Registry into the
  Farmer Registry. A preview: the relay it needs is not built yet.
---

# Registry-to-Registry Sync

{% hint style="warning" %}
**Preview, not yet usable end to end.** Both registries have what they need (outgestion in the source, ingestion in the target), but the two do not connect directly: a small **relay** is needed in between, and it is not built. The design and the gaps are in [registry data sync](../design/registry-data-sync.md). Field names below are illustrative; map them from your registers' actual fields.
{% endhint %}

The example: the **Crop Sown Registry (CSR)** keeps a read-only **Crop activity** section of each farmer up to date in the **Farmer Registry (FR)**, on each approved crop sown record (trigger) and nightly (reconciliation).

| Step | Where | What |
| --- | --- | --- |
| 1 | CSR's install | WebSub hub; an outgestion template and topic for crop sown records |
| 2 | FR's install | The Crop activity section; the CSR as a partner; an update-only ingestion data model and template |
| 3 | Relay | Subscribe to the CSR's topic; sign and forward to the FR |
| 4 | CSR's install | The relay as a partner of the CSR, for the nightly search |
| 5 | Both | Check |

## 1. Crop Sown Registry: publish crop sown records

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

## 2. Farmer Registry: accept crop activity

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
Configure **no intake form** for this data model. Ingestion picks add or update by whether the farmer exists; with an intake form, an event for an unknown Farmer ID would create a farmer. Without one, it is rejected. (An update-only data model is one of the [platform gaps](../design/registry-data-sync.md#what-has-to-be-built).)
{% endhint %}

## 3. Relay: from the CSR's hub to the FR's ingestion

*Not built yet.* Its configuration would be:

| Setting | Example |
| --- | --- |
| Hub and topic | the CSR's WebSub hub, `csr.crop-activity`; the relay subscribes with a secret |
| Target | the FR's ingestion, `https://partner-fr.<department domain>/partner/ingest_data?data_model=CROP_ACTIVITY_V1` |
| Sign as | partner `crop-sown-registry`, with the key onboarded in step 2 (detached JWS over `message`) |
| Nightly search | the CSR's partner API, season summaries changed since the last run; schedule e.g. 02:00 |

For each event it verifies the hub's signature, adds the signature, and posts it to the FR. It retries on failure and skips events older than the farmer's last applied `source_version`.

## 4. Crop Sown Registry: allow the nightly search

The nightly search is a partner's search like any other: in the **CSR's** Partner Management, onboard the relay (acting for the FR, e.g. `PARTNER_FARMER_REGISTRY_SYNC`); in the **CSR's** Consent Manager, a binding and policy for it with only the season summary scopes and the purpose "farmer record maintenance". The Consent Manager does not yet allow sharing on such a standing permission without each farmer's consent: see the [open item](../open-items/README.md).

## 5. Check

1. Approve a crop sown record in the CSR for a farmer that exists in the FR (e.g. `FR-0007`).
2. In the CSR's outgoing messages, the record is transformed and published.
3. In the FR, a change request from the partner appears for that farmer, approved; the Crop activity section shows the season.
4. Repeat with a Farmer ID unknown to the FR: the FR rejects it; no farmer is created.
5. After the nightly run, area sown and the active flag are filled.

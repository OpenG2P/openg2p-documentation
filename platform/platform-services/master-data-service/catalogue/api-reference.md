---
description: >-
  The /catalogue read and write APIs of MDS as Catalogue: lists, values,
  versions, diffs, geography, crosswalk, boundaries, releases, the change feed,
  drafts and approvals
---

# API Reference

The catalogue APIs live under **`/catalogue`**. They follow the same conventions as
the rest of MDS (see the [MDS API Reference](../api-reference.md)). Every endpoint
is also described in the service's OpenAPI page.

* Every call is a **`POST`**, including reads, with the OpenG2P envelope:

  ```json
  { "request_header": { "request_id": "…", "…": "…" },
    "request_body": { "request_payload": { }, "pagination_request": { "page_size": 100, "current_page": 1 } } }
  ```

  `pagination_request` is optional and used only by the paged reads
  (`get_list_values`, `get_geo_units`; default 1000 per page).
* The response is
  `{ "response_header": { "response_status", "response_error_code", "response_error_message", … }, "response_body": { "response_payload", "pagination_response"? } }`.
* Every call needs a **bearer token** from the deployment's Keycloak; reads need
  authentication only, writes need a permission (see
  [Change control](change-control.md#permissions)). The one exception is the
  [AWE callback](#awe-callback).
* Errors come back **inside the envelope** with HTTP 200,
  `response_status: "ERROR"` and a code:

| Code | Meaning |
|---|---|
| `G2P-CAT-400` | Bad request: validation failed (including an `x-list-ref` code that is not an active value of the referenced list's version in effect), no changes to submit, `effective_from` earlier than the latest published version's |
| `G2P-CAT-403` | Not allowed: maker-checker (compared by stable user id), or no bearer token to forward to AWE |
| `G2P-CAT-404` | List, value, version, unit, release or draft not found |
| `G2P-CAT-409` | State conflict: a draft is already open, the draft is not in the right status, approval runs through AWE, the boundary store is not configured, a boundary key is recorded by another version, or a write hit a published (immutable) row |
| `G2P-CAT-502` | AWE could not be reached when opening an approval request |
| `G2P-CAT-500` | Unexpected error |

A write that the database refuses because the row belongs to a published version
(trigger error `G2P-CAT-IMMUTABLE`) is returned as `G2P-CAT-409` with a message
starting `immutable:`.

The examples below show only `request_payload` and `response_payload`.

{% hint style="info" %}
**The existing `/geo` and `/attributes` endpoints remain** with the same paths and
shapes, returning the current published data. Two additive fields carry version
information: `current_version_no` on each list in `/attributes/get_all_attributes`
(null for a list never published, which is also listed), and `list_versions`
(`{attribute_id: version_no}`) in `/attributes/get_attribute_values`. The `/geo`
reads carry no version metadata; use `get_catalogue_config` or `get_geo_versions`.
Legacy writes now go into a draft; see
[What the legacy write endpoints do now](change-control.md#what-the-legacy-write-endpoints-do-now).
{% endhint %}

## Choosing a version

Every read that returns versioned data accepts **at most one** of:

| Field | Type | Meaning |
|---|---|---|
| `version` | integer, `"latest"` or `"draft"` | A version number; the latest published version in effect (the default); or the open draft |
| `as_of` | date-time (ISO 8601) | The published version in effect at that moment |
| `release` | string | A catalogue release code; the list or geography is read at the version the release pins (`G2P-CAT-404` if it pins none) |

Every such response includes a **`version`** object (VersionInfo):

```json
"version": {
  "version_no": 4,
  "status": "PUBLISHED",
  "base_version_no": 3,
  "effective_from": "2026-09-15T00:00:00Z",
  "published_at": "2026-09-14T11:02:37Z",
  "is_latest": true,
  "change_note": "Add 2026 releases",
  "created_by": "5f0c…e1", "created_by_name": "Abebe Kebede", "created_at": "…",
  "updated_by": "5f0c…e1", "updated_by_name": "Abebe Kebede", "updated_at": "…",
  "submitted_by": "5f0c…e1", "submitted_by_name": "Abebe Kebede", "submitted_at": "…",
  "decided_by": "9a41…7c", "decided_by_name": "Tigist Alemu", "decided_at": "…",
  "decision_note": "OK",
  "approval_ref": null
}
```

`is_latest` is true for the version in effect now. The `*_by` fields hold the
**stable user id** (the token's `sub`) or a system name (such as `migration`,
`country-pack-loader` or `awe`); this is what maker ≠ checker compares. The
`*_by_name` fields hold the display name the user had when they acted, for
showing to people; they are `null` for a system actor and for rows written before
names were recorded whose user the change log does not name. Show the name and
fall back to the id. Geography versions add `country`, `owner_org`,
`boundary_objects` and `unit_count`.

The `status` of a version is `DRAFT`, `SUBMITTED`, `PUBLISHED`, `REJECTED` or
`DISCARDED`. Version numbers are never reused.

## Lists

A list is named by `list_code` (its code or its id) in every request.

### `POST /catalogue/get_lists`

All lists with their owner, current published version (in effect now), highest
published version, open draft and a summary of their attribute schema.
`include_unpublished` (default `true`) includes lists never published.

```json
// request
{}
// response
{
  "lists": [
    {
      "list_id": "SEED_VARIETY",
      "list_code": "SEED_VARIETY",
      "display": "Seed variety",
      "display_i18n": { "am": "የዘር ዝርያ" },
      "description": "Released crop varieties",
      "owner_org": "MOA-CROP",
      "is_hierarchical": false,
      "attribute_schema": { "…": "…" },
      "attribute_schema_summary": {
        "properties": ["agro_ecological_zones", "crop", "maturity_days", "release_year"],
        "required": ["crop", "maturity_days"],
        "list_refs": { "crop": "CROP_COMMODITY", "agro_ecological_zones[]": "AGRO_ECOLOGICAL_ZONE" }
      },
      "current_version_no": 7,
      "latest_published_version_no": 7,
      "open_draft_version_no": 8,
      "open_draft_status": "SUBMITTED"
    }
  ]
}
```

### `POST /catalogue/get_list`

One list, with its code, labels, hierarchy flag and attribute schema **as they are
in the selected version**, plus that version's metadata.

```json
// request
{ "list_code": "SEED_VARIETY", "version": "latest" }
// response
{
  "list": { "list_id": "SEED_VARIETY", "list_code": "SEED_VARIETY", "display": "Seed variety", "…": "…" },
  "version": { "version_no": 7, "status": "PUBLISHED", "effective_from": "2026-09-15T00:00:00Z", "is_latest": true, "…": "…" }
}
```

With no selector and no published version in effect, `version` is null.

### `POST /catalogue/get_list_values`

The values of a list at a version, ordered by `sort_order`. Paged.

| Field | Type | Required | Description |
|---|---|---|---|
| `list_code` | string | yes | The list |
| `version` / `as_of` / `release` | | no | See [Choosing a version](#choosing-a-version) |
| `include_retired` | boolean | no | Default `false` |
| `parent_code` | string | no | Only children of this value; `""` for the top level |
| `attribute_filters` | object | no | Values whose `attributes` **contain** these keys and values (JSON containment), e.g. `{ "crop": "MAIZE" }` |
| `search` | string | no | Case-insensitive match on code or label |

The same `ATTRIBUTE` data policies as `/attributes/get_attribute_values` apply.

```json
// request
{ "list_code": "SEED_VARIETY", "as_of": "2026-06-30T00:00:00Z", "attribute_filters": { "crop": "MAIZE" } }
// response
{
  "list_code": "SEED_VARIETY",
  "version": { "version_no": 6, "status": "PUBLISHED", "effective_from": "2026-03-01T00:00:00Z", "is_latest": false, "…": "…" },
  "values": [
    {
      "value_id": "MAIZE_BH661",
      "value_code": "MAIZE_BH661",
      "display": "BH-661",
      "display_i18n": null,
      "parent_code": null,
      "sort_order": 10,
      "attributes": { "crop": "MAIZE", "maturity_days": 160, "release_year": 2011 },
      "roles": null,
      "status": "ACTIVE"
    }
  ],
  "total": 14
}
```

`total` is the number of matching values; `response_body.pagination_response`
carries `number_of_items` and `number_of_pages`.

### `POST /catalogue/get_list_value`

One value by `value_code` at a version. Returns the value even if it is retired.

```json
// request
{ "list_code": "CROP_SEASON", "value_code": "SEASON_SUMMER", "version": "latest" }
// response
{ "list_code": "CROP_SEASON", "version": { "version_no": 3, "…": "…" },
  "value": { "value_id": "…", "value_code": "SEASON_SUMMER", "display": "Summer", "status": "RETIRED", "…": "…" } }
```

### `POST /catalogue/get_list_versions`

The version history of a list, newest first, as VersionInfo objects.

```json
// request
{ "list_code": "SEED_VARIETY" }
// response
{
  "list_code": "SEED_VARIETY",
  "versions": [
    { "version_no": 8, "status": "SUBMITTED", "base_version_no": 7, "change_note": "Add 2026 releases",
      "created_by": "5f0c…e1", "created_by_name": "Abebe Kebede", "submitted_by": "5f0c…e1",
      "submitted_by_name": "Abebe Kebede", "submitted_at": "2026-10-01T08:00:00Z", "is_latest": false, "…": "…" },
    { "version_no": 7, "status": "PUBLISHED", "base_version_no": 5, "effective_from": "2026-09-15T00:00:00Z",
      "published_at": "2026-09-14T11:02:37Z", "decided_by": "9a41…7c", "decided_by_name": "Tigist Alemu",
      "decision_note": "OK", "is_latest": true, "…": "…" },
    { "version_no": 6, "status": "DISCARDED", "base_version_no": 5, "decided_by": "5f0c…e1", "…": "…" }
  ]
}
```

### `POST /catalogue/get_list_diff`

What changed between two versions of a list: list metadata (code, label, labels,
hierarchy flag, attribute schema), and values **added**, **changed** (per field,
before and after), **retired** and **reactivated**. `from_version` defaults to the
base of `to_version`; `to_version` (a number, `"latest"` or `"draft"`) defaults to
`"latest"`. Use `to_version: "draft"` to review a draft.

```json
// request
{ "list_code": "CROP_SEASON", "from_version": 2, "to_version": 3 }
// response
{
  "list_code": "CROP_SEASON",
  "from_version": 2,
  "to_version": 3,
  "metadata_changes": { "display": { "before": "Season", "after": "Crop season" } },
  "added":   [ { "value_code": "SEASON_BELG", "display": "Belg", "status": "ACTIVE", "…": "…" } ],
  "changed": [ { "value_id": "…", "value_code": "SEASON_MEHER", "changes": { "display": { "before": "Meher season", "after": "Meher" } } } ],
  "retired": [ { "value_code": "SEASON_SUMMER", "status": "RETIRED", "…": "…" } ],
  "reactivated": []
}
```

## Geography

### `POST /catalogue/get_geo_versions`

All geography versions, newest first, with status, `effective_from`, `owner_org`,
`country`, active unit count and the boundary object key per level.

### `POST /catalogue/get_geo_levels`

The levels at a version, top-down.

```json
// request
{ "version": "latest" }
// response
{
  "version": { "version_no": 3, "status": "PUBLISHED", "effective_from": "2027-01-01T00:00:00Z", "is_latest": true,
               "country": "ETH", "boundary_objects": { "woreda": "geo/ETH/v3/woreda.geojson" }, "…": "…" },
  "levels": [
    { "level_id": "l1", "level_mnemonic": "region", "parent_level_id": "l0", "display": "Region", "display_i18n": { "am": "ክልል" } }
  ]
}
```

### `POST /catalogue/get_geo_units`

Units at a version. Paged; `GEO` data policies apply.

| Field | Type | Required | Description |
|---|---|---|---|
| `version` / `as_of` / `release` | | no | See [Choosing a version](#choosing-a-version) |
| `level` | string | no | Only units at this level (id or mnemonic) |
| `parent_unit_id` | string | no | Only children of this unit; `""` for the roots |
| `include_retired` | boolean | no | Default `false` |
| `search` | string | no | Case-insensitive match on unit id or name |

```json
// request
{ "as_of": "2026-06-30T00:00:00Z", "level": "woreda", "parent_unit_id": "ET0412" }
// response
{
  "version": { "version_no": 2, "…": "…" },
  "units": [
    { "unit_id": "ET041203", "level_id": "l3", "name": "Adaa", "name_i18n": { "am": "አዳ" },
      "parent_unit_id": "ET0412", "status": "ACTIVE", "valid_from": "1970-01-01T00:00:00Z", "valid_to": null }
  ],
  "total": 9
}
```

### `POST /catalogue/get_geo_unit`

One unit at a version, including if retired, with its `ancestors` (parent first,
up to the root).

```json
// request
{ "unit_id": "ET041203", "version": 3 }
// response
{ "version": { "version_no": 3, "…": "…" }, "unit": { "unit_id": "ET041203", "status": "RETIRED", "…": "…" },
  "ancestors": [ { "unit_id": "ET0412", "…": "…" }, { "unit_id": "ET04", "…": "…" } ] }
```

### `POST /catalogue/get_geo_changes`

Change events of the published versions after `from_version` (default 0) up to and
including `to_version` (default `"latest"`). `unit_id` keeps only events naming
that unit; `include_draft: true` adds the open draft's events.

```json
// request
{ "from_version": 2, "to_version": 3 }
// response
{
  "changes": [
    { "change_id": 57, "version_no": 3, "change_type": "SPLIT", "from_units": ["ET041203"], "to_units": ["ET041217", "ET041218"],
      "effective_date": "2027-01-01", "note": "Regional proclamation 123/2026", "is_auto": false,
      "created_by": "5f0c…e1", "created_by_name": "Abebe Kebede", "created_at": "2026-10-02T09:00:00Z" }
  ]
}
```

### `POST /catalogue/get_geo_crosswalk`

A unit's successors (or predecessors) between two versions, following the change
events across any number of versions. See
[The crosswalk](geography.md#the-crosswalk) for the response and how to use it.

| Field | Type | Required |
|---|---|---|
| `unit_id` | string | yes |
| `from_version` | integer | yes |
| `to_version` | integer, `"latest"` or `"draft"` | no (default `"latest"`; may be earlier than `from_version`) |

Response: `unit_id`, `from_version`, `to_version`, `direction` (`forward`,
`backward` or `none`), `unchanged`, `units`, `unmapped`, `path`.

### `POST /catalogue/get_geo_boundary`

A level's boundary GeoJSON at a version.

| Field | Type | Required | Description |
|---|---|---|---|
| `version` / `as_of` / `release` | | no | Default latest |
| `level` | string | yes | Level mnemonic (or id) |
| `stream` | boolean | no | `true` returns the GeoJSON itself (`application/geo+json`) instead of the envelope |

```json
// response (stream: false)
{
  "version_no": 3,
  "level": "woreda",
  "object_key": "geo/ETH/v3/woreda.geojson",
  "url": null,
  "presigned_url": "https://minio.example.org/openg2p-geo/geo/ETH/v3/woreda.geojson?X-Amz-…"
}
```

`url` is set only when a public base URL is configured
(`catalogue.boundaryStore.publicBaseUrl`); `presigned_url` (valid one hour) only
when the boundary store is configured. An unchanged level's key may name an
earlier version (`v1`).

## Releases

### `POST /catalogue/get_releases`

All releases, newest first: `release_code`, `title`, `note`, `status`,
`geo_version_no`, who created them, last set their members and published them, and
when (`created_by` / `created_by_name` / `created_at`, `members_set_by` /
`members_set_by_name` / `members_set_at`, `published_by` / `published_by_name` /
`published_at`; `*_by` are user ids, `*_by_name` display names), `member_count`.

### `POST /catalogue/get_release`

One release and its members.

```json
// request
{ "release_code": "2027.1" }
// response
{
  "release": { "release_code": "2027.1", "title": "Programme year 2027", "status": "PUBLISHED",
               "geo_version_no": 3, "published_by": "9a41…7c", "published_by_name": "Tigist Alemu",
               "published_at": "2026-12-01T09:00:00Z", "member_count": 2, "…": "…" },
  "members": [
    { "list_id": "CROP_COMMODITY", "list_code": "CROP_COMMODITY", "version_no": 4 },
    { "list_id": "SEED_VARIETY", "list_code": "SEED_VARIETY", "version_no": 7 }
  ]
}
```

## Change feed

### `POST /catalogue/get_changes`

Change-log events after a cursor, oldest first.

| Field | Type | Required | Description |
|---|---|---|---|
| `cursor` | integer | no | The last `event_id` already processed. Default `0` (from the beginning) |
| `limit` | integer | no | 1 to 1000, default 100 |
| `subject_type` | string | no | `list`, `geo` or `release` |
| `subject_id` | string | no | A list id, `geography`, or a release code |
| `event_types` | array | no | Only these event types |

```json
// request
{ "cursor": 1041, "limit": 100 }
// response
{
  "events": [
    { "event_id": 1042, "event_type": "list.version.published", "subject_type": "list", "subject_id": "SEED_VARIETY",
      "version_no": 8, "actor": "9a41…7c", "actor_name": "Tigist Alemu", "at": "2026-10-02T10:15:00Z",
      "details": { "list_code": "SEED_VARIETY", "effective_from": "2026-10-02T10:15:00+00:00", "base_version_no": 7, "current_version_no": 8 } },
    { "event_id": 1043, "event_type": "geo.version.published", "subject_type": "geo", "subject_id": "geography",
      "version_no": 3, "actor": "awe-approver", "actor_name": "awe-approver", "at": "2026-10-20T10:00:00Z",
      "details": { "effective_from": "2027-01-01T00:00:00+00:00", "base_version_no": 2, "current_version_no": 2, "boundary_objects": { "…": "…" } } }
  ],
  "next_cursor": 1043,
  "has_more": false
}
```

Pass `next_cursor` as the next `cursor`; call again while `has_more` is true.
`actor` is the stable user id (token `sub`) or a system name (`system`,
`migration`, `country-pack-loader`, `awe`); `actor_name` is a user's display name
(for an AWE decision, the approver as AWE reports them), `null` for a system
actor.

Event types:

| Subject | Event types |
|---|---|
| Lists | `list.created`, `list.updated` (description / owner), `list.deleted` (never-published list), `list.draft.created`, `list.draft.updated`, `list.draft.metadata_changed`, `list.draft.values_changed`, `list.draft.values_retired`, `list.draft.submitted`, `list.approval.requested`, `list.draft.approved`, `list.draft.rejected`, `list.draft.discarded`, `list.version.published`, `list.version.effective`, `list.version.migrated` |
| Geography | `geo.draft.created`, `geo.draft.updated`, `geo.draft.levels_changed`, `geo.draft.level_removed`, `geo.draft.units_changed`, `geo.draft.units_retired`, `geo.change.recorded`, `geo.change.deleted`, `geo.draft.boundary_uploaded`, `geo.draft.submitted`, `geo.approval.requested`, `geo.draft.approved`, `geo.draft.rejected`, `geo.draft.discarded`, `geo.version.published`, `geo.version.effective`, `geo.version.migrated` |
| Releases | `release.created`, `release.members_set`, `release.published`, `release.deleted` |

`*.version.effective` marks a future-effective version coming into effect.

**Audit Manager.** Every event is also delivered to the Audit Manager as a
CloudEvent whose `id` is derived from the change-log `event_id`. Delivery goes
through the change log as an outbox and is at least once; see
[Audit](change-control.md#audit).

**WebSub.** When a hub URL is configured (`catalogue.websubHubUrl`), MDS publishes
to these topics (prefix `websub_topic_prefix`, default `openg2p.master-data`),
registering each topic on first use:

| Topic | Event |
|---|---|
| `<prefix>.list.published` | `list.version.published` |
| `<prefix>.list.effective` | `list.version.effective`: a future-effective list version came into effect |
| `<prefix>.geo.published` | `geo.version.published` |
| `<prefix>.geo.effective` | `geo.version.effective`: a future-effective geography version came into effect |
| `<prefix>.release.published` | `release.published` |

The content is the JSON of the event's details plus `event_id`, `event_type`,
`subject_type`, `subject_id`, `version_no` and `list_id` (lists) or
`release_code` (releases). Delivery is at least once: de-duplicate on `event_id`.
A version published with an `effective_from` in the past or now gets only the
`published` notification (it is in effect at once); a future-effective one gets
`published` when approved and `effective` when its date passes.

### `POST /catalogue/get_catalogue_config`

How this catalogue is configured, for clients such as the admin UI.

```json
// response
{ "approval_mode": "permission", "boundary_store_enabled": true, "audit_enabled": true,
  "websub_enabled": false, "country": "ETH", "geo_current_version_no": 2 }
```

## Writes: lists

`?` marks an optional field. Every write that edits a draft creates one (from the
highest published version) if none is open.

| Endpoint | Permission | Request payload | Response |
|---|---|---|---|
| `create_list` | `referenceData:create` | `list_code`, `display`, `display_i18n`?, `description`?, `owner_org`?, `is_hierarchical`?, `attribute_schema`?, `list_id`? (default the code), `change_note`? | `list`, `draft` (version 1, nothing published) |
| `update_list` | `referenceData:edit` | `list_code`; `description`?, `owner_org`? (applied at once); `new_list_code`?, `display`?, `display_i18n`?, `is_hierarchical`?, `attribute_schema`? (into the draft) | `list`, `draft` |
| `create_list_draft` | `referenceData:edit` | `list_code`, `base_version`? (must be the highest published), `copy_from_version`?, `change_note`?, `effective_from`? | `list_code`, `draft` |
| `update_list_draft` | `referenceData:edit` | `list_code`, `change_note`?, `effective_from`? | `list_code`, `draft` |
| `upsert_draft_values` | `referenceData:edit` | `list_code`, `values`: a batch of (`value_code`, `display`, `display_i18n`?, `parent_code`?, `sort_order`?, `attributes`?, `roles`?, `value_id`?, `status`?) | `list_code`, `draft`, `values` |
| `retire_draft_values` | `referenceData:delete` | `list_code`, `value_codes`, `cascade`? | `list_code`, `draft`, `retired`, `removed` |
| `discard_draft` | `referenceData:edit` | `list_code` | `list_code`, `discarded_version_no` (kept as `DISCARDED`; the number is not reused) |
| `submit_draft` | `referenceData:edit` | `list_code`, `change_note`?, `effective_from`? | `list_code`, `draft` |
| `approve_draft` | `referenceData:publish` | `list_code`, `version_no`? (guard), `decision_note`?, `effective_from`? (`permission` mode) | `list_code`, `draft` (now published) |
| `reject_draft` | `referenceData:publish` | `list_code`, `version_no`?, `decision_note` (`permission` mode) | `list_code`, `draft` |

In `upsert_draft_values`, an item is matched on `value_id` when given (which lets a
value change its code), else on `value_code`; unmatched items are added (a new
value needs `display`). Only the fields present are changed.

**Example: add two seed varieties and submit**

```json
// upsert_draft_values
{
  "list_code": "SEED_VARIETY",
  "values": [
    { "value_code": "WHEAT_DANDAA", "display": "Dandaa", "attributes": { "crop": "WHEAT", "maturity_days": 120 } },
    { "value_code": "MAIZE_BH546",  "display": "BH-546", "attributes": { "crop": "MAIZE", "maturity_days": 145 } }
  ]
}
// response
{ "list_code": "SEED_VARIETY", "draft": { "version_no": 8, "status": "DRAFT", "base_version_no": 7, "…": "…" },
  "values": [ { "value_code": "WHEAT_DANDAA", "…": "…" }, { "value_code": "MAIZE_BH546", "…": "…" } ] }

// submit_draft
{ "list_code": "SEED_VARIETY", "change_note": "Add 2026 releases" }
```

A validation failure comes back as `G2P-CAT-400` naming the value and the place,
for example `value 'WHEAT_DANDAA': attributes invalid at maturity_days: …`, or for
a list reference
`value 'X': ['TEFF'] are not values of list CROP_COMMODITY (version 4, in effect now)`.
References resolve against the referenced list's version in effect (on the draft's
`effective_from` when that is in the future), never its draft; when the codes exist
only in the referenced list's draft the message adds
`… exist only in the unpublished draft (version 5) of CROP_COMMODITY — publish CROP_COMMODITY first`.
The batch is all or nothing.

## Writes: geography

| Endpoint | Permission | Request payload | Response |
|---|---|---|---|
| `create_geo_draft` | `geo:edit` | `base_version`?, `copy_from_version`?, `change_note`?, `effective_from`?, `owner_org`? | `draft` |
| `update_geo_draft` | `geo:edit` | `change_note`?, `effective_from`?, `owner_org`? | `draft` |
| `upsert_draft_levels` | `geo:edit` | `levels`: a batch of (`level_id`, `level_mnemonic`, `parent_level_id`?, `display`?, `display_i18n`?) | `draft`, `levels` |
| `upsert_draft_units` | `geo:edit` | `units`: a batch of (`unit_id`, `level_id`, `name`, `name_i18n`?, `parent_unit_id`?, `status`?) | `draft`, `units` |
| `retire_draft_units` | `geo:delete` | `unit_ids`, `cascade`? | `draft`, `retired`, `removed` |
| `record_geo_change` | `geo:edit` | `change_type`, `from_units`, `to_units`, `effective_date`?, `note`? | `draft`, `change` |
| `delete_geo_change` | `geo:edit` | `change_id` (an event of the open draft) | `change_id` |
| `upload_draft_boundary` | `geo:edit` | `level` (mnemonic or id), `geojson` (a `FeatureCollection`, in the JSON body) | `draft`, `level`, `object_key`, `features` |
| `submit_geo_draft` | `geo:edit` | `change_note`?, `effective_from`? | `draft` |
| `approve_geo_draft` | `geo:publish` | `version_no`?, `decision_note`?, `effective_from`? (`permission` mode) | `draft` |
| `reject_geo_draft` | `geo:publish` | `version_no`?, `decision_note` (`permission` mode) | `draft` |
| `discard_geo_draft` | `geo:edit` | (empty) | `discarded_version_no` |

A unit's parent must be an active unit of the parent level, and names are unique
among siblings. Upserting a retired unit brings it back.

**Example: record a split**

```json
// record_geo_change
{
  "change_type": "SPLIT",
  "from_units": ["ET041203"],
  "to_units": ["ET041217", "ET041218"],
  "effective_date": "2027-01-01",
  "note": "Regional proclamation 123/2026"
}
```

## Writes: releases

| Endpoint | Permission | Request payload |
|---|---|---|
| `create_release` | `referenceData:edit` | `release_code`, `title`?, `note`? |
| `set_release_members` | `referenceData:edit` | `release_code`, `members` (`list_code`, `version_no`), `geo_version_no`?, `replace`? (default `true`: replace all members; `false`: add or overwrite these) |
| `publish_release` | `referenceData:publish` | `release_code` |
| `delete_release` | `referenceData:delete` | `release_code` (draft releases only) |

Each returns `release` and `members`, except `delete_release` (`release_code`).
Only published versions can be members. Publishing checks that every member is
published and that `x-list-ref` references between member lists resolve within the
release's pins; the publisher must be neither the release's creator nor whoever
last set its members (`G2P-CAT-403`). A published release cannot be changed or
deleted.

## AWE callback

### `POST /catalogue/awe/callback`

In `awe` approval mode, AWE calls this endpoint with its decision on a submitted
draft. It is for AWE only: it is authenticated by an HMAC signature
(`X-Approval-Signature`, `X-Approval-Timestamp`, `X-Approval-Event-Id`), not by a
user token, and does not use the OpenG2P envelope. The body is AWE's webhook event;
the response is `{ "event_id", "applied", "message" }` (`message` is `published`,
`rejected`, `duplicate`, `already <status>` or `ok`). Errors: 401 bad signature,
422 event cannot be applied, 500 unexpected. See
[Change control](change-control.md#awe-through-the-approval-workflow-engine).

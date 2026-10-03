---
description: >-
  How registries, PBMS and other services should read reference data from MDS as
  Catalogue: latest, pinned or as-of reads, caching, the change feed, pinning in
  configuration, storing the version used, retired values and geography changes
---

# For Consumers

This page is for teams building on MDS: registries, PBMS, reporting, the composite,
and any other service that reads code lists or geography.

{% hint style="info" %}
**The registry platform reads MDS through the catalogue API.** A client in the
registry platform's core reads lists, values and geography through `/catalogue`,
caches them by version, follows the change feed (`get_changes`) to notice newly
published versions, and keeps serving the last good data if MDS is briefly
unreachable. It authenticates with the registry's own Keycloak client (client
credentials), so background workers read the same way as the APIs. Activities record
the catalogue versions they were checked against (`catalogue_versions`), and a
registry can pin a catalogue release (`catalogue_release`). The old direct database
reads remain as a rollback switch (`master_data_read_mode: db`; the chart renders
MDS database credentials only in that mode). The registry's staff UI still fills
dropdowns from the legacy `/attributes` and `/geo` APIs, but a register form's geo
**levels** (how many dropdowns, and their names) come from `/catalogue/get_geo_levels`
when the form loads, so the form follows the country's geography with no install
step. Install-time seed scripts (sample loaders, bulk generators, reporting views)
read MDS through the same API with a small client in the seed image (`mds_client.py`),
so they need read access to `/catalogue` (and `/samples` for demo data). **A registry
never reads or writes MDS's database**; its seeding writes only its own.
{% endhint %}

## Latest, pinned or as of

Every read says which version it wants (see
[Concepts](concepts.md#reading-latest-pinned-as-of-release)). Choose by what the data is
used for:

| Use | Read | Why |
|---|---|---|
| Data-entry dropdowns for new records | `latest` | New records should use the current list |
| Displaying an existing record | `latest` with `include_retired: true` | The record's code must still show a label, even if retired |
| A programme's eligibility or entitlement rules | **Pinned** version (or a release) | The rules were defined against that version and must not change silently |
| A report for a past period | `as_of` the period's date, or pinned to the version used | Reproducible: run it again next year and get the same answer |
| A survey, programme cycle or national report that needs everything consistent | A **catalogue release** | All lists and the geography at one agreed set of versions |

## Pin in configuration

A pin belongs in configuration, where it can be reviewed, not in code:

```yaml
catalogue:
  release: "2027.1"            # pin everything at once, or
  lists:
    SEED_VARIETY: 7            # pin individual lists
    CROP_COMMODITY: latest
  geography: 3
```

Moving a pin is a deliberate change: read the [diff](api-reference.md#lists)
between the pinned and the new version, check what it does to your rules, then
change the configuration.

## Store the version with the record

Where a record stores a code, also store **which version the code came from**, or
at least the geography version for unit codes. For example, an entitlement record
might hold `crop: MAIZE` with `catalogue_versions: { "CROP_COMMODITY": 4, "geo": 3 }`,
or a record might hold the release code it was created under.

That lets you later:

* resolve the code exactly as it was meant (`get_list_value` at that version);
* map a unit code to current geography with the
  [crosswalk](geography.md#the-crosswalk), which needs the from-version;
* explain an old decision.

If storing a version per record is not possible, the record's date and an `as_of`
read are the fallback.

## Cache by version

**A published version never changes.** So:

* a response for a **specific version number** can be cached **indefinitely**,
  keyed by list (or geography) and version number;
* a `latest` response should be cached only until the change feed says something
  new was published (or for a short time), then re-read. The `version` object in
  the response tells you which version you got, so the cache can be keyed by it;
* boundary files under a version key are immutable and can be cached the same way.

The legacy `/attributes` and `/geo` reads are cached inside MDS, per API worker. A
publish clears the cache at once on the worker that handled it. Every other worker
(other processes and other replicas) watches a counter, `legacy.generation` in
`g2p_catalogue_state`, which the database bumps whenever it refreshes the
current-state tables (a publish on any worker, a future-effective version coming
into effect, or a country-pack load); each worker checks it every
`catalogue_outbox_relay_seconds` (30 s by default) and clears its own cache when it
has moved. So a legacy read is stale for at most that interval after a publish,
plus, after a future `effective_from` passes, up to `effectiveRefreshSeconds`
(300 s by default) until MDS notices the date and refreshes the tables. Cache
entries also expire after `cache_expire_seconds` (300 s) in any case. The
`/catalogue` reads are not cached.

## Following changes

Do not poll lists to notice changes. Use the **change feed**:

1. Keep the last `event_id` you processed (start with `0`).
2. Call [`get_changes`](api-reference.md#change-feed) with it as the
   `cursor`, process the events in order, and store the new cursor.
3. On a `*.version.published` or `*.version.effective` event for a list or the
   geography you use: drop `latest` caches, and, if you pin, flag that a newer
   version exists for someone to review.

Events are ordered and the cursor is monotonic, so a consumer that was down simply
catches up from its last cursor.

If the deployment has a WebSub hub configured, a consumer can also subscribe to the
topics `openg2p.master-data.list.published`, `openg2p.master-data.list.effective`,
`openg2p.master-data.geo.published`, `openg2p.master-data.geo.effective` and
`openg2p.master-data.release.published` (the prefix is configurable) to be told
immediately, and use `get_changes` to fill any gaps. Notifications are delivered
**at least once**: the same event may arrive twice, so de-duplicate on its
`event_id`.

A version with a **future `effective_from`** is announced twice: when it is
**published** (`*.version.published`; check `effective_from` before treating it as
current, and use the time to prepare), and when it **takes effect**
(`*.version.effective`, on the change feed and on the `*.effective` WebSub topic).

## Retired values

* **Do not offer retired values for new data.** Reads leave them out by default.
* **Do not reject records that hold a retired value.** The value was valid when
  recorded. Read with `include_retired: true` (or `get_list_value`) to show it.
* A registry's coded-value check should validate **new** values against `latest` and
  accept existing values that are retired. (The registry platform validates new
  values against the version in effect and shows retired codes' labels at the
  version recorded on an activity. Accepting an unchanged retired value when an
  entity record is edited is still to do.)

## Geography changes

When a new geography version is published:

* **keep the recorded unit codes**; do not rewrite records automatically;
* **map through the crosswalk** for current reporting; splits need the record's
  location or a review;
* **recompute aggregates** keyed by unit against the new version;
* **re-pin deliberately** anything that targets units (programmes, campaigns);
* **rebuild maps** with the new version's boundaries, keeping the old ones for
  historical views.

The details, with examples, are in
[Geography and boundary changes](geography.md#when-a-new-geography-version-is-published).

## Checklist for a new consumer

* [ ] Read through the `/catalogue` APIs, not MDS's database.
* [ ] Decide per use whether you need latest, a pin, as-of, or a release; put pins in
      configuration.
* [ ] Store the version (or release) used alongside records that hold codes.
* [ ] Cache by version number; follow the change feed with a stored cursor.
* [ ] Show retired values on existing records; hide them in new-entry dropdowns.
* [ ] Have a plan for geography splits affecting your records.

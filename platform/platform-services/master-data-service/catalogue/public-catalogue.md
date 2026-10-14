---
description: >-
  The opt-in, anonymous, read-only public catalogue of MDS: visibility and
  licence, the /public API, CSV / JSON / GeoJSON downloads, DCAT and SKOS
  (JSON-LD), and the deployment settings
---

# Public Catalogue

MDS stays an **admin UI**: there is no public MDS website. What it can do is make
its catalogue **openly readable** by other websites and open-data portals (a
national data portal, CKAN, a ministry site) through an anonymous, read-only API
under **`/public`**, with downloads and standard metadata (DCAT, SKOS) they can
harvest.

Everything public is **opt-in, and off by default**, twice over:

1. The deployment switches the public catalogue on
   (`masterDataAPI.catalogue.public.enabled`, default `false`). While it is off,
   every `/public` path answers **404**.
2. An administrator marks each dataset, and the geography, **public**. Everything
   is **private** by default, including datasets loaded from a country pack.

Whatever the settings, the public API serves **published versions only**. Drafts,
submitted, rejected and discarded versions, private datasets, the change feed,
who made or approved a version, and the
[sample people](../api-reference.md#sample-people-testing-and-demos-only) are never
reachable through it. A private dataset, an unpublished version and a dataset that
does not exist all get the same 404, so the API does not reveal what exists
behind it.

Nothing changes for authenticated callers: the `/catalogue`, `/attributes`,
`/geo` and `/samples` APIs, and the registries that use them, ignore visibility and
keep requiring a token.

## Visibility and licence

| Field | Where | Meaning |
|---|---|---|
| `visibility` | Each dataset; the geography | `private` (default) or `public`. Administrative: applies at once, is not part of a version, and is recorded in the change log (`list.updated`, `geo.settings.updated`). |
| `licence_uri`, `licence_label` | Each dataset; the geography | Optional licence, e.g. `https://creativecommons.org/licenses/by/4.0/` and `CC BY 4.0`. Shown in the public API, DCAT and SKOS. |

* **Datasets:** set on `create_list` or `update_list` (permission
  `referenceData:create` / `referenceData:edit`), or in the dataset dialog of the
  [admin UI](ui.md#visibility-and-licence).
* **Geography:** `update_geo_settings` (permission `geo:edit`) or **Publication
  settings** on the Geography page. Read with `get_geo_settings`. These
  settings are kept outside the geography versions (a published version is
  immutable), so making the geography public makes all its **published** versions
  readable.
* **Country packs:** the loader fills the geography's licence from the pack
  manifest when no licence is set; one an administrator set is kept (see
  [Country packs](country-packs-and-migration.md#licence)). The loader never makes anything public.

A dataset marked public appears once it has a published version **in effect**;
a dataset whose only published version is future-effective is not listed yet, but
that version can be read by number.

{% hint style="info" %}
Data policies (the `DP_` roles that restrict which values a signed-in user sees)
do not apply to the public API: marking a dataset public is the decision to show
all of it.
{% endhint %}

## Public API

Anonymous `GET` requests; JSON responses (JSON-LD for DCAT and SKOS). Errors are
`{"detail": "…"}` with HTTP 400, 404 or 429. Every operation is listed, with its
parameters and responses, in the
[API reference](../api-reference.md#public-catalogue).

| Path | Returns |
|---|---|
| `/public/catalog` | The [DCAT catalogue](#dcat-catalogue) |
| `/public/datasets`, `/public/datasets/{code}` | Public datasets with a published version in effect: title, description, theme, publisher, licence, version, dates, links; one dataset adds its published versions |
| `/public/datasets/{code}/entries`, `…/entries/{entry_code}` | Entries of the selected version (paged, `page_size` up to 5000); one entry, which is also its SKOS concept's address |
| `/public/datasets/{code}/download.csv`, `…/download.json`, `…/skos` | The selected version as CSV, JSON or a [SKOS concept scheme](#skos-concept-schemes) |
| `/public/geography`, `/public/geography/levels`, `/public/geography/units` | The geography (404 unless public), its levels, its units (filtered by `level` and `parent`, paged) |
| `/public/geography/levels/{level}/units.csv`, `…/boundaries.geojson` | Units of a level as CSV; the level's boundaries, streamed from the boundary store |
| `/public/releases`, `/public/releases/{code}` | Published releases with only their public members; a release with nothing public is not listed |

Version selection, where a version applies: `version` (a published version number,
or `latest`, the default: the published version in effect now) or `as_of`
(date-time: the published version in effect then). `version=draft` is refused
(400). Retired entries and units are left out unless `include_retired=true`.

### Downloads

| Download | Columns / content |
|---|---|
| Dataset CSV | `code`, `label`, `label_<lang>` per language present, `parent_code`, `sort_order`, `status`, `attributes` (JSON), `roles` (JSON) |
| Dataset JSON | As `entries`, for the whole version |
| Units CSV | `unit_id`, `name`, `name_<lang>` per language present, `level`, `parent_unit_id`, `status`, `valid_from`, `valid_to` |
| Boundaries GeoJSON | The version's boundary file for the level, as loaded (a `FeatureCollection`) |

Downloads carry `Content-Disposition` file names such as `CROP_COMMODITY-v4.csv`
and `geography-v2-woreda.geojson`. They are generated (or streamed) on request; no
bucket is made public.

### Caching, CORS and rate limit

* Every response has an **`ETag`** (`If-None-Match` gives **304**),
  **`Last-Modified`** (the version's publication time; `If-Modified-Since` is
  honoured), and `Cache-Control: public, max-age=<cacheSeconds>`. Published
  versions are immutable, so a pinned download never changes.
* `Access-Control-Allow-Origin: *` (no credentials), so a website can read the API
  from the browser.
* **Rate limit:** an in-process token bucket per client IP and API worker
  (`rateLimitPerMinute`, default 60, also the burst). Over the limit the API
  answers **429** with `Retry-After`. The client IP is read from
  `X-Forwarded-For`, `trustedProxyHops` entries from the right (1 behind the Istio
  ingress gateway), so a client cannot dodge the limit by sending its own header.
* **Audit:** like every MDS API call, anonymous failures (404, 429) are sent to the
  Audit Manager; anonymous successes (200, 304) are not.

### DCAT catalogue

`GET /public/catalog` describes the catalogue in DCAT (JSON-LD), so CKAN's DCAT
harvester and other open-data portals can harvest it. It lists one dataset per
public dataset with a published version in effect, plus the geography when it is
public, each with its licence, theme, version and one distribution per download
format (pinned to that version). The vocabulary and how fully it is followed are
on [Standards](../standards.md#catalogue-metadata-public-catalogue).

### SKOS concept schemes

`GET /public/datasets/{code}/skos` gives the selected version as a SKOS concept
scheme (JSON-LD): one concept per active entry, with its code, labels per
language and parent. A concept's address
(`/public/datasets/{code}/entries/{entry_code}`) resolves and does not carry the
version, so a code keeps the same address across versions. See
[Standards](../standards.md#datasets-and-entries).

## Base URL

Links in DCAT, SKOS and the JSON responses are absolute. Their base is
`catalogue.public.baseUrl` when set (e.g. `https://catalogue.example.gov`); when
empty it is taken from the request (`X-Forwarded-Proto` and `X-Forwarded-Host`,
which the public host's VirtualService sets).

## Deployment

Chart values under `masterDataAPI.catalogue.public` (Rancher group **Public
catalogue**, shown once the catalogue is enabled):

| Value | Default | Environment variable | Meaning |
|---|---|---|---|
| `enabled` | `false` | `MASTER_DATA_API_PUBLIC_CATALOGUE_ENABLED` | Serve `/public`; off: 404 everywhere under it |
| `baseUrl` | `""` | `MASTER_DATA_API_PUBLIC_BASE_URL` | Base of absolute links (see above) |
| `rateLimitPerMinute` | `60` | `MASTER_DATA_API_PUBLIC_CATALOGUE_RATE_LIMIT_PER_MINUTE` | Per client IP and worker; `0` disables |
| `trustedProxyHops` | `1` | `MASTER_DATA_API_PUBLIC_CATALOGUE_TRUSTED_PROXY_HOPS` | Proxies that append to `X-Forwarded-For`; `0` uses the socket peer |
| `cacheSeconds` | `300` | `MASTER_DATA_API_PUBLIC_CATALOGUE_CACHE_SECONDS` | `Cache-Control` max-age |
| `title` | `Master data catalogue` | `MASTER_DATA_API_PUBLIC_CATALOGUE_TITLE` | DCAT catalogue title |
| `publisher` | `""` | `MASTER_DATA_API_PUBLIC_CATALOGUE_PUBLISHER` | DCAT catalogue publisher; empty uses `catalogue.defaultOwnerOrg` |
| `istio.enabled` | `false` | — | A separate host for the public catalogue |
| `istio.host` | `catalogue.<namespace>.openg2p.org` | — | Its hostname |
| `istio.gateway` | `internal` | — | Istio gateway of that host |

The separate host's VirtualService routes **only `/public/`** (GET, HEAD, OPTIONS)
to the API; nothing else of the API or the admin UI is reachable on it. On the
main MDS host `/public` is also served (to whoever can reach that host).

{% hint style="warning" %}
The default gateway is the existing **internal** gateway, so the catalogue is
reachable on the internal network only. Exposing it to the internet needs a public
(internet-facing) Istio gateway named in `istio.gateway`, with DNS and a TLS
certificate for the host, and a decision that the datasets marked public may be
published. Consider a CDN or the gateway's own rate limiting in front of it: the
API's limit is per worker and per pod.
{% endhint %}

The API's own setting `public_catalogue_default_language` (default `en`) is the
language tag of the plain `display` labels in SKOS and DCAT.

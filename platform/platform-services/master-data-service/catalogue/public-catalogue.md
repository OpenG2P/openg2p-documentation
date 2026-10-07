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
   is **private** by default, including lists loaded from a country pack.

Whatever the settings, the public API serves **published versions only**. Drafts,
submitted, rejected and discarded versions, private datasets, the change feed,
who made or approved a version, and the
[sample people](api-reference.md#sample-people-testing-and-demos-only) are never
reachable through it. A private dataset, an unpublished version and a dataset that
does not exist all get the same 404, so the API does not reveal what exists
behind it.

Nothing changes for authenticated callers: the `/catalogue`, `/attributes`,
`/geo` and `/samples` APIs, and the registries that use them, ignore visibility and
keep requiring a token.

## Visibility and licence

| Field | Where | Meaning |
|---|---|---|
| `visibility` | Each list; the geography | `private` (default) or `public`. Administrative: applies at once, is not part of a version, and is recorded in the change log (`list.updated`, `geo.settings.updated`). |
| `licence_uri`, `licence_label` | Each list; the geography | Optional licence, e.g. `https://creativecommons.org/licenses/by/4.0/` and `CC BY 4.0`. Shown in the public API and as `dct:license` in DCAT and SKOS. |

* **Lists:** set on `create_list` or `update_list` (permission
  `referenceData:create` / `referenceData:edit`), or in the dataset dialog of the
  [admin UI](ui.md#visibility-and-licence).
* **Geography:** `update_geo_settings` (permission `geo:edit`) or **Publication
  settings** on the Geo Locations page. Read with `get_geo_settings`. These
  settings are kept outside the geography versions (a published version is
  immutable), so making the geography public makes all its **published** versions
  readable.
* **Country packs:** the loader fills the geography's licence from the pack
  manifest (`license`, and `license_uri` when given; the URI of a well-known
  licence such as CC BY-IGO or CC0-1.0 is derived from its label) when no licence
  is set; one an administrator set is kept. The loader never makes anything public.

A dataset marked public appears once it has a published version **in effect**;
a list whose only published version is future-effective is not listed yet, but
that version can be read by number.

{% hint style="info" %}
Data policies (the `DP_` roles that restrict which values a signed-in user sees)
do not apply to the public API: marking a dataset public is the decision to show
all of it.
{% endhint %}

## Public API

Anonymous `GET` requests; JSON responses (JSON-LD for DCAT and SKOS). Errors are
`{"detail": "…"}` with HTTP 400, 404 or 429.

Version selection, where a version applies: `version` (a published version number,
or `latest`, the default: the published version in effect now) or `as_of`
(ISO date-time: the published version in effect then). `version=draft` is refused
(400).

| Endpoint | Returns |
|---|---|
| `GET /public/catalog` | The [DCAT catalogue](#dcat-catalogue) (JSON-LD) |
| `GET /public/datasets` | Public datasets with a published version in effect: `code`, `title`, `title_i18n`, `description`, `theme` (the list's domain), `publisher` (`owner_org`), `licence`, `version`, `effective_from`, `issued` (first publication), `modified` (current version's publication), `links` |
| `GET /public/datasets/{code}` | One dataset, plus its published `versions` (`version`, `effective_from`, `published_at`, `change_note`). A `Link` header points at the SKOS form. |
| `GET /public/datasets/{code}/entries` | Entries of the selected version: `code`, `label`, `labels` (per language), `parent_code`, `sort_order`, `attributes`, `roles`, `status`. Active entries only unless `include_retired=true`; `parent_code` filters (`""` for the top level); paged with `page` and `page_size` (default 1000, at most 5000), with `total`. |
| `GET /public/datasets/{code}/entries/{entry_code}` | One entry (also the IRI of its SKOS concept) |
| `GET /public/datasets/{code}/download.csv` | The selected version as CSV (below) |
| `GET /public/datasets/{code}/download.json` | The selected version as JSON: `dataset`, `version`, `effective_from`, `published_at`, `title`, `entries` |
| `GET /public/datasets/{code}/skos` | The selected version as a [SKOS concept scheme](#skos-concept-schemes) (JSON-LD) |
| `GET /public/geography` | 404 unless the geography is public. `country`, `publisher`, `licence`, `version`, `effective_from`, `issued`, `modified`, `levels` (with unit counts and download links), published `versions` |
| `GET /public/geography/levels` | Levels of the selected version |
| `GET /public/geography/units` | Units, filtered by `level` (mnemonic or id) and `parent` (`""` for the root); paged; `include_retired` |
| `GET /public/geography/levels/{level}/units.csv` | Units of a level as CSV |
| `GET /public/geography/levels/{level}/boundaries.geojson` | Boundaries of a level as GeoJSON, streamed from the boundary object store (404 when the version has none) |
| `GET /public/releases` | Published releases with only their **public** members, and the geography version only when the geography is public; a release with nothing public is not listed |
| `GET /public/releases/{code}` | One published release (public members only) |

### Downloads

| Download | Columns / content |
|---|---|
| Dataset CSV | `code`, `label`, `label_<lang>` per language present, `parent_code`, `sort_order`, `status`, `attributes` (JSON), `roles` (JSON) |
| Dataset JSON | As `entries`, for the whole version |
| Units CSV | `unit_id`, `name`, `name_<lang>` per language present, `level`, `parent_unit_id`, `status`, `valid_from`, `valid_to` |
| Boundaries GeoJSON | The version's boundary object for the level, as loaded (RFC 7946 `FeatureCollection`) |

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

`GET /public/catalog` returns a `dcat:Catalog` as JSON-LD, DCAT-AP style, that
CKAN's DCAT harvester (ckanext-dcat) and other DCAT harvesters can read:

* the catalogue: `dct:title`, `dct:description`, `dct:publisher` (`foaf:Agent`),
  `dct:modified`, `dcat:themeTaxonomy` (a SKOS scheme of the themes in use);
* one **`dcat:Dataset`** per public dataset with a published version in effect,
  plus one for the geography when it is public: `dct:identifier`, `dct:title`
  (language-tagged), `dct:description`, `dct:publisher`, `dct:license`,
  `dct:issued`, `dct:modified`, `dcat:theme`, `dcat:keyword`, `dcat:version` and
  `owl:versionInfo` (the version in effect), `dcat:landingPage`;
* one **`dcat:Distribution`** per format, pinned to that version: `dcat:downloadURL`,
  `dcat:accessURL`, `dcat:mediaType` (IANA media type IRI), `dct:format` (EU file
  type IRI) and `dct:license`. Lists have CSV, JSON and SKOS (JSON-LD); the
  geography has a units CSV per level and, where the version has boundaries, a
  GeoJSON per level.

```json
{
  "@context": { "dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/", "…": "…" },
  "@id": "https://catalogue.example.gov/public/catalog",
  "@type": "dcat:Catalog",
  "dct:title": "Master data catalogue",
  "dcat:dataset": [
    {
      "@id": "https://catalogue.example.gov/public/datasets/CROP_COMMODITY",
      "@type": "dcat:Dataset",
      "dct:identifier": "CROP_COMMODITY",
      "dct:title": [ { "@value": "Crop", "@language": "en" }, { "@value": "ሰብል", "@language": "am" } ],
      "dct:license": { "@id": "https://creativecommons.org/licenses/by/4.0/", "@type": "dct:LicenseDocument", "rdfs:label": "CC BY 4.0" },
      "dcat:theme": { "@id": "https://catalogue.example.gov/public/catalog#themes-agriculture" },
      "dcat:version": "4",
      "dcat:distribution": [
        { "@type": "dcat:Distribution", "dct:title": "CROP_COMMODITY (CSV)",
          "dcat:downloadURL": { "@id": "https://catalogue.example.gov/public/datasets/CROP_COMMODITY/download.csv?version=4" },
          "dcat:mediaType": { "@id": "https://www.iana.org/assignments/media-types/text/csv" },
          "dct:format": { "@id": "http://publications.europa.eu/resource/authority/file-type/CSV" } }
      ]
    }
  ]
}
```

### SKOS concept schemes

`GET /public/datasets/{code}/skos` returns the selected version as JSON-LD
(`@graph`):

* a **`skos:ConceptScheme`** (`@id` `…/datasets/{code}/skos`): `skos:prefLabel`
  per language, `dct:title`, `dct:description`, `skos:notation` (the dataset code),
  `owl:versionInfo` and `dcat:version`, `dct:issued`, `dct:license`,
  `dct:publisher`, `skos:hasTopConcept`;
* one **`skos:Concept`** per active entry (`@id` `…/datasets/{code}/entries/{entry_code}`,
  which resolves): `skos:notation` (the code), `skos:prefLabel` with a language tag
  per `display_i18n` locale (plus `display` in the default language,
  `public_catalogue_default_language`, when `display_i18n` lacks it),
  `skos:inScheme`, and `skos:broader` (the parent) or `skos:topConceptOf`.

Concept IRIs do not carry the version, so a code keeps the same IRI across
versions.

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

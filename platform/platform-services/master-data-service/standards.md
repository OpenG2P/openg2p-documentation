---
description: >-
  Every standard the Master Data Service (Catalogue) uses or follows, where it
  is used and how fully: catalogue metadata, datasets, geography, licences,
  formats, events, HTTP and security.
---

# Standards

MDS keeps its own data model and maps it onto open standards where it publishes
or exchanges data. This page is the single list of those standards. Other MDS
pages link here instead of describing them.

**Status:** **Used**: implemented and in use. **Partly**: used, with the limits
given in the notes. **To explore**: not used yet.

## At a glance: what a public consumer uses

Anyone in the country can find and read the public catalogues with ordinary open-data tools; the endpoints are described in the DCAT catalogue, so harvesters find them without reading MDS documentation. Only the staff API (editing, approvals, behind a login) is MDS's own.

| Need | Standard | Where |
| --- | --- | --- |
| Find what data exists | W3C DCAT 3, JSON-LD (DCAT-AP style) | `GET /public/catalog`: harvestable by CKAN and national open-data portals |
| Read a code list | W3C SKOS concept scheme, JSON-LD | `GET /public/datasets/{code}/skos` |
| Download | CSV, JSON; GeoJSON (RFC 7946) for boundaries | Per dataset version and per geography level ([downloads](public-catalogue.md#what-it-offers)) |
| Notice changes | DCAT `modified` dates; HTTP caching (`ETag`, `Last-Modified`) | Every public response. The change feed and its WebSub notifications are for authenticated consumers only ([consumers](consumers.md)) |
| Licence | Creative Commons / Open Data Commons URIs | `licence_uri` on each dataset and the geography |

The sections below list every standard in detail.

## Catalogue metadata (public catalogue)

These apply to the opt-in [public catalogue](public-catalogue.md)
(`/public/...`), which is off by default.

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [W3C DCAT](https://www.w3.org/TR/vocab-dcat-3/) (Data Catalog Vocabulary), version 3 | `GET /public/catalog` | Used | One `dcat:Catalog`; a `dcat:Dataset` per public dataset, and one for the geography when public; a `dcat:Distribution` per format with `dcat:downloadURL`, `dcat:accessURL`, `dcat:mediaType`. Also `dcat:theme`, `dcat:themeTaxonomy`, `dcat:keyword`, `dcat:version` (DCAT 3), `dcat:landingPage` |
| [DCAT-AP](https://semiceu.github.io/DCAT-AP/) (EU application profile) | `GET /public/catalog` | Partly | Follows the DCAT-AP style (licence, publisher, EU file types, IANA media types) so CKAN's DCAT harvester (ckanext-dcat) can read it. Not validated against the DCAT-AP SHACL shapes |
| [DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) (`dct:`) | DCAT and SKOS documents | Used | `dct:title` (language-tagged), `dct:description`, `dct:identifier`, `dct:publisher`, `dct:license` (`dct:LicenseDocument`), `dct:format`, `dct:issued`, `dct:modified` |
| [FOAF](http://xmlns.com/foaf/spec/) | DCAT documents | Used | Publisher as `foaf:Agent` with `foaf:name`; the catalogue's `foaf:homepage` |
| [OWL](https://www.w3.org/TR/owl2-overview/), [RDF Schema](https://www.w3.org/TR/rdf-schema/) | DCAT and SKOS documents | Used | Only `owl:versionInfo` (the version) and `rdfs:label` (licence label) |
| [XML Schema datatypes](https://www.w3.org/TR/xmlschema11-2/) | DCAT and SKOS documents | Used | `xsd:dateTime` on issued and modified dates |
| [EU file-type authority list](https://op.europa.eu/en/web/eu-vocabularies/concept-scheme/-/resource?uri=http://publications.europa.eu/resource/authority/file-type) | `dct:format` of each distribution | Used | CSV, JSON, JSON-LD, GeoJSON |
| [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/) | DCAT and SKOS responses | Used | `application/ld+json`, with an inline `@context` |

## Datasets and entries

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [W3C SKOS](https://www.w3.org/TR/skos-reference/) | `GET /public/datasets/{code}/skos` | Used | A dataset version is a `skos:ConceptScheme` (`skos:notation`, `skos:prefLabel`, `skos:hasTopConcept`); each active entry a `skos:Concept` with `skos:notation` (the code), `skos:prefLabel` per language, `skos:broader` (parent) or `skos:topConceptOf`, `skos:inScheme`. Concept IRIs (`/public/datasets/{code}/entries/{entry_code}`) resolve and do not carry the version. Mappings to other vocabularies (`skos:exactMatch`) are not published |
| [JSON Schema](https://json-schema.org/draft/2020-12) 2020-12 | A dataset's `attribute_schema` (typed entry fields) | Used | Entries are validated on write, submit and approval. `x-list-ref` (a field, or each item of an array field, that must hold an entry of another dataset) is an OpenG2P extension |
| [ISO 639](https://www.iso.org/iso-639-language-code) / [BCP 47](https://www.rfc-editor.org/info/bcp47) language tags | `display_i18n`, `name_i18n` keys (e.g. `en`, `am`, `om`); SKOS and DCAT language tags | Partly | Used as given by the country pack; MDS does not validate the tags. The plain label's language is set per deployment (see [Deployment](deployment.md#public-catalogue-host)) |
| [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) / [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) | All dates and times: `effective_from`, `as_of`, `published_at`, change-event dates | Used | |

## Geography

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [OCHA COD-AB](https://data.humdata.org/dashboards/cod) and [P-codes](https://humanitarian.atlassian.net/wiki/spaces/imtoolbox/pages/222265609/P-codes) | Unit ids (`unit_id`, `level_value_id`), the `ETH` country pack | Used | The pack's units and boundaries come from COD-AB, so codes match datasets that use the same P-codes. MDS does not check the P-code format; after a reparent without a recode a code's prefix no longer names its parent (see [Geography](geography.md)) |
| [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) alpha-3 | Country pack name and geography `country` (e.g. `ETH`); boundary keys `geo/<country>/v<n>/…` | Partly | A convention, not validated. The demo country `XKM` uses the ISO 3166 user-assigned range so it cannot collide with a real country |
| [GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946) (RFC 7946) | Boundary files per level and version: upload (`upload_draft_boundary`), `get_geo_boundary`, `/public/.../boundaries.geojson` | Used | One `FeatureCollection` per level; features matched to units by `properties.pcode`. MDS checks the type, not the geometry |
| [OGC API – Features](https://ogcapi.ogc.org/features/) | — | To explore | Per-unit features, paging, bounding boxes. Today boundaries are one GeoJSON file per level |

## Licences

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| Licence URIs ([Creative Commons](https://creativecommons.org/licenses/), [Open Data Commons](https://opendatacommons.org/licenses/)) | `licence_uri` and `licence_label` on each dataset and the geography; `dct:license` in DCAT and SKOS | Used | Free text; the admin UI suggests CC BY 4.0, CC BY-SA 4.0, CC0 1.0, CC BY-IGO, ODbL 1.0. A pack's geography licence comes from its source (see [Country Packs](country-packs.md#sources-and-licence)) |
| [SPDX licence ids](https://spdx.org/licenses/) | Country-pack `manifest.json` `license` | Partly | The loader accepts an SPDX id (e.g. `CC0-1.0`, `CC-BY-4.0`, `ODbL-1.0`) or a label and derives the licence URI. MDS stores URI and label, not an SPDX id |

## Mappings to international schemes

Codes stay the country's own; a mapping to an international scheme is a typed
field of the entry (see
[Design Decisions](design-decisions.md#mapping-to-international-standards)).

| | Status |
|---|---|
| Typed fields per entry, checked by JSON Schema, versioned with the dataset | **Used** |
| Finding entries by a field value (`attribute_filters`) | **Used** |
| COD-AB P-codes as geography unit ids | **Used** (from the shipped country pack) |
| Field names for international mappings (`isced_level`, `isco_code`, `icd10_code`, `iso4217_code`, `fao_wca_icc`, `faostat_item_code`, `agrovoc_uri`, `dadis_breed_id`, `ucum_code`, `hs_code`) | **Convention**: a suggestion, not enforced |
| International mappings in the shipped Ethiopia pack | **Not provided**: the pack carries none today |
| International schemes loaded as datasets of their own and referenced from a field | **To explore**: possible with what is built; no pack does it |
| Publishing mappings as `skos:exactMatch` in the [public catalogue's](public-catalogue.md) SKOS | **To explore** (see [Datasets and entries](#datasets-and-entries)) |

## Formats

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [JSON](https://datatracker.ietf.org/doc/html/rfc8259) (RFC 8259) | Every API; dataset downloads | Used | |
| [CSV](https://datatracker.ietf.org/doc/html/rfc4180) (RFC 4180) | `/public/.../download.csv`, `/public/.../units.csv` | Used | UTF-8, one row per entry or unit; labels per language as `label_<lang>` / `name_<lang>` columns |
| [IANA media types](https://www.iana.org/assignments/media-types/media-types.xhtml) | Every public response and DCAT `dcat:mediaType` | Used | `application/json`, `text/csv`, `application/ld+json`, `application/geo+json` |

## Events and notifications

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [CloudEvents](https://cloudevents.io/) 1.0 | Audit Manager: every catalogue change-log event and every API call | Used | Change-log events: type `org.openg2p.master_data.<event_type>`, `id` derived from the change-log `event_id`, at least once. API calls: one event per call, from the audit middleware (source `/openg2p/master-data-api`). See [Audit](change-control.md#audit) |
| [W3C WebSub](https://www.w3.org/TR/websub/) | Notifications when a version is published or takes effect | Partly | Optional (needs a hub). MDS registers topics and publishes with `hub.mode=register` / `publish`, as the OpenG2P hub expects; those publisher calls are hub-specific, not part of the WebSub recommendation. Subscribers use standard WebSub |

## HTTP API and security

| Standard | Where in MDS | Status | Notes |
|---|---|---|---|
| [OpenAPI](https://spec.openapis.org/oas/v3.1.0) 3.1 | `/openapi.json`, `/docs`; the published spec `docs/openapi/openapi-master-data.json` | Used | Generated from the code. See [API Reference](api-reference.md) |
| OpenG2P request/response envelope | Every `POST` endpoint | Used | An OpenG2P convention (openg2p-fastapi-common), not an external standard: `request_header` + `request_body.request_payload`; business errors as HTTP 200 with `response_status: ERROR` |
| [OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749) / [OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html), bearer [JWT](https://datatracker.ietf.org/doc/html/rfc7519) | Every endpoint except `/public`, `/ping` and the AWE callback | Used | Keycloak through OpenG2P IAM: staff log in to the admin UI; services use client credentials. Users are identified by the token's `sub` |
| [HMAC](https://datatracker.ietf.org/doc/html/rfc2104)-SHA256 | AWE decision callback | Used | `X-Approval-Signature: sha256=…` over timestamp and body |
| HTTP conditional requests ([RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#name-conditional-requests)) and caching ([RFC 9111](https://www.rfc-editor.org/rfc/rfc9111)) | `/public/...` | Used | `ETag` / `If-None-Match`, `Last-Modified` / `If-Modified-Since` (304), `Cache-Control: public, max-age` |
| [CORS](https://fetch.spec.whatwg.org/#http-cors-protocol) | `/public/...` | Used | `Access-Control-Allow-Origin: *`, no credentials |
| HTTP 429 and `Retry-After` ([RFC 6585](https://www.rfc-editor.org/rfc/rfc6585), RFC 9110) | `/public/...` rate limit | Used | Per client IP, read from `X-Forwarded-For` (a de facto header) |
| [OData](https://www.odata.org/documentation/) | — | To explore | For BI tools querying datasets live |

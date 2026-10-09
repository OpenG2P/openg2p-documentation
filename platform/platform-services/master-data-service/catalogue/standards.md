---
description: >-
  The open standards the Master Data catalogue uses, and where: catalogue
  metadata, code lists, geography, licences, downloads, events and the HTTP API.
---

# Standards

The catalogue keeps its own data model, and maps it onto open standards wherever it publishes or exchanges data. A consumer that knows these standards can read the catalogue without OpenG2P-specific code.

## Catalogue and datasets

| Standard | Used for | Where |
| --- | --- | --- |
| [**DCAT**](https://www.w3.org/TR/vocab-dcat-3/) (W3C Data Catalog Vocabulary) | The catalogue itself: `dcat:Catalog`, each public dataset as a `dcat:Dataset` with its downloads as `dcat:Distribution` (`dcat:downloadURL`, `dcat:mediaType`), keywords, themes (`dcat:theme`, `dcat:themeTaxonomy`), version (`dcat:version`) and landing page | [Public catalogue](public-catalogue.md) `GET /public/catalog` |
| [**DCMI Metadata Terms**](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) (Dublin Core, `dct:`) | Title, description, identifier, publisher, licence (`dct:license`, `dct:LicenseDocument`), format, issued and modified dates | Same documents |
| [**FOAF**](http://xmlns.com/foaf/spec/) | The publisher (`foaf:Agent`, `foaf:name`, `foaf:homepage`) | Same documents |
| [**SKOS**](https://www.w3.org/TR/skos-reference/) (W3C Simple Knowledge Organization System) | Each dataset's values as a concept scheme: `skos:ConceptScheme`, `skos:Concept` with `skos:notation` (the code), `skos:prefLabel` (labels), `skos:broader` for hierarchies, `skos:inScheme`, `skos:hasTopConcept` | Public catalogue, per dataset |
| [**JSON-LD**](https://www.w3.org/TR/json-ld11/) | The serialisation of the DCAT and SKOS documents (`application/ld+json`, with an `@context`) | Public catalogue |
| [**XML Schema datatypes**](https://www.w3.org/TR/xmlschema11-2/) | Typed dates in the linked data (`xsd:dateTime`) | DCAT documents |

## Geography

| Standard | Used for | Where |
| --- | --- | --- |
| [**OCHA COD-AB**](https://data.humdata.org/dashboards/cod) and [**P-codes**](https://humanitarian.atlassian.net/wiki/spaces/imtoolbox/pages/222265609/P-codes) | The country pack's administrative boundaries and unit codes (e.g. Ethiopia's region → zone → woreda), so units match the humanitarian and government datasets that use the same P-codes | [Geography](geography.md), [country packs](country-packs-and-migration.md) |
| [**GeoJSON**](https://datatracker.ietf.org/doc/html/rfc7946) (RFC 7946) | Boundary downloads per level (`application/geo+json`) | Public catalogue, admin UI |

## Licences and attribution

| Standard | Used for | Where |
| --- | --- | --- |
| **Licence URIs** (e.g. [Creative Commons](https://creativecommons.org/licenses/)) | Each public dataset and geography version carries a licence as a URI plus label (`dct:license`), e.g. [CC BY-IGO](https://creativecommons.org/licenses/by/3.0/igo/) for the OCHA boundaries, with the source's attribution | [Public catalogue](public-catalogue.md) |

## Values and labels

| Standard | Used for | Where |
| --- | --- | --- |
| [**BCP 47**](https://www.rfc-editor.org/info/bcp47) language tags (ISO 639 codes) | Translated labels per value (`display_i18n`, e.g. `en`, `am`); the plain label's language is `public_catalogue_default_language` | Datasets, SKOS `prefLabel` |
| [**ISO 8601**](https://www.iso.org/iso-8601-date-and-time-format.html) | Dates and times (effective-from dates, publication times) | All APIs |

## Downloads

| Standard | Used for | Where |
| --- | --- | --- |
| [**CSV**](https://datatracker.ietf.org/doc/html/rfc4180) (RFC 4180) and [**JSON**](https://datatracker.ietf.org/doc/html/rfc8259) (RFC 8259) | Dataset downloads | Public catalogue, admin UI |
| [**IANA media types**](https://www.iana.org/assignments/media-types/media-types.xhtml) | `text/csv`, `application/json`, `application/ld+json`, `application/geo+json` on every download and document | Public catalogue |

## Events and change notifications

| Standard | Used for | Where |
| --- | --- | --- |
| [**CloudEvents**](https://cloudevents.io/) 1.0 | Every change and API call sent to the Audit Manager | Change log, audit |
| [**WebSub**](https://www.w3.org/TR/websub/) (W3C) | Notifications when a version is published or takes effect (topics under `openg2p.master-data`), optional | [For consumers](consumers.md) |

## HTTP API

| Standard | Used for | Where |
| --- | --- | --- |
| [**OpenAPI**](https://spec.openapis.org/oas/latest.html) | The API description (`/docs`, `/openapi.json`) | [API reference](api-reference.md) |
| **HTTP conditional requests** ([RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#name-conditional-requests): `ETag`, `If-None-Match`, `Last-Modified`) and caching ([RFC 9111](https://www.rfc-editor.org/rfc/rfc9111): `Cache-Control`) | Public reads answer `304 Not Modified` when unchanged and may be cached | Public catalogue |
| [**CORS**](https://fetch.spec.whatwg.org/#http-cors-protocol) | Public reads can be called from any web page (`Access-Control-Allow-Origin: *`, no credentials) | Public catalogue |
| [**OAuth 2.0**](https://datatracker.ietf.org/doc/html/rfc6749) / [**OpenID Connect**](https://openid.net/specs/openid-connect-core-1_0.html) | Staff login (through IAM and Keycloak) and server-to-server calls (client credentials) | Admin API and UI |

## Not used (yet)

* [**OData**](https://www.odata.org/documentation/), for BI tools querying datasets live: to explore ([open items](../../../../open-agri-stack/open-items/README.md)).
* [**OGC API – Features**](https://ogcapi.ogc.org/features/) for geography (per-unit features, paging, bounding boxes): to explore; boundaries are GeoJSON files per level today.

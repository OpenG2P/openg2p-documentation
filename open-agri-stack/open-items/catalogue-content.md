---
description: >-
  TODO: what the Agri Stack catalogue datasets still lack: variety details to
  confirm, more varieties, cross-classification, international code mappings,
  agri input and livestock catalogues, and the kebele level.
---

# Catalogue Content (TODO)

{% hint style="info" %}
**Status: open.** This page is about the content of the country pack's datasets, not the catalogue service. For the service, see [open items: catalogues](README.md#catalogues).
{% endhint %}

## Where it stands

The ETH pack's agriculture theme ([`openg2p-data`, `packs/ETH/domains/agriculture`](https://github.com/OpenG2P/openg2p-data/tree/develop/packs/ETH/domains/agriculture)) follows the Ministry of Agriculture's crop variety portal (Crop Technologies, read 2026-10-16):

| Dataset | Content | Typed attributes |
| --- | --- | --- |
| `CROP_CATEGORY` | MoA's 8 crop categories (cereals, food legumes, oilseeds, fruits and vegetables, roots and tubers, stimulant crops, industrial crops, spices and medicinal plants), plus Other | — |
| `CROP_COMMODITY` | 121 crops: MoA's 119, plus `CROP_MALT_BARLEY` and `CROP_OTHER`. `CROP_WHEAT` is retired for `CROP_BREAD_WHEAT` and `CROP_DURUM_WHEAT` | `category` (a `CROP_CATEGORY` code, required), `scientific_name` |
| `SEED_VARIETY` | 8 varieties (teff, bread wheat, maize, barley, sorghum) | `crop` (a `CROP_COMMODITY` code, required), `official_name`, `breeding_code`, `release_year`, `research_centre` |

Labels are English, with Amharic (`display_i18n.am`) where MoA gives it. Scientific names are MoA's, with spelling errors corrected (e.g. *Sorghum bicolor*, *Solanum tuberosum*, *Salvia officinalis*).

## To do

### 1. Confirm with MoA

* **Kakaba** (`VAR_WHEAT_KAKABA`): not on MoA's bread wheat page, which lists 56 of the 102 varieties it counts. It is linked to `CROP_BREAD_WHEAT`, but its official name, breeding code, release year and research centre are not filled. Confirm them (Kakaba is commonly given as Picaflor #1, Kulumsa, 2010).
* **BH661** (`VAR_MAIZE_BH661`): the portal cuts off its pedigree, so `breeding_code` is not filled.
* **Amharic labels** missing for the 9 categories and for 52 crops MoA gives none for, among them faba bean, field pea, haricot bean, cabbage, cassava, taro and yam.
* **Labels MoA shares or may have wrong:**
  * Peppermint, spearmint, Japanese mint and Spanish mint are all ናና.
  * Onion and shallot are both ሽንኩርት; sunflower and safflower are both ሱፍ.
  * Emmer wheat is አጃ, a word also used for oats.
  * White cumin's scientific name is given as *Nigella sativa*, the same as black cumin.
  * "Fine bush" has no scientific name. Its varieties (Adante, Lomami, Boston, Volta) are fine beans, so it is labelled "Fine bush bean", without a scientific name.
  * Haricot bean and common bean are both *Phaseolus vulgaris*; MoA lists them separately, so the pack does too.
* **Malt barley:** MoA lists malt barley varieties under Barley. `CROP_MALT_BARLEY` is kept (category Cereals) because it is an existing code and a separate value chain. Decide whether to keep it or retire it in favour of `CROP_BARLEY`.

### 2. More varieties, only if needed

MoA lists about 1,460 released varieties. Import them into `SEED_VARIETY` only when a registry or programme needs them (e.g. for input subsidy by variety). The portal's details pages are plain HTML, one per crop, so an import script is simple. Pages may be cut short, as bread wheat's is.

### 3. Cross-classification, only if asked

A crop has one category. Further groupings (cash crop, export crop, fodder) would be a `CROP_GROUP` dataset and an array attribute on `CROP_COMMODITY` whose items carry `x-list-ref: CROP_GROUP` (see [typed attributes](../../platform/platform-services/master-data-service/concepts.md#typed-attributes)).

### 4. International code mappings

Add optional attributes to `CROP_COMMODITY` mapping each crop to FAO's Indicative Crop Classification (WCA 2020), FAOSTAT item codes and AGROVOC concept URIs (attribute names as in [MDS design decisions](../../platform/platform-services/master-data-service/design-decisions.md)). See [standards](../architecture/standards.md#todo-agricultural-data-standards-for-the-catalogues).

### 5. Agri input catalogues (deferred)

Fertiliser, pesticide, seed and machinery products. To add one later, add a dataset file in the pack's `domains/agriculture/` with an `attribute_schema`. For example, `FERTILIZER_PRODUCT` with `type` (`x-list-ref: FERTILIZER_TYPE`), nutrient content and pack unit, or `PESTICIDE_PRODUCT` with registration number, active ingredient and target agents (`x-list-ref: INFESTATION_AGENT`). Master Data loads it with the theme, and a registry refers to it through a reference rule. No code change is needed.

### 6. Livestock catalogues

`LIVESTOCK_TYPE` and `LIVESTOCK_BREED` are generic today (breed is only improved, local or hybrid). Species and breed lists (e.g. from FAO DAD-IS), each breed tied to its species by an attribute, belong with the Livestock Registry, when it is built.

### 7. Kebele level in geography

The ETH pack stops at woreda (OCHA COD-AB). A kebele is written as text in the address (`address.json`). A kebele level needs a source with codes and boundaries (e.g. CSA or the Ethiopian Statistical Service), P-codes that nest under woredas, and a decision on how registries move from the address text to the code.

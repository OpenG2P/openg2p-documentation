# Farmer Registry

Farmer Registry is a manifestation of [OpenG2P Registry Platform](../registry/) with specifics related to a farmer registry. This registry contains the following registers:

1. Farmer Register
2. Household Register

The domain models for these registers are available in the [extensions repository](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/tree/develop/openg2p-registry-farmer-extension).

The Farmer Registry inherits all the [features of the registry platform](registry/features/).

## Versions

Refer to [versions](registry/versions/).

## Domain models

Each domain model below represents a database table in the Farmer Registry. The Farmer and Household models are **registers** (extending the core `G2PRegister` base); the remaining models are supporting tables that store related data linked to a register record. All models extend core platform base classes (`G2PRegister`, `G2PPerson`, `G2PGeo`, etc.) and add domain-specific columns. Fields inherited from the base classes (such as `internal_record_id`, `functional_record_id`, `record_name`, `status`, name fields, date of birth, gender, geo coordinates, address etc.) are not repeated here.

{% hint style="info" %}
Every register model has a corresponding **History** table (e.g., `g2p_register_history_farmers`) with the same domain columns, used for version snapshots. History tables are not listed separately below.
{% endhint %}

---

### Farmer (`g2p_register_farmers`)

Extends: `G2PRegister`, `G2PPerson`, `G2PGeo`

The primary register for individual farmer records. Inherits person-level fields (name, date of birth, gender, foundational ID) from `G2PPerson` and location fields from `G2PGeo`.

| Column | Data type | Description |
| --- | --- | --- |
| `estimated_age` | Integer | Estimated age of the farmer (used when exact date of birth is unavailable) |
| `has_personal_phone` | Boolean | Whether the farmer has a personal phone |
| `disabled` | Boolean | Whether the farmer has a disability |
| `disability_type` | String (enum) | Type of disability. Values: `VISION`, `HEARING`, `MOBILITY`, `COGNITION`, `SELF_CARE`, `COMMUNICATION` |
| `disability_severity` | String (enum) | Severity of disability. Values: `NO_DIFFICULTY`, `SOME_DIFFICULTY`, `A_LOT_OF_DIFFICULTY`, `CANNOT_DO_AT_ALL` |
| `source_of_income` | String (enum) | Primary source of income. Values: `CROP_PRODUCTION`, `LIVESTOCK_PRODUCTION`, `GOVERNMENT_NGO_SUPPORT`, `OTHERS` |
| `source_of_income_other` | String | Free-text description when `source_of_income` is `OTHERS` |
| `language_spoken` | String | Language spoken by the farmer (ISO-639-2 code, attribute lookup) |
| `education_level` | String (enum) | Educational level. Values: `ILLITERATE`, `CAN_READ_AND_WRITE`, `BASIC`, `INTERMEDIARY`, `HIGHER_EDUCATION` |
| `national_id_masked` | String | Masked representation of the national ID |

---

### Household (`g2p_register_households`)

Extends: `G2PRegister`, `G2PGeo`

Represents a farmer's household. Does not extend `G2PPerson` since a household is a group, not an individual.

| Column | Data type | Description |
| --- | --- | --- |
| `household_head` | String | Name or identifier of the household head |
| `size_of_group` | Integer | Total number of members in the household |
| `number_of_children` | Integer | Number of children in the household |
| `number_of_female_members` | Integer | Number of female members |
| `number_of_male_members` | Integer | Number of male members |
| `other_land_owner` | Boolean | Whether anyone other than the primary farmer owns land in the household |

---

### Household Member (`g2p_register_household_members`)

Extends: `G2PRegister`, `G2PPerson`, `G2PGeo`

Individual members of a household. Inherits person-level fields (name, date of birth, gender) from `G2PPerson`. Linked to a Household via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `is_disabled` | Boolean | Whether the household member has a disability |

---

### Land (`g2p_register_lands`)

Extends: `G2PRegister`, `G2PGeo`, `G2PGeoShape`

Represents a land parcel associated with a farmer. Linked to a Farmer via `link_internal_record_id`. Extends `G2PGeoShape` for polygon/boundary data in addition to point-location from `G2PGeo`.

| Column | Data type | Description |
| --- | --- | --- |
| `land_ownership_type` | String (enum) | Type of land ownership. Values: `OWNER`, `TENANT`, `CROP_SHARE` |
| `certificate_storage_id` | Text | Reference to the stored land ownership certificate (document storage ID) |
| `land_size` | String | Size of the land parcel |
| `unit` | String (enum) | Unit of land size measurement. Values: `HECTARE`, `ACRE`, `SQUARE_METER`, `SQUARE_KM`, `SQUARE_FOOT`, `SQUARE_YARD` |
| `soil_fertility` | String | Soil fertility assessment |
| `current_land_use` | String (enum) | Current use of the land. Values: `AGRICULTURAL`, `RESIDENTIAL`, `GRAZING`, `FOREST` |
| `farming_type` | String (enum) | Type of farming practised. Values: `CROP`, `LIVESTOCK`, `MIXED`, `AQUACULTURE`, `AGROFORESTRY` |
| `year_of_acquisition` | Integer | Year the land was acquired |
| `means_of_acquisition` | String | How the land was acquired (attribute lookup) |

---

### Crop (`g2p_register_crops`)

Extends: `G2PRegister`

Represents a crop cultivated by a farmer. Linked to a Farmer via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `commodity` | String | Type of crop/commodity (attribute lookup) |
| `planted_date` | Date | Date the crop was planted |
| `season` | String | Agricultural season |
| `end_use` | String (enum) | Intended end use of the crop. Values: `FOOD_HUMAN_CONSUMPTION`, `FEED_ANIMALS`, `BIOFUELS_NONFOOD`, `OTHER` |

---

### Livestock (`g2p_register_livestocks`)

Extends: `G2PRegister`

Represents livestock owned by a farmer. Linked to a Land via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `livestock_type` | String | Type of livestock (attribute lookup) |
| `breed` | String | Breed of the livestock (attribute lookup) |
| `head_count` | Integer | Number of animals |
| `livestock_system` | String (enum) | Livestock rearing system. Values: `NOMADIC_PASTORAL`, `SEMI_NOMADIC`, `SEDENTARY_PASTORAL`, `MIXED`, `INDUSTRIAL` |

---

### Farm Inputs (`g2p_register_farm_inputs`)

Extends: `G2PRegister`

Captures the agricultural inputs and resources available to a farmer. Linked to a Farmer via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `fertilizer_use` | Boolean | Whether the farmer uses fertilizers |
| `pesticide_use` | Boolean | Whether the farmer uses pesticides |
| `insecticide_use` | Boolean | Whether the farmer uses insecticides |
| `improved_seed_use` | Boolean | Whether the farmer uses improved/certified seeds |
| `water_source` | String | Primary water source (attribute lookup). E.g., Rainfed, Irrigation GW/Surface, Well, Water Harvesting, Surface Water |
| `access_to_machinery` | Boolean | Whether the farmer has access to farm machinery |
| `access_to_finance` | Boolean | Whether the farmer has access to agricultural finance/credit |

---

### Membership Details (`g2p_register_membership_details`)

Extends: `G2PRegister`

Captures cooperative and farmer cluster membership information. Linked to a Farmer via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `is_primary_cooperative_member` | Boolean | Whether the farmer is a member of a primary cooperative |
| `primary_cooperative_name` | String | Name of the primary cooperative |
| `is_cooperative_union_member` | Boolean | Whether the farmer is a member of a cooperative union |
| `cooperative_union_name` | String | Name of the cooperative union |
| `is_farmer_cluster_member` | Boolean | Whether the farmer is a member of a farmer cluster |
| `farmer_cluster_role` | String (enum) | Role within the farmer cluster. Values: `LEAD`, `DEPUTY`, `SECRETARY`, `ACCOUNTANT`, `MEMBER` |

---

### Poverty Score (`g2p_register_poverty_scores`)

Extends: `G2PRegister`

Stores poverty assessment scores for a household. Linked to a Household via `link_internal_record_id`.

| Column | Data type | Description |
| --- | --- | --- |
| `poverty_score` | String | Computed or assessed poverty score value |
| `poverty_score_type` | String | Type/methodology of the poverty score (e.g., PMT, PPI) |

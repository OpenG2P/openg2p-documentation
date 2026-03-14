---
description: ORM Models for Defining Registry Domain Models
---

# ORM models

The OpenG2P Registry platform provides a set of **base ORM models** to help implementers define the domain models required for a registry.

The primary base models are:

* `g2p_register`
* `g2p_table`
* `g2p_program_register`

These models include a set of **core attributes required to support registry functionality** such as identity management, record linking, and workflow processing.

It is **mandatory** that all domain models defined within a registry **extend one of these base models**, depending on the role the dataset plays within the registry.

***

### Core Attributes Provided by Base Models

#### g2p\_register

**`internal_record_id`**

This is the **internal primary key** of the record and is implemented as a **UUID**.

All internal retrieval operations and business logic within the registry rely on this attribute to uniquely identify records.

***

**`functional_record_id`**

This represents the **functional identifier** assigned to records within a register.

By default, the OpenG2P Registry uses the **MOSIP ID Generator** to allocate functional IDs. The MOSIP ID Generator produces **numeric identifiers** with configurable parameters such as:

* Number of digits
* Prohibited combinations or sequences
* Check-digit computation

These identifiers are typically the **externally visible IDs** used by registry users and external systems.

***

**`link_internal_record_id`**

This attribute is used to **link a record in one register to a record in another register**.

For example:

* An **Individual** in an Individual Register belongs to a **Household** in a Household Register.
* In this case, the Individual record stores the `link_internal_record_id` of the corresponding Household record.

This mechanism enables **relationships between registers** while maintaining independent datasets.

***

**`link_foundational_id`**

This attribute is used to **link registry records to a foundational identity system**, when the registry itself does not maintain a register of individuals.

For example:

A **Vehicle Registry** may maintain a Vehicle Register but may not maintain a register of individuals. However, vehicles still need to be linked to their owners.

If the country or region has a **foundational identity system** for individuals, this attribute can be used to link the asset (e.g., the vehicle) to the individual’s foundational ID.

***

**`record_name`**

This attribute represents the **human-readable name of the record**.

Domains can configure how the `record_name` is constructed based on attributes within the register. The platform provides **extensibility hooks** that allow implementation teams to define custom logic for generating this value.

Customizations should be implemented in the domain service layer by extending  the [g2p\_register\_domain\_service](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/services/g2p_register_domain_service.py). Reference implementation is available in [g2p\_register\_domain\_service\_farmer](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/register_domain/services/g2p_register_domain_service_farmer.py)

which demonstrates how the `record_name` attribute can be populated using domain-specific attributes.

***

**search\_text**

This attribute is used to enable **efficient text search across registry records**.

The `search_text` column is indexed using the PostgreSQL **`pg_trgm` (trigram) extension**, which allows the registry to support:

* **Partial string searches**
* **Fuzzy matching**
* **Typo-tolerant lookups**

This capability makes it easier for users to locate records even when the exact value of an attribute is not known.

The platform provides **extensibility** that allows domain implementations to determine which attributes should be combined to populate the `search_text` field. For example, implementations may choose to include fields such as names, phone numbers, identifiers, or other searchable attributes relevant to the domain.

Customizations should be implemented in the domain service layer by extending  the [g2p\_register\_domain\_service](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/services/g2p_register_domain_service.py). Reference implementation is available in [g2p\_register\_domain\_service\_farmer](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/register_domain/services/g2p_register_domain_service_farmer.py)

which demonstrates how the `search_text` attribute can be populated using domain-specific attributes.

***

#### g2p\_table

**`internal_record_id`**

This is the **internal primary key** of the record and is implemented as a **UUID**.

All internal retrieval operations and business logic within the registry rely on this attribute to uniquely identify records.

**`link_internal_record_id`**

This attribute is used to **link a record in a Table to a record in another Register or Table**.

For example, consider an **Individual Register** where additional information about individuals is stored in a supporting table called `g2p_table_utilities`. This table may contain a list of **public utilities subscribed to by an individual**, such as electricity, water, or internet services.

In this case, each record in `g2p_table_utilities` will store the **`internal_record_id` of the corresponding Individual record** in its `link_internal_record_id` field.

This mechanism enables the platform to support **relationships between datasets**, including:

* A **Register linked to another Register**
* A **Table linked to a Register**
* A **Table linked to another Table**

At the same time, it allows each dataset to remain **logically independent**, while still maintaining referential relationships between related records.

g2p\_register\_individuals

<table data-full-width="true"><thead><tr><th width="199.078857421875">internal_record_id</th><th>functional_record_id</th><th>nam</th></tr></thead><tbody><tr><td><pre><code>7f1c2a9e
</code></pre></td><td><pre><code>1000452
</code></pre></td><td><pre><code>Ravi Kumar
</code></pre></td></tr></tbody></table>

g2p\_table\_utilities

<table><thead><tr><th width="342.7225341796875">internal_record_id</th><th>utility_type</th><th>subscription_id</th><th>link_internal_record_id</th></tr></thead><tbody><tr><td><pre><code>2a6b3e5c
</code></pre></td><td>Electricity</td><td></td><td><pre><code>7f1c2a9e
</code></pre></td></tr><tr><td><pre><code>7b6g3y4p
</code></pre></td><td>Water</td><td></td><td><pre><code>7f1c2a9e
</code></pre></td></tr><tr><td><pre><code>8c7h4u5q
</code></pre></td><td>Internet</td><td></td><td><pre><code>7f1c2a9e
</code></pre></td></tr></tbody></table>

***

####

#### g2p\_program\_register

### Convenience Models Provided by the Platform

In addition to the base models, the platform provides **convenience models** that simplify the implementation of common domain patterns.

#### `g2p_person`

This model should be used when the register represents **individual persons**.

Typical examples include:

* Farmer Register
* Disability Register
* Individual Register

The model provides commonly required attributes and structures relevant to representing individuals

```

internal_record_id    |    name 
UUID-1                |    Ravi Kumar

Utilities Table (g2p_table_utilities)
internal_record_id    | utility_type        |link_internal_record_id 
1                    | Electricity        |    UUID-1 
2                    | Water                 |         UUID-1 
3                    | Internet | UUID-1
```

```
```

### Utilities Table (g2p\_table\_utilities)

utility\_id | utility\_type | link\_internal\_record\_id 1 | Electricity | UUID-1 2 | Water | UUID-1 3 | Internet | UUID-1

***

#### `g2p_geo`

This model is used when register records require **geographical or address information**.

When a register extends `g2p_geo`, it stores only the **lowest level geographical administrative identifier**.

For example, consider a country with the following administrative hierarchies:

**Rural hierarchy**

Country → State → District → Sub-District → Panchayat → Village

**Urban hierarchy**

Country → State → District → Sub-District → City → Ward

In such cases, the register record stores only the **Village ID or Ward ID** in:

`g2p_geo.geo_lowest_level_value_id`

The platform then automatically derives the **full administrative hierarchy** and stores it as a JSON structure in:

`g2p_geo.geo_code_hierarchy_json`

This approach ensures that:

* The register records remain **compact and normalized**
* The **complete location hierarchy remains easily accessible** when needed.

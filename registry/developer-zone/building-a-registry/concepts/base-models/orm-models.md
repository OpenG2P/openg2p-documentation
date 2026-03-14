---
description: ORM Models for Defining Registry Domain Models
---

# ORM models

The OpenG2P Registry platform provides a set of **base ORM models** to help implementers define the domain models required for a registry.

The primary base models are:

* G2PRegister
* G2PTable
* G2PProgramRegister

These models include a set of **core attributes required to support registry functionality** such as identity management, record linking, and workflow processing.

It is **mandatory** that all domain models defined within a registry **extend one of these base models**, depending on the role the dataset plays within the registry.

***

### Core Attributes Provided by Base Models

#### G2PRegister (g2p\_register)

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

#### G2PTable (g2p\_table)

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

An example is given below

**g2p\_register\_individuals** (Register to manage individuals)

<table data-full-width="true"><thead><tr><th width="199.078857421875">internal_record_id</th><th>functional_record_id</th><th>nam</th></tr></thead><tbody><tr><td><pre><code>7f1c2a9e
</code></pre></td><td><pre><code>1000452
</code></pre></td><td><pre><code>Ravi Kumar
</code></pre></td></tr></tbody></table>

**g2p\_table\_utilities** (TABLE to manage an individual's utility subscriptions)

<table data-full-width="true"><thead><tr><th width="166.7701416015625">internal_record_id</th><th width="142.775146484375">utility_type</th><th width="159.03955078125">subscription_id</th><th>link_internal_record_id</th></tr></thead><tbody><tr><td><pre><code>2a6b3e5c
</code></pre></td><td><pre><code>Electricity
</code></pre></td><td><pre><code>9000848
</code></pre></td><td><pre><code>7f1c2a9e
</code></pre></td></tr><tr><td><pre><code>7b6g3y4p
</code></pre></td><td><pre><code>Water
</code></pre></td><td><pre><code>18579594
</code></pre></td><td><pre><code>7f1c2a9e
</code></pre></td></tr><tr><td><pre><code>8c7h4u5q
</code></pre></td><td><pre><code>Sewage
</code></pre></td><td><pre><code>18589583
</code></pre></td><td><pre class="language-actionscript-3"><code class="lang-actionscript-3">7f1c2a9e
</code></pre></td></tr></tbody></table>

***

#### G2PProgramHistory (g2p\_program\_history)

The `g2p_program_register` model is used to store **applications submitted for a specific benefit program**. Each record represents an application submitted by an individual or household to be considered for participation in a program.

The following are the key attributes associated with this model.

<table data-full-width="true"><thead><tr><th width="176.470458984375">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>internal_record_id</td><td>The internal <strong>UUID primary key</strong> of the application record. This identifier is used internally by the registry for data retrieval, relationships, and business logic.</td></tr><tr><td>program_id</td><td>The unique identifier of the <strong>benefit program</strong> for which the application is submitted. This links the application record to the corresponding program defined in the Program and Benefit Management System (PBMS).</td></tr><tr><td>program_mnemonic</td><td>A short, human-readable <strong>code or mnemonic</strong> representing the program. This is typically used for easier identification of the program in logs, integrations, and operational workflows.</td></tr><tr><td>foundational_id</td><td>The <strong>foundational identity identifier</strong> of the applicant, if available. This typically corresponds to a national or regional foundational ID used to uniquely identify individuals.</td></tr><tr><td>link_foundational_id</td><td>Used to link the application to another <strong>foundational identity record</strong>, when the application relates to a different individual than the applicant. For example, a household member applying on behalf of another individual.</td></tr></tbody></table>

### Convenience Models Provided by the Platform

In addition to the base models, the platform provides **convenience models** that simplify the implementation of common domain patterns.

#### G2PPerson (g2p\_person)

This model should be used when the register represents **individual persons**.

Typical examples include:

* Farmer Register
* Disability Register
* Individual Register

The model provides commonly required attributes and structures relevant to representing individuals.

***

#### G2PGeo (g2p\_geo)

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

### Base Models for Version History

The OpenG2P Registry platform provides **base models** to store **version history for registry records** in order to support auditability, traceability, and change tracking.

Whenever a record in a register or table is modified, the platform stores the previous version of the record in a corresponding **history model**. This allows the system to maintain a **complete historical trail of changes** made to registry data over time.

The following models are used to store version history:

<table><thead><tr><th width="315.04046630859375">History Model</th><th>Description</th></tr></thead><tbody><tr><td><code>G2PRegisterHistory</code><br><code>e.g. G2PRegisterHistoryHouseholds</code></td><td>Stores historical versions of records from registers that extend the <code>G2PRegister</code> base model.</td></tr><tr><td><code>G2PTableHistory</code><br><code>e.g. G2PTableHistoryUtilities</code></td><td>Stores historical versions of records from tables that extend the <code>G2PTable</code> base model.</td></tr><tr><td><code>G2PGeoHistory</code><br><code>e.g. G2PRegistryHistoryIndividuals</code></td><td>Stores historical versions of geographic data associated with records that extend the <code>G2PGeo</code> model.</td></tr><tr><td><code>G2PPersonHistory</code><br><code>e.g. G2PRegistryHistoryIndividuals</code></td><td>Stores historical versions of person-related attributes for registers that extend the <code>G2PPerson</code> model.</td></tr></tbody></table>

#### Purpose of Version History

The version history mechanism enables the registry platform to:

* Maintain a **complete audit trail** of data changes
* Support **traceability of record updates over time**
* Enable **data rollback or investigation** when required
* Provide **transparency for governance and compliance processes**

By separating historical records into dedicated history models, the platform ensures that **operational datasets remain optimized for current usage**, while still preserving full historical information.

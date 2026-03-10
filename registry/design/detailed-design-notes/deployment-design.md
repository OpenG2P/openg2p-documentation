---
description: How to create a Registry Deployment for a target Domain
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Deployment Design

Let's say we need to deploy a Household Registry and we have ascertained that we need to have two Registers in the Registry

1. **Household Register**
2. **Individuals Register**

In addition to these two Registers, let's say, we also need to capture the vehicles that are owned by the Individuals.

If Vehicles are only additional peripheral information and does not involving allocating a functional ID to every Vehicle, the Vehicle information store (table) is just a simple table (where one individual can have multiple vehicles), instead of being configured as a "REGISTER"

3. **Vehicles Table**

### 1. Create a Household Registry Extension Pack

Fork the repo - [https://github.com/OpenG2P/openg2p-registry-gen2-extensions](https://github.com/OpenG2P/openg2p-registry-gen2-extensions)

There are reference implementations (farmer\_extension) available here. Create a suitable folder here, in our case - "household\_extension"

### 2. Define ORM models for the identified Registers and Tables

<mark style="color:$primary;">**Target folder**</mark>\
<mark style="color:blue;">openg2p-registry-farmer-extension/src/openg2p\_registry\_farmer\_extension/register\_domain</mark>

The **ORM Model** defines how a domain entity is **persisted in the registry database**. It specifies the fields, identifiers, and relationships that represent the entity in storage.

Define ORM models to establish the **database structure for the registry records**, enabling the platform to store, retrieve, and manage the entity data.

#### G2PRegisterHousehold

```py
class G2PRegisterHousehold(G2PRegister, G2PGeo): 
tablename = "g2p_register_households"
```

Here, G2PRegister is a base class that needs to be extended by all REGISTER Classes

G2PRegister brings the following attributes into the inherited REGISTER Class

```py
class G2PRegister(BaseORMModel): 
    abstract = True
    internal_record_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True, unique=True, index=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True, index=True) # Link to internal_record_id of the parent
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    record_image_storage_id: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    last_approved_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    last_approved_by: Mapped[str] = mapped_column(String, nullable=False)
    search_text: Mapped[str] = mapped_column(Text, nullable=True)
```

The G2PRegisterHousehold class needs to extend G2PGeo, if the Household register has address attributes.    &#x20;

```py
class G2PGeo(BaseORMModel):
    __abstract__ = True
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    altitude: Mapped[str] = mapped_column(String, nullable=True)
    plus_code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    address_line_2: Mapped[str] = mapped_column(String, nullable=True)
    postal_code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    geo_lowest_level_value_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    geo_code_hierarchy_json: Mapped[str] = mapped_column(JSONB, nullable=True)
```

#### G2PRegisterIndividual

```
class G2PRegisterIndividual(G2PRegister, G2PPerson, G2PGeo): 
tablename = "g2p_register_individuals"
```

The G2PPerson abstract class brings the following attributes into the Register.&#x20;

<pre class="language-py"><code class="lang-py"><strong>class G2PPerson(BaseORMModel): 
</strong>    abstract = True
    foundational_id: Mapped[str] = mapped_column(String, nullable=True, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    given_name: Mapped[str] = mapped_column(String, nullable=True)
    prefix: Mapped[str] = mapped_column(String, nullable=True)
    suffix: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(String, nullable=True)
    birth_date: Mapped[str] = mapped_column(Date, nullable=True)
    phone_numbers: Mapped[list] = mapped_column(JSONB, nullable=True)
    emails: Mapped[list] = mapped_column(JSONB, nullable=True)
    marital_status: Mapped[MaritalStatusEnum] = mapped_column(String, nullable=True)
    occupation: Mapped[str] = mapped_column(String, nullable=True)
    income_level: Mapped[str] = mapped_column(String, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)
    education_level: Mapped[str] = mapped_column(String, nullable=True)
    registration_date: Mapped[str] = mapped_column(Date, nullable=True)
</code></pre>

#### G2PTableVehicles

```py
class G2PTableVehicle(G2PTable): 
tablename = "g2p_table_vehicles"
```

Since, we are treating vehicles as just a table of attributes for an individual, we only extend **G2PTable** and not G2PRegister. Any store, where we are not managing functional IDs, where there is no formal registry functionalities required, we can consider using G2PTable rather than G2PRegister. The G2PTable brings the following attributes

<pre class="language-py"><code class="lang-py"><strong>class G2PTable(BaseORMModel): 
</strong>    abstract = True
    internal_record_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True, index=True) # Link to internal_record_id of the parent
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    last_approved_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    last_approved_by: Mapped[str] = mapped_column(String, nullable=False)
</code></pre>

### 3. Define ORM Models for version histories of Registers and Tables

#### G2PRegisterHistoryHousehold

```py
class G2PRegisterHistoryHousehold(G2PRegisterHistory, G2PGeo): 
tablename = "g2p_register_history_households"
```

#### G2PRegisterHistoryIndividual

```py
class G2PRegisterHistoryHousehold(G2PRegisterHistory, G2PGeo): 
tablename = "g2p_register_history_individuals"
```

#### G2PTableHistoryVehicle

```
class G2PTableHistoryVehicle(G2PTableHistory): 
tablename = "g2p_table_history_vehicles"
```

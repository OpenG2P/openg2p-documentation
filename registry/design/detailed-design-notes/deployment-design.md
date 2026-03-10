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

### 1. ORM Models for the identified Registers and Tables

The **ORM Model** defines how a domain entity is **persisted in the registry database**. It specifies the fields, identifiers, and relationships that represent the entity in storage.

Implementers define an ORM model to establish the **database structure for the registry records**, enabling the platform to store, retrieve, and manage the entity data.

We need to create the following ORM Models

```
class G2PRegisterHousehold(G2PRegister, G2PGeo): 
tablename = "g2p_register_households"
```

Here, G2PRegister is a base class that needs to be extended by all REGISTER Classes

G2PRegister brings the following attributes into the inherited REGISTER Class

class G2PRegister(BaseORMModel): **abstract** = True

<pre><code><strong>internal_record_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
</strong>functional_record_id: Mapped[str] = mapped_column(String, nullable=True, unique=True, index=True)
link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True, index=True) # Link to internal_record_id of the parent
link_foundational_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
record_name: Mapped[str] = mapped_column(String, nullable=True)
record_image_storage_id: Mapped[str] = mapped_column(Text, nullable=True)
created_by: Mapped[str] = mapped_column(String, nullable=False)
created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
last_approved_at: Mapped[str] = mapped_column(DateTime, nullable=False)
last_approved_by: Mapped[str] = mapped_column(String, nullable=False)
search_text: Mapped[str] = mapped_column(Text, nullable=True)
</code></pre>


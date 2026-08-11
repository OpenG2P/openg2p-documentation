# Registry themes

## OpenG2P Registry Gen2 - Theme Management Design

### Repositories

* registry-platform/core/openg2p-registry-core
* registry-gen2-apis

***

### Models

#### Existing Models - Changes

**g2p\_registry\_configuration**

* **New Attribute**: registry\_theme\_id

#### New Models

**registry\_themes**

| Column               | Type         | Constraint       |
| -------------------- | ------------ | ---------------- |
| theme\_id            | UUID/Integer | PK               |
| theme\_mnemonic      | String(50)   | NOT NULL, UNIQUE |
| is\_factory\_shipped | Boolean      | NOT NULL         |

**registry\_theme\_values**

| Column           | Type         | Constraint       |
| ---------------- | ------------ | ---------------- |
| theme\_value\_id | UUID/Integer | PK               |
| theme\_id        | UUID/Integer | Non-Unique Index |
| attribute\_name  | ENUM         | NOT NULL         |
| attribute\_value | LONGTEXT     | NOT NULL         |

**Theme Attributes (attribute\_name ENUM)**

* primary\_color\_1
* primary\_color\_2
* secondary\_color\_1
* secondary\_color\_2
* secondary\_color\_3
* neutral\_color\_1
* neutral\_color\_2
* font\_family
* font\_url
* dashboard\_image

***

### API Methods

#### Endpoint: /registry-configuration <mark style="color:$primary;">(existing controller)</mark>

**get\_registry\_configuration (POST)**

* Get registry configuration
* Response: registry configuration object with theme reference

**update\_registry\_configuration (POST)**

* Update registry configuration
* Response: updated configuration

#### Endpoint: /registry-theme <mark style="color:$primary;">(new controller)</mark>

**get\_all\_themes (POST)**

* Get all available themes
* Response: list of themes

**create\_theme (POST)**

* Create custom theme (non-factory)
* Request: { theme\_mnemonic, theme\_values\[] }
* Response: theme\_id

**remove\_theme (POST)**

* Delete custom theme (factory-shipped cannot be deleted)
* Request: { theme\_id }
* Response: success confirmation

**update\_theme\_values (POST)**

* Update theme values (all 10/12 attributes together)
* Request: { theme\_id, theme\_attribute\_values\[] }
* Response: theme\_id

**get\_theme\_values (POST)**

* Get all theme values for a theme
* Request: { theme\_id }
* Response: list of theme attribute values


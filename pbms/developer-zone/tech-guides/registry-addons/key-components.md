# Key Components

Within the repository you’ll find the following relevant sub-directories:

* [`g2p_registry_addon`](https://github.com/OpenG2P/pbms/tree/develop/odoo/extensions/) — core registry models, access rights, views etc.
* [`g2p_registry_type_addon`](https://github.com/OpenG2P/pbms/tree/develop/odoo/extensions/) — registry “types” or variants that act as a base for viewing the core registry modules over PBMS.

Each module follows the typical Odoo addon structure: manifest file (`__manifest__.py`), Python models, XML views, security/access files, possibly data or demo CSVs.

***

### Core Registry Add-on: `g2p_registry_addon`

This add-on provides the baseline registry framework for PBMS, handling the registrant models, UI scaffolding and JS/CSS enhancements.

<table><thead><tr><th width="170">File</th><th>Purpose</th></tr></thead><tbody><tr><td><code>__manifest__.py</code></td><td>Module metadata: name, version, data/ security/ view files to load. Declares dependency on <code>g2p_pbms</code> and other modules.</td></tr><tr><td><code>models/</code></td><td>Python files defining the core Registry ORM models. This is the foundation of the registry infrastructure. All inheriting from a base <code>g2p.registry</code> ORM.</td></tr><tr><td><code>views/</code></td><td>XML files that define the user interface: list/tree views, form views, search filters for the registry models. Mostly inheriting and updating existing views already defined in the main odoo module. </td></tr><tr><td><code>security/</code></td><td>Access control definitions containing model access rules. Ensures correct permissions for reading/editing registry models. Access group must be from the main PBMS module (<code>g2p_pbms.&#x3C;group_name></code> )</td></tr><tr><td><code>static/</code></td><td>Static assets (JS/CSS) used for UI enhancements and browser based event logic or translation files (po) if the module or needs multi-language support.</td></tr><tr><td><code>data/</code> (optional)</td><td>Initial seed data or configuration records required for basic registry operation (e.g., default ID type entries, registry tags).</td></tr></tbody></table>

***

### Registry Type Add-on: `g2p_registry_type_addon`

This module lets you communicate to the PBMS  about the registries you are going to be defining in `g2p_registry_addon` , which helps in enabling front-loading of PBMS UI with registry type data since registry specific UI and model enhancements are performed later by the  core registry add-on module.

<table><thead><tr><th width="170">File</th><th>Purpose</th></tr></thead><tbody><tr><td><code>__manifest__.py</code></td><td>Metadata for the specific registry type module: declares dependency on some odoo inbuilt modules.</td></tr><tr><td><code>models/</code></td><td>Python files defining ORM models for target model mapping. These are standalone and very minimal, only storing the model names and their target registry names.</td></tr><tr><td><code>security/</code></td><td>Access rules specific to this module, if applicable. Generally not needed.</td></tr><tr><td><code>static/</code></td><td>Contains the JS/CSS, if needed. Generally, only stores the icon in the <code>/description</code> folder.</td></tr></tbody></table>

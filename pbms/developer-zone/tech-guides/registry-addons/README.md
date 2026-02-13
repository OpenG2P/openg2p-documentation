# Registry Addons

This guide provides details on implementing the [Registry Addon Odoo Modules](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions) for integration with PBMS Odoo.

## Overview

The registry modules, namely `g2p_registry_addon` and `g2p_registry_type_addon` serve multiple purposes including:

* Standardize contract for interacting with various **G2P Registries** within the PBMS Odoo.
* Abstraction of registry specific views, models, security and static files from the main odoo module which ensures consistent behavior across different registry integrations.
* Custom implementations of these modules allow developers to integrate new registries (for example, `farmer`, `student`, or `worker` registries) without modifying the PBMS Odoo modules' core logic.

{% hint style="info" %}
These registry add-ons do not reflect the data stored in G2P Registry, these are present in PBMS for viewing and ideation purposes only.
{% endhint %}

You can find the the entire set of odoo addons' implementation [here](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions), which also includes custom implementation for [`farmer` and `student` registries](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/tree/3.0/g2p_registry_addon/models).

{% content-ref url="key-components.md" %}
[key-components.md](key-components.md)
{% endcontent-ref %}

{% content-ref url="example-implementation-workflow.md" %}
[example-implementation-workflow.md](example-implementation-workflow.md)
{% endcontent-ref %}

---
description: WORK IN PROGRESS
---

# G2P Enumerator

### Module name

g2p\_enumerator

### Module title

OpenG2P Enumerator

### Technology base

odoo

### Functionality

* The `g2p_enumerator` module facilitates the management and tracking of enumerator data within the OpenG2P system. It includes the collection of geographical data and other relevant information of enumerators.&#x20;

#### Design notes <a href="#design-notes" id="design-notes"></a>

* The `g2p_enumerator` module is designed to be an integral part of the OpenG2P system, ensuring that enumerator data is seamlessly integrated with other registrant information.
* The enumerator details are added as a tab within the `res.partner` form view to provide a consolidated view of all relevant data.
* Special attention has been given to ensure that geographical data collected by enumerators is accurately recorded and easily accessible.

### Relationships with other entities

#### Dependencies

* `base`
* `mail`
* `contacts`
* `g2p_registry_base`
* `g2p_registry_group`

#### User interface <a href="#user-interface" id="user-interface"></a>

* The enumerator details are integrated into the user interface by adding a new page inside the group form view. This page, labeled "**Enumerator Details**," includes fields for **enumerator name, ID, data collection date, and location data (latitude, longitude, altitude, accuracy**).

#### Configuration <a href="#configuration" id="configuration"></a>

* &#x20;NA&#x20;

#### Source code <a href="#source-code" id="source-code"></a>

https://github.com/OpenG2P/openg2p-registry/tree/17.0-develop/g2p\_enumerator​

#### Installation <a href="#installation" id="installation"></a>

* Ensure that the module dependencies ("base," "mail," "contacts," "g2p\_registry\_base") are installed
* Install the "G2P Registry: Group" module from the Odoo Apps interface

#### ​ <a href="#undefined" id="undefined"></a>

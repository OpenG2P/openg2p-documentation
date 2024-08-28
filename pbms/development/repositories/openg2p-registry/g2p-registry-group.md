# G2P Registry: Groups

### Module name

g2p\_registry\_group

### Module title

G2P Registry: Groups

### Technology base

\<Odoo>

### Functionality

* Users can create new groups with customizable configurations
* Configure group-specific settings such as access permissions and visibility
* **Manage Group Memberships**
  * Effortlessly add or remove individuals from groups
  * Track historical membership changes for auditing purposes
* **Fine-grained Access Control**
  * Utilizes the "security/ir.model.access.csv" file to define precise access control rules
  * Ensures that only authorized users can perform specific actions within the module
* **Categorize Groups**
  * Define different kinds of groups to categorize them based on specific criteria
  * Enhances organization and usability by grouping similar entities together
* **Tailored User Interface**
  * Introduces custom views through "views/groups\_view.xml" for an intuitive and user-friendly experience
  * Optimizes the display of group-related information for better usability
* **Configure Membership Views**
  * Utilizes "views/membership\_kinds\_view.xml" to configure views related to membership kinds within groups
  * Enhances the representation of membership-related data

### Design notes

NA

### Relationships with other entities

**Dependencies**

Module dependencies&#x20;

* base
* mail
* contacts
* g2p\_registry\_base

### User interface

NA

### Configuration

* After installation, configure group entitlement sequences
* Review and adjust security settings based on organizational requirements

### Source code

[https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_group](https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_group)

### Installation

* Ensure that the module dependencies ("base," "mail," "contacts," "g2p\_registry\_base") are installed
* Install the "G2P Registry: Groups" module from the Odoo Apps interface

---
description: Upgrading a deployment
---

# Upgrades

* Upgrades using Helm upgrade feature via Rancher
* Complexity of upgrades depends on the level of changes
* In general, the persistence storage like the database is preserved during upgrades
* Any Odoo database incompatible changes have to be dealt at Odoo level - Odoo provides are feature to upgrade database via its UI
* For non-Odoo database changes, suitable migration scripts must be provided.
* An upgrade must be thoroughly tested in staging before pushing in production

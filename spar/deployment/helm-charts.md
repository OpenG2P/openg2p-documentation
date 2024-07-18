---
description: SPAR Master Helm Chart
---

# Helm Charts

SPAR and all its dependencies are installed using a single\* [Helm chart](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/charts). Following dependent components are installed with the option to deselect them:

* SPAR Mapper
* SPAR Self Service API
* SPAR Self Service UI
* Keymanager

#### Database <a href="#database" id="database"></a>

Postgresql is installed as part of the above chart in the same namespace. The default database created is `spardb`.

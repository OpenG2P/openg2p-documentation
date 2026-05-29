---
description: G2P Bridge Master Helm Chart
---

# Helm Charts

G2P Bridge and all its dependencies are installed using a single\* [Helm chart](https://github.com/OpenG2P/openg2p-g2p-bridge-deployment/tree/develop/charts). Following dependent components are installed with the option to deselect them:

* G2P Bridge Partner API
* G2P Bridge Celery Beat Producers
* G2P Bridge Celery Workers

#### Database <a href="#database" id="database"></a>

Postgresql is installed as part of the above chart in the same namespace. The default database created is `openg2p_g2p_bridge_db`.

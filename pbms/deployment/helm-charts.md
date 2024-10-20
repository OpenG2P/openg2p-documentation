---
description: PBMS Master Helm Chart
---

# Helm Charts

PBMS and all its dependencies are installed using a single\* [Helm chart](https://github.com/OpenG2P/openg2p-pbms-deployment/tree/develop/charts).  The following dependent components are installed with the option to deselect them:

* PBMS Odoo Package (Odoo + PostgreSQL)
* Mail SMTP server
* MinIO
* ODK Central
* Keymanager
* OpenSearch
* Reporting (Reporting Framework + Reporting Init)
* Superset
* eSignet

{% hint style="info" %}
The chart has been split into parts to address the Kubernetes ETCD limitation. \
[Learn more](https://docs.openg2p.org/deployment/helm-charts#helm-chart-size-limitation)<mark style="color:blue;">>></mark>
{% endhint %}

### Database <a href="#database" id="database"></a>

Postgresql is installed as part of the above chart in the same namespace. The default database created is `pbmsdb`.

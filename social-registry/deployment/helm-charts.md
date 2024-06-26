---
description: Social Registry Master Helm Chart
---

# Helm Charts

Social Registry and all its dependencies are installed using a single\* [Helm chart](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/develop/charts).  Following dependent components are installed with the option to deselect them:

* Social Registry Odoo Package (Odoo + PostgreSQL)
* Mail SMTP server
* MinIO
* ODK Central
* Keymanager
* OpenSearch
* Reporting (Reporting Framework + Reporting Init)

{% hint style="info" %}
\* The chart has been split into parts to address the Kubernetes ETCD limitation. [Learn more >>](../../deployment/helm-charts.md#helm-chart-size-limitation)
{% endhint %}

## Database

Postgresql is installed as part of the above chart in the same namespace. The default database created is `socialregistrydb`.

---
description: Work in progress
---

# Monitoring and Reporting

## Introduction

Monitoring the status of programs and registries is vital for program administrators. OpenG2P integrates a [reporting framework](https://github.com/mosip/reporting) that lets users create dashboards of their choice to visualise data. The framework uses open-source technology components to create a pipeline of data flowing from the databases to visualisation tools. A sample dashboard is given below:

<figure><img src="../../.gitbook/assets/reporting-dashboard.png" alt=""><figcaption></figcaption></figure>

## Reporting infra

<figure><img src="../../.gitbook/assets/reporting-infra (1).png" alt=""><figcaption></figcaption></figure>

Details of this infrastructure may be found [here](https://github.com/mosip/reporting).

## New reporting infra

{% hint style="info" %}
**THIS IS WORK IN PROGRESS**

1. Apache Superset (with Postgres) for data analysis and visualization
2. Kibana + Elasticsearch for parsing log data and showing various sliced and diced data. (this replaces by OpenSearch)
3. Grafana + Prometheus for real time resource monitoring

Apache Superset is fully free (unlike Metabase) and seems to have a bigger community and features. It perhaps requires more development support than Metabase.
{% endhint %}

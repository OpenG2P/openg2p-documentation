# 📔 Dashboards Creation Guide

This document contains instructions for the developers (or dashboard creators) to create dashboards to visualize data on OpenSearch.

## Prerequisites

* OpenSearch and Reporting are installed and user roles are allocated for being able to access OpenSearch.

## Procedure

* Go to OpenSearch Dashboards -> Dashboard Management -> Index Pattern. Create an Index Pattern with following parameters:
  * Index Pattern Name : schema name + table name with wildcard to match all environments. Example `*.public.res_partner*` or `*.public.g2p_program_membership` .
  * Timestamp field: `@timestamp_gen` .
* Go to Discover and select the Index Pattern (from the menu on the top left) to look at the data present in OpenSearch.
* Go to Visualization (or Visualize menu), and create all the visualizations as per your requirement with appropriate names. Each visualization corresponds to one graph/metric/chart.
* Go to Dashboards. Create a Dashboard, and add all the visualization created before to this dashboard. Each Dashboard is a collection of visualizations. Lay out the position and size of the visualizations on the Dashboard and save it.
* Export Dashboard from Saved Object menu (include related objects while exporting).

[Learn more>>](https://opensearch.org/docs/latest/dashboards/dashboard/index/)


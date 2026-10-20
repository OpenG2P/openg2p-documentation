---
description: >-
  Deploying the Crop Sown Registry: install order and the Jobs that run on
  install and upgrade.
---

# Deployment

This page lists the order and what runs on install. What the Crop Sown Registry is and how it is packaged: [Crop Sown Registry](../README.md#how-it-is-packaged). The install steps and choices: [Deploying on Rancher](rancher.md).

## Order

1. [Infrastructure setup](../../../../operations/deployment/infrastructure-setup/) and [environment creation](../../../../operations/deployment/environment-setup-multi-node.md).
2. **commons-base**, then **commons-services**, in the namespace ([Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md)). Which commons-services settings it needs: [Prerequisites](rancher.md#prerequisites).
3. The Crop Sown Registry: [Deploying on Rancher](rancher.md).

The Farmer Registry is not needed ([why](../README.md#how-it-relates-to-the-farmer-registry)).

## What happens on install

| Order | Job | Does |
| --- | --- | --- |
| Regular Job | the `iam-register` Job | Registers the staff portal's roles and permissions in IAM. A failure here does not fail the release |
| Hook, weight 10 | `<release>-db-seed` | Waits for the APIs and for AWE. Loads the registers, activity types, indicators, ODK mapping, Cluster screens, reporting views, DCI templates and Cluster approval policies. With **Load Sample Data**, the two sample clusters |
| Hook, weight 20 | `<release>-activity-samples` | Only with **Load sample crop seasons**. Records the sample crop seasons. **Fails the release** if any cannot be loaded |
| Hook, weight 25 | `<release>-sanity` | The platform's smoke tests: the partner API is up and serves DCI search |

Helm stops at the first failed hook, so a missing Job means an earlier one failed.

The seed is idempotent. On upgrade, activity types, indicators and the ODK mapping are updated in place. Cluster screens are inserted once; changes to them need an upgrade script (see [Customisation](../customisation.md#clusters)).

{% hint style="warning" %}
db-seed waits for AWE. If AWE in commons-services is down, db-seed blocks, the install times out, and the later Jobs are never created. If you see no sanity Job, check db-seed and commons-services first.
{% endhint %}

## Next

* [Deploying on Rancher](rancher.md): prerequisites, choices, sample data, ODK, checks after install
* [Customisation](../customisation.md): what a country changes

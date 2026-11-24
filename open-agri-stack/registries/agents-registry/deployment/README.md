---
description: >-
  Deploying the Agents Registry: install order and the Jobs that run on install
  and upgrade.
---

# Deployment

This page lists the order and what runs on install. What the Agents Registry is and how it is packaged: [Agents Registry](../README.md#how-it-is-packaged). The install steps and choices: [Deploying on Rancher](rancher.md).

## Order

1. [Infrastructure setup](../../../../operations/deployment/infrastructure-setup/) and [environment creation](../../../../operations/deployment/environment-setup-multi-node.md).
2. **commons-base**, then **commons-services**, in the namespace ([Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md)). Which commons-services settings it needs: [Prerequisites](rancher.md#prerequisites).
3. The Agents Registry: [Deploying on Rancher](rancher.md).

No other registry is needed, and the Exchange is not involved: the Agents Registry shares nothing with partners.

## What happens on install

| Order | Job | Does |
| --- | --- | --- |
| Regular Job | the `iam-register` Job | Registers the staff portal's roles and permissions in IAM. A failure here does not fail the release |
| Hook, weight 10 | `<release>-db-seed` | Waits for the APIs and for AWE. Loads the registers, the Agent screens, search and intake form, the training activity types and indicators, and the reporting views. With **Load Sample Data**, also the country pack's sample agents, the sample Agent approval policies and the demo staff users they name |
| Hook, weight 20 | `<release>-activity-samples` | Only with **Load sample trainings**. Records the sample trainings and certifications. **Fails the release** if they cannot be loaded |
| Hook, weight 25 | `<release>-sanity` | The platform's smoke tests: the partner API is up |

Helm stops at the first failed hook, so a missing Job means an earlier one failed.

The seed is idempotent: on upgrade, the registers, screens, search, activity types and indicators are updated in place, and the reporting views recreated. On start, the APIs add any column a newer version declares to the existing tables.

{% hint style="warning" %}
db-seed waits for AWE. If AWE in commons-services is down, db-seed blocks, the install times out, and the later Jobs are never created. If you see no sanity Job, check db-seed and commons-services first.
{% endhint %}

## Next

* [Deploying on Rancher](rancher.md): prerequisites, choices, sample data, checks after install, uninstall
* [Customisation](../customisation.md): what a country changes

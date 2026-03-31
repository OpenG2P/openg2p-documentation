---
description: >-
  Roles, permissions, and role-permission mappings for the OpenG2P Registry
  module, managed via Keycloak under the 'staff' realm.
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# RBAC Roles and Permissions

## Overview

The OpenG2P Registry enforces role-based access control (RBAC) through **Keycloak**. All roles and permissions listed on this page are scoped to:

| Property   | Value                   |
| ---------- | ----------------------- |
| **Realm**  | `staff`                 |
| **Client** | `registry-staff-portal` |

Roles are organised into two classifications — **Operations** and **Configurations** — each serving a distinct functional area of the registry.

{% hint style="info" %}
The roles and permissions listed here are the defaults shipped with OpenG2P Registry. They can be customised during installation via the Registry Helm chart.
{% endhint %}

## Roles

### Operations roles

Operations roles govern day-to-day data management workflows such as intake, editing, verification, and integration monitoring.

| Role                     | Description                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| Intake Officer           | Handles initial data entry and submission of new records into the registry.                      |
| Intake Validator         | Validates and verifies the accuracy of newly submitted intake records before further processing. |
| Data Editor              | Edits and updates existing registry records as part of ongoing data maintenance.                 |
| Data Validator           | Reviews and verifies changes made to registry records to ensure correctness and compliance.      |
| Data Supervisor          | Approves verified registry changes, making them final and officially accepted.                   |
| Integration Manager      | Manages and monitors data exchange between the registry and external systems.                    |
| Operations Administrator | Has full operational control across the registry.                                                |

### Configuration roles

Configuration roles control how the registry itself is set up — schemas, integrations, and reference data.

| Role                      | Description                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| Schema Designer           | Configures core registry settings such as domain schemas, fields, and validation rules.                |
| Integration Specialist    | Sets up and manages configurations for integrations with external systems and APIs.                    |
| Reference Data Specialist | Maintains and updates reference/master data used across the registry.                                  |
| Technical Administrator   | Has full control over all configuration aspects, including registry, integrations, and reference data. |

## Permissions

Below is the complete set of fine-grained permissions available within the `openg2p-registry` client.

{% tabs %}
{% tab title="Intake & Verification" %}
| Permission                      | Description                   |
| ------------------------------- | ----------------------------- |
| `intakeForm:create`             | Create a new intake form      |
| `intakeForm:view`               | View intake forms             |
| `verificationIntakeForm:create` | Create an intake verification |
| `verificationIntakeForm:view`   | View intake verifications     |
{% endtab %}

{% tab title="Register & Change Requests" %}
| Permission                         | Description                          |
| ---------------------------------- | ------------------------------------ |
| `register:view`                    | View registry records                |
| `registerHistory:view`             | View registry record history         |
| `changeRequest:view`               | View change requests                 |
| `changeRequest:create`             | Create a change request              |
| `changeRequest:approve`            | Approve a change request             |
| `verificationChangeRequest:view`   | View change request verifications    |
| `verificationChangeRequest:create` | Create a change request verification |
{% endtab %}

{% tab title="Messages" %}
| Permission             | Description            |
| ---------------------- | ---------------------- |
| `incomingMessage:view` | View incoming messages |
| `outgoingMessage:view` | View outgoing messages |
{% endtab %}

{% tab title="Registry Configuration" %}
| Permission                   | Description                 |
| ---------------------------- | --------------------------- |
| `registryConfiguration:view` | View registry configuration |
| `registryConfiguration:edit` | Edit registry configuration |
| `registerDefinition:view`    | View register definitions   |
| `registerDefinition:create`  | Create register definitions |
| `registerDefinition:edit`    | Edit register definitions   |
| `registerDefinition:delete`  | Delete register definitions |
| `registerTab:view`           | View register tabs          |
| `registerTab:create`         | Create register tabs        |
| `registerTab:edit`           | Edit register tabs          |
| `registerTab:delete`         | Delete register tabs        |
| `registerSection:view`       | View register sections      |
| `registerSection:create`     | Create register sections    |
| `registerSection:edit`       | Edit register sections      |
| `registerSection:delete`     | Delete register sections    |
{% endtab %}

{% tab title="Integration" %}
| Permission                | Description               |
| ------------------------- | ------------------------- |
| `dataModel:view`          | View data models          |
| `dataModel:create`        | Create data models        |
| `dataModel:edit`          | Edit data models          |
| `dataModel:delete`        | Delete data models        |
| `ingestPartner:view`      | View ingest partners      |
| `ingestPartner:create`    | Create ingest partners    |
| `ingestPartner:edit`      | Edit ingest partners      |
| `ingestPartner:delete`    | Delete ingest partners    |
| `ingestKeyPath:view`      | View ingest key paths     |
| `ingestKeyPath:create`    | Create ingest key paths   |
| `ingestKeyPath:edit`      | Edit ingest key paths     |
| `ingestKeyPath:delete`    | Delete ingest key paths   |
| `ingestExpression:view`   | View ingest expressions   |
| `ingestExpression:create` | Create ingest expressions |
| `ingestExpression:edit`   | Edit ingest expressions   |
| `ingestExpression:delete` | Delete ingest expressions |
| `ingestTemplate:view`     | View ingest templates     |
| `ingestTemplate:create`   | Create ingest templates   |
| `ingestTemplate:edit`     | Edit ingest templates     |
| `ingestTemplate:delete`   | Delete ingest templates   |
| `ingestEnricher:view`     | View ingest enrichers     |
| `ingestEnricher:create`   | Create ingest enrichers   |
| `ingestEnricher:edit`     | Edit ingest enrichers     |
| `ingestEnricher:delete`   | Delete ingest enrichers   |
| `outgestTemplate:view`    | View outgest templates    |
| `outgestTemplate:create`  | Create outgest templates  |
| `outgestTemplate:edit`    | Edit outgest templates    |
| `outgestTemplate:delete`  | Delete outgest templates  |
| `outgestTopic:view`       | View outgest topics       |
| `outgestTopic:create`     | Create outgest topics     |
| `outgestTopic:edit`       | Edit outgest topics       |
| `outgestTopic:delete`     | Delete outgest topics     |
{% endtab %}

{% tab title="Reference Data" %}
| Permission             | Description           |
| ---------------------- | --------------------- |
| `referenceData:view`   | View reference data   |
| `referenceData:create` | Create reference data |
| `referenceData:edit`   | Edit reference data   |
| `referenceData:delete` | Delete reference data |
{% endtab %}
{% endtabs %}

## Role–permission mapping

### Operations roles

{% tabs %}
{% tab title="Intake Officer" %}
**Technical name:** `registry-ops-intake-officer`

| Permission          |
| ------------------- |
| `intakeForm:create` |
| `intakeForm:view`   |
{% endtab %}

{% tab title="Intake Validator" %}
**Technical name:** `registry-ops-intake-verifier`

| Permission                      |
| ------------------------------- |
| `intakeForm:view`               |
| `verificationIntakeForm:view`   |
| `verificationIntakeForm:create` |
{% endtab %}

{% tab title="Data Editor" %}
**Technical name:** `registry-ops-registry-editor`

| Permission             |
| ---------------------- |
| `register:view`        |
| `registerHistory:view` |
| `changeRequest:view`   |
| `changeRequest:create` |
{% endtab %}

{% tab title="Data Validator" %}
**Technical name:** `registry-ops-registry-verifier`

| Permission                         |
| ---------------------------------- |
| `register:view`                    |
| `registerHistory:view`             |
| `changeRequest:view`               |
| `verificationChangeRequest:view`   |
| `verificationChangeRequest:create` |
{% endtab %}

{% tab title="Data Supervisor" %}
**Technical name:** `registry-ops-registry-approver`

| Permission                       |
| -------------------------------- |
| `register:view`                  |
| `registerHistory:view`           |
| `changeRequest:view`             |
| `verificationChangeRequest:view` |
{% endtab %}

{% tab title="Integration Manager" %}
**Technical name:** `registry-ops-integration-manager`

| Permission             |
| ---------------------- |
| `incomingMessage:view` |
| `outgoingMessage:view` |
{% endtab %}

{% tab title="Ops Administrator" %}
**Technical name:** `registry-ops-super-operator`

| Permission                         |
| ---------------------------------- |
| `intakeForm:create`                |
| `intakeForm:view`                  |
| `verificationIntakeForm:view`      |
| `verificationIntakeForm:create`    |
| `register:view`                    |
| `registerHistory:view`             |
| `changeRequest:view`               |
| `changeRequest:create`             |
| `verificationChangeRequest:view`   |
| `verificationChangeRequest:create` |
| `incomingMessage:view`             |
| `outgoingMessage:view`             |
{% endtab %}
{% endtabs %}

### Configuration roles

{% tabs %}
{% tab title="Schema Designer" %}
**Technical name:** `registry-config-registry-configurator`

| Permission                   |
| ---------------------------- |
| `registryConfiguration:view` |
| `registryConfiguration:edit` |
| `registerDefinition:view`    |
| `registerDefinition:create`  |
| `registerDefinition:edit`    |
| `registerDefinition:delete`  |
| `registerTab:view`           |
| `registerTab:create`         |
| `registerTab:edit`           |
| `registerTab:delete`         |
| `registerSection:view`       |
| `registerSection:create`     |
| `registerSection:edit`       |
| `registerSection:delete`     |
{% endtab %}

{% tab title="Integration Specialist" %}
**Technical name:** `registry-config-integration-configurator`

| Permission                |
| ------------------------- |
| `dataModel:view`          |
| `dataModel:create`        |
| `dataModel:edit`          |
| `dataModel:delete`        |
| `ingestPartner:view`      |
| `ingestPartner:create`    |
| `ingestPartner:edit`      |
| `ingestPartner:delete`    |
| `ingestKeyPath:view`      |
| `ingestKeyPath:create`    |
| `ingestKeyPath:edit`      |
| `ingestKeyPath:delete`    |
| `ingestExpression:view`   |
| `ingestExpression:create` |
| `ingestExpression:edit`   |
| `ingestExpression:delete` |
| `ingestTemplate:view`     |
| `ingestTemplate:create`   |
| `ingestTemplate:edit`     |
| `ingestTemplate:delete`   |
| `ingestEnricher:view`     |
| `ingestEnricher:create`   |
| `ingestEnricher:edit`     |
| `ingestEnricher:delete`   |
| `outgestTemplate:view`    |
| `outgestTemplate:create`  |
| `outgestTemplate:edit`    |
| `outgestTemplate:delete`  |
| `outgestTopic:view`       |
| `outgestTopic:create`     |
| `outgestTopic:edit`       |
| `outgestTopic:delete`     |
{% endtab %}

{% tab title="Ref Data Specialist" %}
**Technical name:** `registry-config-reference-data-configurator`

| Permission             |
| ---------------------- |
| `referenceData:view`   |
| `referenceData:create` |
| `referenceData:edit`   |
| `referenceData:delete` |
{% endtab %}

{% tab title="Technical Administrator" %}
**Technical name:** `registry-config-super-configurator`

| Permission                   |
| ---------------------------- |
| `registryConfiguration:view` |
| `registryConfiguration:edit` |
| `registerDefinition:view`    |
| `registerDefinition:create`  |
| `registerDefinition:edit`    |
| `registerDefinition:delete`  |
| `registerTab:view`           |
| `registerTab:create`         |
| `registerTab:edit`           |
| `registerTab:delete`         |
| `registerSection:view`       |
| `registerSection:create`     |
| `registerSection:edit`       |
| `registerSection:delete`     |
| `dataModel:view`             |
| `dataModel:create`           |
| `dataModel:edit`             |
| `dataModel:delete`           |
| `ingestPartner:view`         |
| `ingestPartner:create`       |
| `ingestPartner:edit`         |
| `ingestPartner:delete`       |
| `ingestKeyPath:view`         |
| `ingestKeyPath:create`       |
| `ingestKeyPath:edit`         |
| `ingestKeyPath:delete`       |
| `ingestExpression:view`      |
| `ingestExpression:create`    |
| `ingestExpression:edit`      |
| `ingestExpression:delete`    |
| `ingestTemplate:view`        |
| `ingestTemplate:create`      |
| `ingestTemplate:edit`        |
| `ingestTemplate:delete`      |
| `ingestEnricher:view`        |
| `ingestEnricher:create`      |
| `ingestEnricher:edit`        |
| `ingestEnricher:delete`      |
| `outgestTemplate:view`       |
| `outgestTemplate:create`     |
| `outgestTemplate:edit`       |
| `outgestTemplate:delete`     |
| `outgestTopic:view`          |
| `outgestTopic:create`        |
| `outgestTopic:edit`          |
| `outgestTopic:delete`        |
| `referenceData:view`         |
| `referenceData:create`       |
| `referenceData:edit`         |
| `referenceData:delete`       |
{% endtab %}
{% endtabs %}

{% hint style="info" %}
The **Operations Administrator** role is a superset of all operations roles. Similarly, the **Technical Administrator** role is a superset of all configuration roles.
{% endhint %}

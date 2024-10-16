---
description: WORK IN PROGRESS
---

# Record Revision History

Any changes/updates to records in the Registry have to be captured by the system.  Admins must be able to see the information associated with a registry record on previous dates. Admins must also be able to generate reports of aggregate data for an earlier period.  For example, the total number of farmers with more than 10 acres of land as of Dec 2023.

{% hint style="info" %}
Revision History is not the same as [Audit Logs](logging/audit-log.md) or [System Log](../../monitoring-and-reporting/logging.md). &#x20;
{% endhint %}

## Functionality

* All the changes to records in the social registry are recorded along with datetime stamp of the change.
* The users who can view the revision history are registrars, administrators, system admins, etc.
* The revision history is searchable based on fields like Social Registry ID, etc.
* Ability to generate aggregated reports on one or more fields covering a time period.
* Privacy: The PII data and their changes are also logged into the revision history. Whether or not to capture PII fields, and their changes, is left to system administrators.

## Design

* The current design involves [Reporting Framework](../../monitoring-and-reporting/reporting-framework/). Social Registry deployment is packaged with Reporting Framework installation, which is configured to capture all the changes to the registry records and send them to OpenSearch.
* All changes to records get captured as separate documents under the OpenSearch Index including the timestamp of change.
* This makes it easy to query for records or data at a particular point in time, while the main Social Registry continues to maintain the latest data.
* Dashboards and Reports can be generated easily on OpenSearch Dashboards. A reference dashboard for revision history is available (TODO).
* By default, all the fields and their changes are captured, but the [reporting framework configuration](../../monitoring-and-reporting/reporting-framework/) allows not to capture PII data.
* Social Registry can generate a unique Registry ID for each record. That registry ID can be used to query for changes related to a particular record.
* If you are using a customized social registry that involves multiple tables that store additional data, and are _related_ to the main _res\_partner_ table (via foreign key), then you are required to create separate OpenSearch connectors for all these tables.
  * In the connector configuration of these adjunct tables, use the [DynamicNewField](../../monitoring-and-reporting/reporting-framework/user-guides/connector-creation-guide.md) SMT to add the above-mentioned Registry ID field to these adjunct tables, so that changes to these adjunct tables can also be queried using the same registry ID.
* When a record is deleted from the Social Registry DB, there will be no change in revision history on OpenSearch.
* Refer to [Reporting guides](../../monitoring-and-reporting/reporting-framework/#creating-dashboards) for further configuration.

## User stories

* Update a record in the Social Registry via any [update mechanism](registry-update-mechanisms.md), say through the UI (odoo-based), or the APIs, etc.
* Check that the changes are reflected on OpenSearch with appropriate timestamp (TODO: elaborate.)

## Other Approaches

* OCA offers a module called [Audit Log](https://github.com/OCA/server-tools/blob/17.0/auditlog) (AGPL-3 License).
  * This allows capturing changes to any Odoo table based on configured rules.
  * It provides an Odoo native UI to view all the changes and allows for access control on what kind of user can view the changes.
  * It also allows for capturing the User who performed the changes.
  * However, all changes to all the tables are recorded in a single audit log table. Furthermore changes to each field of the table are logged as separate rows, called audit log lines.
  * This also makes it very difficult to query the changes or look at a version of a record at a particular point in time.
  * Very difficult to generate reports.
  * Changes are only captured when updates are made through Odoo, but not captured when there are direct DB changes.
* Smile-SA offers a module called [Audit Trail](https://github.com/Smile-SA/odoo\_addons/tree/16.0/smile\_audit) (LGPL-3 License).
  * This allows capturing changes to any Odoo table based on configured rules.
  * All changes to a particular record can viewed on Odoo by opening the "Revision History" under the record.
  * It also allows for capturing the User who performed the changes.
  * However, similar to OCA, all changes to all the tables are recorded in a single audit log table. But record data before the change and data after the change are captured (as Python dictonaries) against each change.
  * Difficult to query the changes or look at a version of a record at a particular point in time. Very difficult to generate reports.


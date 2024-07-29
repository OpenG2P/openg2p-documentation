---
description: WORK IN PROGRESS
---

# Record Change History

Changes to specific fields by admin/operators/end-users must be logged in the system for query and auditing.  Admins must see the information associated with a registrant for previous dates.  Admins must also be able to generate reports of aggregate data for an earlier period.  For example, the total number of farmers with more than 10 acres of land as of Dec 2023.

{% hint style="info" %}
Change log is not the same as [Audit Logs](../../features/audit-log.md) or [System Log](../../../monitoring-and-reporting/logging.md). &#x20;
{% endhint %}

## Functionality

* All the changes to records in the social registry are recorded along with datetime stamp of the change, nature of change, and author of the change. A record is defined as a row in `res.partner` table.
* The changes are viewable via a user interface of Odoo. &#x20;
* The viewers of this data are registrars, program admins, agents, and counsellors.
* The changes are searchable based on fields like Reference ID, name etc.
* Ability to generate aggregated reports on one or more fields covering a time period.
* Access control mechanism for authorized users to access this data.
* The change log table is not editable under any circumstances.
* Privacy:  The change log contains all the information of the registry and hence needs to be given very limited access along with data security similar to the registry primary data. See [Privacy and Security](../../functionality/privacy-and-security.md).
* This data is accessible via standard registry query [APIs](../../features/api/).
* What if the record gets deleted (TBD).

## Available solutions

OCA offers a module called "Audit Log" that does some similar but is licensed as AGPL. Further, it does not provide all the desired features.

## User stories

### Update

1. A user edits a record via the available [update mechanisms](../../features/registry-update-mechanisms.md) of the Social Registry. The change is automatically stored in the backend silently without any special indication to the user more than the usual update flow.

### View

1. Against each record, there is a button, say, _History_ to view the history of changes to this record.
2. User clicks on _History._ User sees a table of all changes related to the record, paginated, default order by descending timestamp. &#x20;
3. User can change the sort using the `Sort by` button
4. If the data list is large user can search through records (TBD)
5.

## Design

### Database

A separate history table in the database is

### Reports

* Reporting framework is leveraged for generating reports on the change logs.

### User interface

## Test design

## Source code

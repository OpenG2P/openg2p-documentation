---
description: Logging in PBMS
---

# Logging

## Introduction

In OpenG2P logging is performed at various levels:

* **System logs** for monitoring and debugging
* **Audit logs** for business process auditing
* **Change logs** for recording changes to data

## System logs

Each module outputs system logs for different levels:

* INFO, ERROR, DEBUG, WARNING

Logs from all modules are channelized and indexed for viewing on dashboards and triggering alerts.  Refer to [Logging](../../monitoring-and-reporting/logging.md) for further details.

## Audit logs

For Odoo modules  [Odoo's Audit Log](https://github.com/OCA/server-tools/tree/16.0/auditlog) package is used.

For FastAPI modules, audit logs are implemented using [MOSIP's Auditmanager Service](https://github.com/mosip/audit-manager/tree/release-1.2.0).

## Change logs

For PBMS, change logs are implemented using [Odoo's Audit Log](https://github.com/OCA/server-tools/tree/16.0/auditlog) package. Rules are added against the models to record field level changes.

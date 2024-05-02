---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Registry Update Mechanisms

Social Registry (SR) may be updated in several ways:

* [**APIs**](api/)**:** SR can be updated using APIs. This allows for automated updates and real-time syncing of data between systems.
* **Login-based direct data entry**: Authorized users can log in to the Social Registry system and manually enter or update information. This method provides direct control over the data and allows for immediate updates.
* **Service provider portal** for updates by agents/operators/enumerators.
* [ODK ](../../utilities-and-tools/odk-collection-app.md)(Android, agent, offline): ODK  is a set of tools that allows for data collection using mobile devices. Users can collect data offline using ODK Collect and then upload it to the Social Registry system when a connection is available.
* **CSV**: Users can update the Social Registry by uploading a CSV (Comma-Separated Values) file containing the updated information. This method is useful for bulk updates or when users have the data in a spreadsheet format. _(Currently supporting using scripts that call APIs)_

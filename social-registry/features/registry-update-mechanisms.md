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
* **Service provider portal:** Where service providers like institutions or entity that provides services to registrant beneficiary can login to the portal. They can manually add and update the registrant details on the portal.
* [ODK ](../../utilities-and-tools/odk-collection-app.md)(Android, agent, offline): ODK  is a set of tools that allows for data collection using mobile devices. Enumerator or field agents can collect data offline using ODK Collect and then upload it to the Social Registry system when a network connection is available.
* **CSV**: Users can update the Social Registry by uploading a CSV (Comma-Separated Values) file containing the updated information. This method is useful for bulk updates or when users have the data in a spreadsheet format. _(Currently supporting using scripts that call APIs)_

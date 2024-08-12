---
description: Work in Progress
---

# Enumerator ID

Why enumerator ID?&#x20;

Enumerator and Data Collector are the same person&#x20;

Enumerator ID will be generated when an enumerator is onboarded - in the social registry&#x20;

ODK app user ID is set against the enumerator ID - enumerator logging into reg portal should be able to access the records made by him in the ODK - we list app users in the reg portal user creation&#x20;

Questions&#x20;

* What is the sequence of the ID? Random? Prefix? Uniqueness
  * Use sequencer on Odoo to generate IDs - 5 digits. Prefix should be configurable.  For eg. EID-00001
* Where will the ID be shown? In the user profile on registration portal, we can show the enumerator ID + will be created and stored in the registry, service provider management on registry, Has to appear in the enumerator details section of each record  &#x20;
* When will the ID be generated? When the data collector is added in the registry -> service provider. It will be auto generated after you click on 'save data collector'&#x20;
* Can enumerator log in with his ID to the registration portal? Can be enabled  - Phase 2&#x20;
* Can ID be deleted or deactivated - deactivate users in the admin portal itself&#x20;
* Read only field everywhere&#x20;
* Who can create enumerator? Data Admin and System Admin&#x20;
* Data admin can search registry by enumerator ID - Phase 2




# Create a Custom Group

## Description

This guide provides step-by-step instruction to create a custom group and add the users to this group. Users get the group's access rights and permissions, those who are included in this group.

## Pre-requisites

A user must have an Administrator role.&#x20;

## Procedure

1. In the menu bar, click the icon ![](../../.gitbook/assets/image.png) and select _**Settings**_.
2. The _**Settings**_ screen is displayed
3. In the left menu bar, click the _**General Settings**_
4. Scroll down to the _**Developer Tools**_ section, click the link _**Activate the developer mode**_

<figure><img src="../../.gitbook/assets/settings-odoo role.PNG" alt=""><figcaption><p>Choose Settings Screen</p></figcaption></figure>

<figure><img src="../../.gitbook/assets/settings-develpoer mode.png" alt=""><figcaption><p>Settings Screen</p></figcaption></figure>

5. The developer mode is activated
6. In the _**Settings**_ screen, click _**User & Companies**_ and click the option _**Groups**_
7. The _**Groups**_ screen is displayed. Click the _**Create**_ button.

<figure><img src="../../.gitbook/assets/odoo-groups (1).png" alt=""><figcaption><p>User &#x26; Companies - Users</p></figcaption></figure>

<figure><img src="../../.gitbook/assets/odoo-create.PNG" alt=""><figcaption><p>Groups - screen</p></figcaption></figure>

8. The _**Groups/New**_ screen is displayed.

<figure><img src="../../.gitbook/assets/group-application.PNG" alt=""><figcaption></figcaption></figure>

In _**Groups/New**_ screen, the available features and their descriptions are:

<table><thead><tr><th width="245">Feature</th><th>Description</th></tr></thead><tbody><tr><td>Application</td><td><p>Select the appropriate option in the drop-down. </p><p>For example, here <em><strong>OpenG2P Module Access</strong></em> is selected in the drop-down</p></td></tr><tr><td>Name </td><td><p>Enter the role of the user </p><p>For example, the role of the user is entered as <em><strong>Administrator</strong></em></p></td></tr><tr><td>Share Group</td><td><p>Check the Share Group option. </p><p>Note: Check this option if you want to allow users of this group to grant additional access to other users who might not be in the original group.</p></td></tr></tbody></table>

9. Click the _**Users**_ tab.&#x20;

<figure><img src="../../.gitbook/assets/group-share-group.PNG" alt=""><figcaption></figcaption></figure>

In _**Users tab**_, the available features and their descriptions are:

| Feature | Description |
| ------- | ----------- |
| Name    |             |
|         |             |
|         |             |

7. To add users to this group, click on _Add a Line._ A pop-up window appears to allow the selection of the users from a list. You can view and manage the users assigned to the group.

<div>

<figure><img src="../../.gitbook/assets/create-group-users (2).png" alt=""><figcaption></figcaption></figure>

 

<figure><img src="../../.gitbook/assets/odoo-user (1).png" alt=""><figcaption></figcaption></figure>

</div>

8. Select _OpenG2P ModuleAccess / Administrator_ as _Group Name_ in the _Inherited_ tab and click on _Add a Line._ A pop-up window shows a list of groups to select from. This group will get the access rights of the _OpenG2P ModuleAccess / Administrator_ group, and the users added to this group will be automatically added to the _OpenG2P ModuleAccess / Administrator_ group.

<div>

<figure><img src="../../.gitbook/assets/group-inherited.PNG" alt=""><figcaption></figcaption></figure>

 

<figure><img src="../../.gitbook/assets/inherits (1).png" alt=""><figcaption></figcaption></figure>

</div>

9. Select the _Menus_ tab and click on _Add a Line_. A pop-up window shows a list of menus to select from. These menu options provide access to multiple modules and their functionality.

<div>

<figure><img src="../../.gitbook/assets/odoo-menu-addline.png" alt=""><figcaption></figcaption></figure>

 

<figure><img src="../../.gitbook/assets/odoo-menu.PNG" alt=""><figcaption></figcaption></figure>

</div>

10. Select the _Views_ tab and click on _Add a Line_. A pop-up window shows the list of views to select from. A view represents various screens and forms used in the user interface.

<div>

<figure><img src="../../.gitbook/assets/odoo-view-addline.png" alt=""><figcaption></figcaption></figure>

 

<figure><img src="../../.gitbook/assets/odoo-views.PNG" alt=""><figcaption></figcaption></figure>

</div>

11. Select the _Access Rights_ tab and click on _Add a Line._ Enter the name, and select the model from the drop-down. Tick one or more checkboxes for the relevant access options - _None_, _Read Access_, _Write Access_, _Create Access_, and _Delete Access_.

<figure><img src="../../.gitbook/assets/Create-group-access-rights.PNG" alt=""><figcaption></figcaption></figure>

12. Select the _Record Rules_ tab. This tab allows you to set up certain rules and access rights that can be configured within specific modules.
13. Optionally select the _Notes_ tab to add any additional notes or remarks about the setup or group's configuration.
14. Click on _Save._ A new group gets created.

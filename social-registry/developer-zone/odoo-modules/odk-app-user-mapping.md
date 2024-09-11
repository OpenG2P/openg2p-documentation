---
description: WORK IN  PROGRESS
---

# ODK App User Mapping

### **Module name**

`g2p_odk_user_mapping`

### **Module title**

ODK App User Mapping

### **Technology base**

Odoo

### **Functionality**

#### **Add drop-downs for ODK Config and App User**

* **Select ODK Config**
  * In the _**Registration Portal**_, implement a drop-down menu to allow the users select from the available ODK Configurations.
  * Dynamically fetches and displays ODK Configuration options based on the user's selection.
* **Select App User**
  * Implement a drop-down menu to list ODK App users.
  * Use the ODK API to fetch the list of App users based on the selected ODK Configuration.
  * Display the fetched App users in the drop-down menu.
* **Fetch ODK App Users via ODK API**
  * Integrate with the ODK API to retrieve the list of available App users for the selected ODK Configuration.
  * Use the fetched data to dynamically populate the _**Select App User**_ drop-down menu.

### **Design notes**

N/A

### **Relationships with other entities**

* **Dependencies**
  * `base`
  * `account`
  * `g2p_odk_importer`

### **User interface**

N/A

### **Configuration**

1. **ODK Config**
   * Navigate to the ODK menu in the _**Social Registry**_ module.
   * Add your ODK user credentials and project details.
2. **Map the ODK User in the Registration Portal**
   * Navigate to the Registration Portal user menu.
   * Add user details such as email, name, etc.
   * Select the ODK Configuration and then choose a dynamic user based on the selected ODK Configuration.

### **Source code**

[GitHub Repository for `g2p_odk_user_mapping`](https://github.com/OpenG2P/openg2p-registration-portal/blob/17.0-develop/g2p\_odk\_user\_mapping)

### **Installation**

1. Ensure that the module dependencies such as `base`, `account`, `g2p_odk_importer`are installed.
2. Install the _**ODK App User Mapping**_ module from the Odoo Apps interface.

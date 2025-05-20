---
description: This module enhances the security of the OpenG2P application.
---

# G2P Registry: Security

### Module name

`g2p_security`

### Module title

G2P Registry: Security

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

* **Session Timeout Management**
  * Automatically logs out inactive users by monitoring session file timestamps.
  * Ends sessions that exceed the configured timeout.
  * Updates timestamps on active HTTP requests.
* **Debug Mode Restriction**
  * Restricts access to Debug Mode for users by "Restrict Debug Mode" group.
* **Database Parameter Removal from Signup URLs**
  * Removes the `db` parameter from generated signup URLs for enhanced security.



**Dependencies**

Module dependencies

* base
* auth\_signup

### Configuration

**• Session Timeout**

* **Parameter Key**: `inactive_session_timeout_seconds`
* **Default Value**: `7200` seconds (2 hours)
* **Configuration Methods**:
  * **Odoo UI**:\
    Navigate to **Settings → Technical → Parameters → System Parameters** and set the key.
  *   **Programmatically**:\
      Use the following code to set the timeout value:

      ```python
      self.env['ir.config_parameter'].set_param('inactive_session_timeout_seconds', '3600')
      ```
* When the parameter is updated, the module **clears the ORM cache** to apply the new value immediately across all sessions.

***

**• Hide DB in URLs (Optional)**

* **Parameter Key**: `g2p_security.hide_db_param`
* **Set to**: `"True"` to remove the `db` parameter from generated signup URLs
* **Default**: `"True"`

### Source code

[https://github.com/OpenG2P/openg2p-registry](https://github.com/OpenG2P/openg2p-registry/tree/17.0-1.5/g2p_security)

### Installation

* Install the "G2P Registry: Security" module from the Odoo Apps interface.

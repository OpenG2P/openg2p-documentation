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

**Functionality**

**Session Timeout Management**

* **Automatic User Logout**: Monitors user session activity and automatically logs out inactive users
* **Configurable Timeout**: Session timeout duration can be configured via system parameters
* **Activity Tracking**: Updates session timestamps on active HTTP requests to track user activity
* **Session Expiration Check**: Compares last activity time with current time to determine if session has expired
* **Graceful Logout**: Properly terminates expired sessions while preserving database connection

**Session Timeout Control**

* **Enable/Disable Feature**: Session timeout can be activated or deactivated via configuration
* **Real-time Configuration**: Changes to session timeout settings immediately clear cache for instant application

**Debug Mode Restriction**

* Restricts access to Debug Mode for users by "Restrict Debug Mode" group

**Database Parameter Removal from Signup URLs**

* Removes the `db` parameter from generated signup URLs for enhanced security

**Dependencies**

**Module dependencies**

* base
* auth\_signup

**Configuration**

**Session Timeout Parameters**

**Timeout Duration**

* **Parameter Key**: `inactive_session_timeout_seconds`
* **Default Value**: `7200` seconds (2 hours)
* **Description**: Sets the duration of inactivity before a session expires

**Timeout Activation**

* **Parameter Key**: `inactive_session_timeout_active`
* **Default Value**: `False`
* **Description**: Enables or disables the session timeout feature
* **Values**:
  * `"True"` - Session timeout is active
  * `"False"` - Session timeout is disabled

**Hide DB in URLs (Optional)**

* **Parameter Key**: `g2p_security.hide_db_param`
* **Set to**: `"True"` to remove the `db` parameter from generated signup URLs
* **Default**: `"True"`

**Source code** [https://github.com/OpenG2P/openg2p-registry/tree/17.0-develop/g2p\_security](https://github.com/OpenG2P/openg2p-registry/tree/17.0-develop/g2p_security)

**Installation**

* Install the "G2P Registry: Security" module from the Odoo Apps interface.


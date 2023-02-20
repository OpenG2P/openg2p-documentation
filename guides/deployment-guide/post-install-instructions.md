---
description: Work in progress
---

# Post Install Instructions

## Post-install setup

* Once Odoo server is up, login as admin. And enter `debug mode` on odoo.
* Go to _Settings_ -> _Technical_ -> _System Parameters_.
  * Confiugre `web.base.url` to your required base url.
  * Create another system parameter, with name `web.base.url.freeze`, and value `True`.
  * Create another system parameter, with name `auth_oauth.authorization_header`, and value `True`.
* Go to Apps sections on UI, click on _Update Apps List_ action on top.
* Search through and install required G2P Apps & Modules.
* After all apps are installed, proceed to create users and assigning roles.
* Do not use `admin` user after this step. Log back in as regular user.
* Configure `ID Types` on `Registry` -> `Configuration`.
* WIP.

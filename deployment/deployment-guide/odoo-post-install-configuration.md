# Odoo Post Install Configuration

* Once the Odoo server is up, log in as admin. And enter `debug mode` on odoo.
* Go to _Settings_ -> _Technical_ -> _System Parameters_.
  * Configure `web.base.url` to your required base URL.
  * Create another system parameter, with the name `web.base.url.freeze`, and value `True`.
  * Create another system parameter, with the name `auth_oauth.authorization_header`, and value `True`.
* Go to the _Apps_ sections on UI, and click on the _Update Apps List_ action on top.
* Search through and install required G2P Apps & Modules.
* After all, apps are installed, proceed to create users and assign roles.
* Do not use the `admin` user after this step. Log back in as a regular user.
* Configure `ID Types` on `Registry` -> `Configuration`.
* WIP.

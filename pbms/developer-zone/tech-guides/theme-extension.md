# Theme Extension

PBMS ships an Odoo module, **`pbms_theme_extension`**, that carries the branding of the
Odoo back-office and login experience: the login page, the favicon and logo, fonts, and
company/user-level tweaks. For a country deployment you typically fork or extend this module
to apply your own branding.

This is step 5 of the [Country Implementation Guide](./country-implementation-guide.md) and
is independent of the registry work — you can do it at any time.

The module lives at `odoo/extensions/pbms_theme_extension/`.

## What the module contains

```
pbms_theme_extension/
├── __manifest__.py
├── controllers/
│   └── web_login.py          # customises the login controller / error messages
├── models/
│   ├── res_company.py         # favicon override on res.company
│   └── res_user.py            # res.users login / reset-password overrides
├── templates/
│   ├── g2p_login_page.xml      # login page (inherits web.login / auth_signup.login)
│   └── g2p_reset_password.xml  # reset-password page
├── views/
│   └── webclient_templates.xml # favicon <link> in the web layout <head>
└── static/
    └── src/
        ├── css/
        │   ├── style.css
        │   └── fonts/          # Roboto-*.woff
        ├── img/               # favicon-*.png, openg2p-*.png, logos
        ├── js/
        │   └── g2p_window_title.js  # browser tab title
        └── scss/
            ├── new_login_page.scss
            ├── g2p_login_page.scss
            └── assets_menu.scss
```

## The manifest

`__manifest__.py` declares the templates, views and asset bundles. This is the file you
edit when you add a template or a static asset:

```python
{
    "name": "PBMS Theme",
    "category": "G2P",
    "version": "3.1.1",
    "depends": ["base", "web", "auth_signup", "website"],
    "data": [
        "templates/g2p_login_page.xml",
        "templates/g2p_reset_password.xml",
        "views/webclient_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pbms_theme_extension/static/src/js/g2p_window_title.js",
            "pbms_theme_extension/static/src/css/style.css",
        ],
        "web.assets_frontend": [
            "pbms_theme_extension/static/src/scss/new_login_page.scss",
        ],
    },
    "application": True,
    "installable": True,
}
```

Note the split: back-office styling and the window-title JS go in `web.assets_backend`; the
login page (a public/frontend page) is styled from `web.assets_frontend`.

## Login page templates

`templates/g2p_login_page.xml` inherits Odoo's stock login templates and rewrites them.
Concretely it:

- Inherits `web.login` (template `id="login"`) and `auth_signup.login` and overrides them at
  `priority="99"` so PBMS wins over the base theme.
- Uses `xpath` to change the login form: replaces the `login` field label with
  `Email / Username`, strips placeholders, hides the default header/footer
  (`no_header` / `no_footer`), and injects the company logo via
  `/web/binary/company_logo`.

To rebrand the login page, edit the `xpath` overrides here (labels, layout) and swap the
image/logo references. Styling lives in `static/src/scss/new_login_page.scss`.

`templates/g2p_reset_password.xml` does the equivalent for the password-reset page.

### Login controller and messages

`controllers/web_login.py` extends Odoo's `Home` controller to reword the login error, e.g.
turning `Wrong login/password` into `Login failed due to Invalid credentials !`. Edit this
to change login-flow behaviour or messages.

`models/res_user.py` overrides `res.users` — it customises the reset-password lookup (by
login or email) and the `_login` hook. This is where self-service / registrant access rules
to the back-office are enforced.

## Favicon and logo

Favicon and logo assets live in `static/src/img/` (e.g. `favicon.png`,
`favicon-white-background.png`, `favicon-black-background.png`, `openg2p-black.png`,
`openg2p-white.png`). Two mechanisms serve them:

1. **Web layout head** — `views/webclient_templates.xml` replaces the `<link rel="shortcut
   icon">` in `web.layout`'s `<head>`, defaulting to
   `/pbms_theme_extension/static/src/img/favicon-white-background.png`:

   ```xml
   <template id="custom_web_layout" inherit_id="web.layout" priority="99">
       <xpath expr="//head/link[@rel='shortcut icon']" position="replace">
           <link type="image/x-icon" rel="shortcut icon"
                 t-att-href="x_icon or '/pbms_theme_extension/static/src/img/favicon-white-background.png'" />
       </xpath>
   </template>
   ```

2. **Company favicon** — `models/res_company.py` overrides `res.company` with
   `get_g2p_favicon()`, which reads the PNG from the module's `static/src/img/` via
   `get_resource_path` and returns it base64-encoded:

   ```python
   class ResCompany(models.Model):
       _inherit = "res.company"

       def get_g2p_favicon(self, img_path_module="", img_path_rel=""):
           img_path = get_resource_path(
               img_path_module or "pbms_theme_extension",
               img_path_rel or "static/src/img/favicon-white-background.png",
           )
           with tools.file_open(img_path, "rb") as f:
               return base64.b64encode(f.read())
   ```

To rebrand: replace the PNG files in `static/src/img/` (keep the same file names, or update
every reference), and update the login-template logo `src`.

## Fonts

The Roboto font family is bundled as `.woff` files under `static/src/css/fonts/` and pulled
in from `static/src/css/style.css`. To change the typeface, drop your font files into that
folder and update the `@font-face` / `font-family` declarations in `style.css` (and the
login SCSS). Keeping fonts bundled in the module (rather than loading from a CDN) keeps the
back-office self-contained for air-gapped installs.

## Window title

`static/src/js/g2p_window_title.js` sets the browser tab title. Edit it to change the
displayed product/organisation name.

## Forking for a country

For a country-specific theme you have two options:

- **Edit in place** — change the assets and templates inside `pbms_theme_extension`
  directly. Simplest; your changes are baked into the Odoo image (see below).
- **Fork as a new module** — copy `pbms_theme_extension` to
  `odoo/extensions/<country>_theme_extension`, change the `name` in `__manifest__.py`, and
  adjust template `id`s / asset paths to the new module name. Install it instead of (or
  after) the base theme. A separate module keeps your branding cleanly divorced from the
  upstream module and easier to carry across upgrades.

Either way, keep the module inside `odoo/extensions/` so the packaging step picks it up.

## Packaging into the Odoo image

The Odoo Dockerfile (`docker/openg2p-pbms-odoo/utils/Dockerfile`) copies the **entire**
extensions directory into the Odoo addons path:

```dockerfile
COPY odoo/extensions ${EXTRA_ADDONS_DIR}/pbms-extensions
```

Each immediate sub-directory of `EXTRA_ADDONS_DIR` becomes an `addons_path` entry (handled
by `docker/openg2p-pbms-odoo/utils/docker-entrypoint.d/00-gather-addons.sh`). So any changes
to `pbms_theme_extension` — or a new `<country>_theme_extension` module placed alongside it —
are included automatically when you rebuild the Odoo image (step 6 of the
[Country Implementation Guide](./country-implementation-guide.md)). After rebuilding, make
sure the module is installed/upgraded in the target database and, if you forked it, that it
is in the list of modules to install.

# Example Implementation Workflow

Before starting the implementation of the custom registry add-ons, we need to ensure the design and implementation of custom registry views within the registry database based on some set standards. These views will serve as the communication interface with PBMS -  enabling rule configuration, reference lookups during calculations, and other integrations. This design will ensure that both PBMS and Background Task modules have standardized and consistent access to the necessary registry attributes, forming a unified knowledge base for PBMS functions across the registry.

Once the registry views are defined in the registry database, we can use that design as models within the `g2p_registry_addons` module.

{% hint style="warning" %}
It is important that these models be defined as custom views in the registry database so that PBMS can use them for lookups, query and other purposes. Since they are custom views, they do not expose the underlying model name(s) from the registry database.
{% endhint %}

Hereafter, we'll go over the implementation of `farmer` and `student` registries in [odoo-extensions](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/tree/3.0).

## Defining Registry Models (`/models`)

For each of the registry models, create a python file in the `/models` folder of `g2p_registry_addon` module. These models will inherit from `g2p.registry` present in `/models/registry.py`

<pre class="language-python"><code class="lang-python"># g2p_registry_addon/models/farmer_registry.py
class G2PFarmerRegistry(models.Model):
    _name = "g2p.farmer.registry"
    _description = "Farmer Registry"
<strong>    _inherit = "g2p.registry"
</strong>    
    ## ... add fields as designed in the registry views ...
</code></pre>

Once all the models are created, update the `g2p_registry_type_addon/models` with the newly created models.  It is recommended to update the security file`/security/ir.model.access.csv` with your new models.

<pre class="language-python"><code class="lang-python"># g2p_registry_type_addon/models/registry.py
class G2PTargetModelMapping:
    """Static mapping from registry type key to model name."""

<strong>    MODEL_MAPPING = {
</strong><strong>        "student": "g2p.student.registry",
</strong><strong>        "farmer": "g2p.farmer.registry",
</strong><strong>    }
</strong>
    @classmethod
    def get_target_model_name(cls, key):
        """Get the model name for a given key."""
        return cls.MODEL_MAPPING.get(key)

class G2PRegistryType(Enum):
<strong>    FARMER = "farmer"
</strong><strong>    STUDENT = "student"
</strong><strong>    OTHER = "other"
</strong>
    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields."""
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
</code></pre>

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
g2p_student_registry_read,Read Student Registry,model_g2p_student_registry,g2p_pbms.group_beneficiary_list_viewer,1,0,0,0
g2p_student_registry_write,Write Student Registry,model_g2p_student_registry,g2p_pbms.group_beneficiary_list_editor,1,1,1,1

g2p_farmer_registry_read,Read Farmer Registry,model_g2p_farmer_registry,g2p_pbms.group_beneficiary_list_viewer,1,0,0,0
g2p_farmer_registry_write,Write Farmer Registry,model_g2p_farmer_registry,g2p_pbms.group_beneficiary_list_editor,1,1,1,1
```

## Defining Views (`/views`)

Now, we can go ahead and define custom views by inheriting views from `g2p_pbms`. Ideally we use this section for adding registry specific view in PBMS Odoo UI, but in your custom implementation you can add new views inherit views outside of those shown here all within the scope if what's allowed in odoo.

Although these views should be present for an ideal installation as an add-on to PBMS Core Odoo:

### `/registry` and `/menu.xml`

In these views we define the menu ribbon view (including both tree and form) for the new registries defined.

<figure><img src="../../../../.gitbook/assets/image (1) (3).png" alt=""><figcaption></figcaption></figure>

*   Create a window action (`ir.actions.act_window`) referencing your model.

    ```xml
    <!--- /registry/farmer_registry_view.xml --->
    <record id="action_g2p_farmer_registry" model="ir.actions.act_window">
        <field name="name">Farmer Registry</field>
        <field name="res_model">g2p.farmer.registry</field>
        <field name="view_mode">tree,form</field>
    </record>
    ```
*   Define the tree and form view for your model, listing the fields you want users to see for each record. Recommended to use `create="0"` tag prop since the data in these models do not reflect actual registry data.

    ```xml
    <record id="view_g2p_farmer_registry_form" model="ir.ui.view">
        <field name="name">g2p.farmer.registry.form</field>
        <field name="model">g2p.farmer.registry</field>
        <field name="arch" type="xml">
            <form string="G2P Farmer Registry" create="0">
                <sheet>
                    <group>
                        <field name="field_1"/>
                        ...
                        <field name="field_n"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    <record id="view_g2p_farmer_registry_tree" model="ir.ui.view">
        <field name="name">g2p.farmer.registry.tree</field>
        <field name="model">g2p.farmer.registry</field>
        <field name="arch" type="xml">
            <tree string="G2P Farmer Registry" create="0">
                <field name="field_1"/>
                ...
                <field name="field_n"/>
            </tree>
        </field>
    </record>

    ```
*   Ensure you link the action (here `action_g2p_farmer_registry`) into a menu item with the correct parent so users can access it. This can be done via inheriting the PBMS menu as shown in `/menu.xml`

    <pre class="language-xml"><code class="lang-xml">&#x3C;!--- /menu.xml --->
    &#x3C;odoo>
        &#x3C;menuitem id="menu_g2p_farmer_registry"
                  name="Farmer Registry"
    <strong>              parent="g2p_pbms.menu_g2p_registry"
    </strong><strong>              action="action_g2p_farmer_registry"
    </strong>              sequence="1"/>
        &#x3C;menuitem id="menu_g2p_student_registry"
                  name="Student Registry"
    <strong>              parent="g2p_pbms.menu_g2p_registry"
    </strong><strong>              action="action_g2p_student_registry"
    </strong>              sequence="2"/>
    &#x3C;/odoo>
    </code></pre>

### `/eligibility`, `/entitlement` and `/priority`

These views will add model based UI enhancements which is required for effective use of PBMS operations, mainly rule based view.

Referring the existing inheritance implementation update the model based information within the `<xpath>` block. You are free to add or remove the domain widget blocks based on the number of models.&#x20;

<pre class="language-xml"><code class="lang-xml">&#x3C;!-- /eligibility/eligibility_rule_view.xml -->
&#x3C;!-- Inject domain widgets inside the &#x3C;group> -->
&#x3C;xpath expr="//form/sheet/group" position="inside">

    &#x3C;!-- Domain widget for the 'farmer' type -->
<strong>    &#x3C;field name="pbms_domain" widget="domain"
</strong><strong>            options="{'model': 'g2p.farmer.registry'}"
</strong><strong>            invisible="target_registry != 'farmer'"/>
</strong>
    &#x3C;!-- Domain widget for the 'student' type -->
    &#x3C;field name="pbms_domain" widget="domain"
            options="{'model': 'g2p.student.registry'}"
            invisible="target_registry != 'student'"/>

&#x3C;/xpath>
</code></pre>

{% hint style="info" %}
The views are already set to inherit from the PBMS views and it's recommended to use the same view or follow the same convention while creating new inheritance views into PBMS

```xml
<odoo>
    <record id="view_g2p_eligibility_rule_definition_form_inherit" model="ir.ui.view">
        <field name="name">g2p.eligibility.rule.definition.form.inherit</field>
        <field name="model">g2p.eligibility.rule.definition</field>
        <field name="inherit_id" ref="g2p_pbms.view_g2p_eligibility_rule_definition_form"/>
        <field name="arch" type="xml">
        ...
    </record>
</odoo>
```
{% endhint %}

### `/bgtask`

This view defines the **Search Beneficiaries** section in PBMS UI and is paired with a custom-defined widget (in the `/static` folder) which integrates JavaScript to manage the search functionality.

<figure><img src="../../../../.gitbook/assets/image (82).png" alt=""><figcaption></figcaption></figure>

Update your model info within the `<xpath>` groups. Use the correct `target_registry` and `model` as defined earlier.

<pre class="language-xml"><code class="lang-xml">&#x3C;xpath expr="//page[.//field[@name='target_registry']]/group" position="after">
  &#x3C;!-- Only one beneficiary_search field is shown based on registry type -->
<strong>  &#x3C;group name="beneficiary_search_farmer" invisible="target_registry != 'farmer'">
</strong><strong>    &#x3C;widget name="g2p_beneficiaries_widget" model="g2p.farmer.registry" id="farmer_beneficiary_search_widget"/>
</strong><strong>  &#x3C;/group>
</strong>  &#x3C;group name="beneficiary_search_student" invisible="target_registry != 'student'">
    &#x3C;widget name="g2p_beneficiaries_widget" model="g2p.student.registry" id="student_beneficiary_search_widget"/>
  &#x3C;/group>
&#x3C;/xpath>
</code></pre>

## Adding Functionality (`/static`)

Inside the static folder, we have:

* `/src/css` to add any custom styles.
* `/src/js` to define and use Owl Components, such as the [`G2PBeneficiariesComponent`](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/blob/3.0/g2p_registry_addon/static/src/js/beneficiaries_widget.js) for custom logic related to the beneficiaries search functionality.
* `/src/xml` to define registry specific views, such as the [`g2p_beneficiaries_info_tpl`](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/blob/3.0/g2p_registry_addon/static/src/xml/g2p_beneficiaries_info_tpl.xml) for custom beneficiary search views.

During custom implementation, based on the models the only necessary changes to be done in the `/static` folder is updating the table [head](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/blob/7341f27f7726f0a003881dd9c4ad67e1fc6a71a7/g2p_registry_addon/static/src/xml/g2p_beneficiaries_info_tpl.xml#L30) and [data](https://github.com/OpenG2P/openg2p-pbms-odoo-extensions/blob/7341f27f7726f0a003881dd9c4ad67e1fc6a71a7/g2p_registry_addon/static/src/xml/g2p_beneficiaries_info_tpl.xml#L57) fields in the beneficiaries info template based on the [response structure](../registry-connectors/example-implementation-workflow.md) set during registry connector setup.

{% hint style="info" %}
Custom looking views for Eligibility and Entitlement Summary view screens are not registry specific and are explained in [Summary View](../summary-view/)
{% endhint %}

***

Once you’ve pushed your custom add-ons code to GitHub, you can move on to building a tailored Docker image for your setup. Simply follow the existing [Docker creation guide](../../pbms-docker.md#odoo) for **PBMS Odoo**, and update the path to point to your extensions package.

This ensures your deployment aligns with PBMS standards while giving you the flexibility to integrate new registries and custom logic cleanly.

---
description: >-
  A brief discussion about the summary view in PBMS odoo user interface followed
  by ways to customize the same
---

# Summary View

Summary lines (the underlying model responsible for rendering the summary view) runs onclick of the `View <Eligibility/Entitlement>  List` button via the method [`_compute_summary_lines`](https://github.com/OpenG2P/openg2p-pbms-odoo/blob/aa01745d6826d8410a2b21892dfca99a25200cf1/g2p_pbms/models/beneficiary_list/bgtask_summary_wizard.py#L269)<br>

<figure><img src="../../../../.gitbook/assets/image (85).png" alt=""><figcaption></figcaption></figure>

The programmatic flow is as follows

* Clear existing summary lines by `wizard.summary_line_ids = [(5, 0, 0)]`
* Fetch configuration parameters `staff_portal_api_url`, `keymanager_sign_application_id` for formulating  a request.
* Construct an API request payload with `beneficiary_list_id` and `target_registry`
* Sign the payload using the `keymanager.provider` service and issues a POST request to the `/summary` endpoint of pbms staff portal api
* Parse the [JSON response](../registry-connectors/example-implementation-workflow.md#create-custom-schema-schemas-and-model-definitions-models), which includes two major parts:
  * `beneficiary_list_summary`: general summary fields for the list
  * `registry_summary`: optional type-specific fields
* Iterate over the keys of both summaries (skipping excluded keys like `id` and `target_registry`). For each key:
  * If the value is a dictionary (mapping benefit\_code\_id → value), it resolves the `benefit_mnemonic` and `measurement_unit` and creates a line with `summary_type='entitlement'` if from `beneficiary_list_summary`, or from `registry_summary` it may use `'eligibility'` or `'entitlement'` depending on context.
  * If scalar value, formats numbers (thousands separators) and creates a line with `summary_type='general'` or `'eligibility'`.
* Write the list of new lines into `wizard.summary_line_ids` as Many2many commands \[(0, 0, {...})].
* The wizard lines are stored in the `g2p.api.summary.line` model, which has fields: `wizard_id` (Many2one), `key`, `value`, and `summary_type` (selection: general / entitlement / eligibility).

This is how the summary lines are stored as key value pairs instead of hard coded column headers making them easy to customize.

<figure><img src="../../../../.gitbook/assets/image (86).png" alt=""><figcaption></figcaption></figure>

Each section corresponds to a `summary_type`:

* General: for overall beneficiary list metrics.
* Eligibility: for demographic or eligibility data.
* Entitlement: for benefit distribution and entitlement statistics.

```xml
<page string="Summary">
  <group>
    <strong><field name="general_title" readonly="1" widget="handle_display"/></strong>
    <field name="summary_general_line_ids" nolabel="1">
      <tree create="false" edit="false">
        <field name="key"/><field name="value"/>
      </tree>
    </field>
  </group>
  <group>
    <strong><field name="eligibility_group_title" readonly="1" widget="handle_display"/></strong>
    <field name="summary_eligibility_line_ids" nolabel="1">
      <tree create="false" edit="false">
        <field name="key"/><field name="value"/>
      </tree>
    </field>
  </group>
  <group>
    <strong><field name="entitlement_group_title" readonly="1" widget="handle_display"/></strong>
    <field name="summary_entitlement_line_ids" nolabel="1">
      <tree create="false" edit="false">
        <field name="key"/><field name="value"/>
      </tree>
    </field>
  </group>
</page>
```

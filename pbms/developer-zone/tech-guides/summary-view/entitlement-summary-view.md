---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Entitlement Summary View

Entitlement metrics come from two places:

* The `beneficiary_list_summary` portion of the API response, specifically fields like `total_disbursement_quantity`, `average_entitlement_per_registrant`, and any mapping of `benefit_code_id` to value. These are processed with `summary_type='entitlement'`
* The `registry_summary` dictionary entries may also be tagged with `summary_type='entitlement'`, especially when they contain _entitlement_ statistics (e.g., `entitlement_amount_q1`, `entitlement_amount_male_q3`).

The same formatting logic applies as for eligibility lines: numeric formatting, measurement units looked up using benefit\_code mapping, title-cased “key”.

### Storage & UI linkage

* Records with `summary_type='entitlement'` are inserted into the `g2p.api.summary.line` model.
* In the UI, the summary view (for example the wizard’s results page) aggregates or lists these entitlement lines—allowing users to inspect disbursement quantities, averages and quartiles for each benefit code.

### Customizing new fields

For entitlement fields (e.g., a new benefit code metric or multiplier-based value) you can follow a similar path:

1. Include the new entitlement metric in the `beneficiary_list_summary` or in the `registry_summary` as a dictionary keyed by `benefit_code_id`.
2. Extend your model to capture that metric (you may add fields to `BeneficiaryListSummaryFarmer` or a custom summary model). Keep in mind that the logic for calculation and handling of this metric must also be created in the extensions.
3. The generic loop in `_compute_summary_lines` handles dictionary-values: benefit\_code\_id → value. So no change is needed to logic. You only need to ensure your benefit code shows up in `g2p.benefit.codes` so `benefit_mnemonic` resolution works.
4. If you need to display a new measurement unit, update the `measurement_unit` in `g2p.benefit.codes` rather than altering the loop logic.
5. Again, bundle your additions in a separate Odoo module (inherit models, extend views) so core code remains untouched and upgradeable.


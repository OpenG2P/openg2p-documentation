---
description: >-
  Proposal: make the activity register staff UI configurable where
  implementations differ (tabs, list columns, context and summary pages, form
  widgets), in line with the registry platform's widget approach for registers.
---

# Activity Register UI Configuration (Proposal)

{% hint style="warning" %}
**Status: proposed, not built.** This page describes a design for the staff UI and the activity configuration. What exists today is in the table below and in [Activity register](../features/activity-register.md) and its [design](activity-register.md).
{% endhint %}

## The issue

A register's staff portal screens are set by configuration: sections, tabs and fields are metadata, and the platform's widget library renders them, so a registry such as the Farmer Registry needs no UI code.

The activity register UI is generic platform code (`ui/staff-ui/src/app/[locale]/activity/…`, `features/activity/…`), the same for every activity register. It is only partly driven by configuration:

| Part | Today |
| --- | --- |
| Record form | Generated from each activity type's JSON Schema (`SchemaForm`), with its own inputs for geography and calendar dates. It does not use the platform's widget library |
| Tabs | Fixed in code (`app/[locale]/activity/[type]/page.tsx`): Activities, Contexts (labelled Current state when the register has a projection), Work list, Summaries, Indicators, Record, Settings, for every activity register |
| List columns, context page, summary display | Partly configurable through `ui_hints` in the activity configuration (`meta_data/activity-config/<Register>.json`): `context_columns`, `summary_fields`, `batch_carry_fields`, search placeholders. The rest is fixed in code |

## Decision so far

No full page builder: an activity register's screens follow its model (activities, contexts with their current state, aggregates, indicators), which is the same for crop sowing, livestock events or attendance. Make configurable only what really varies between implementations, with today's screens as the default, so existing registries (e.g. the Crop Sown Registry) keep working unchanged.

## What to build

All settings in the activity configuration file, extending `ui_hints`.

| # | Change | Effort | Risk |
| --- | --- | --- | --- |
| 1 | **Tabs shown and their labels:** e.g. no Work list when no type needs verification, "Crop seasons" or "Herds" for contexts, no Indicators | Small | Low |
| 2 | **List columns** for activities, contexts and summaries: which payload, current-state or aggregate fields (extends `context_columns`, `summary_fields`) | Small to medium | Low |
| 3 | **Context and summary pages:** which current-state and aggregate fields, and how they are grouped | Medium | Low |
| 4 | **Form widgets from the platform's widget library,** chosen per field with a schema hint (e.g. `x-widget`), so registers and activity registers share one widget set; the calendar date input and the geography picker become ordinary widgets | Larger | Medium: data entry; test with an existing register's forms (e.g. the Crop Sown Registry's) |

## Order of work

1. A short design note in the [Activity Register design](activity-register.md).
2. Items 1 to 3 together; document the settings; existing registries unchanged by default.
3. Item 4 separately, after checking the widget library's components against the activity form's needs (calendar dates, geography, lists, participants).

## Done when

* Every activity register gets today's screens with no new settings.
* A registry can hide or rename tabs, choose list columns and lay out the context and summary pages through its activity configuration alone.
* The record form uses the platform's widgets, chosen per field; no registry needs UI code.
* The settings are documented in the Activity Register design page.

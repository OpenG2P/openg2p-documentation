# Customise ODK Form - Add Ethiopian Calendar

The field registration agents download the ODK forms using the ODK Collect App. The ODK form can be tailored to meet specific demographic needs. A customised ODK form is used to record the registrants' data in \*Ethiopian calendar format as needed.

{% hint style="info" %}
The [Ethiopian Calendar](https://ethiopianembassy.org/ethiopian-time/) has 12 months of 30 days each, plus five or six additional days (sometimes known as the 13th month), which are added at the end of the year to match the calendar to the solar cycle.
{% endhint %}

An Ethiopian calendar format is needed during,

* Data collection using ODK.
* Storage of data/time field in the Social Registry.
* Calculations based on Ethiopian date time.

## **Customise ODK form**

Add **ethiopian** to the appearance column in the xls-formatted ODK form to capture the registrants' data in Ethiopian calendar format as needed.

## Customise parameter value

The ODK form's customised parameter values are listed below the relevant columns to assist the field agents record registrants' data in Ethiopian calendar format as needed.

<table><thead><tr><th width="92">type</th><th width="142">name</th><th width="129">label</th><th>required</th><th>appearance</th></tr></thead><tbody><tr><td>date</td><td>ethiopian_calendar</td><td>Ethiopian Calendar</td><td>yes</td><td>ethiopian</td></tr></tbody></table>

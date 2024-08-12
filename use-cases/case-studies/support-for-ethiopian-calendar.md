# Customise ODK form with Ethiopian Calendar

The field registration agents download the ODK forms using the ODK Collect App. The ODK form can be tailored to meet specific demographic needs. Here, the registrants' data is captured in \*Ethiopian calendar format using a customised ODK form.

{% hint style="info" %}
The [Ethiopian Calendar](https://ethiopianembassy.org/ethiopian-time/) has 12 months of 30 days each, plus five or six additional days (sometimes known as the 13th month), which are added at the end of the year to match the calendar to the solar cycle.
{% endhint %}

The Ethiopian calendar format is required during,

* Data collection using ODK.
* Storage of data/time field in the Social Registry.
* Calculations based on Ethiopian date time.

## **Customise ODK form**

Add **ethiopian** to the appearance column in the xls-formatted ODK form to capture the registrants' data in Ethiopian calendar format.

## Customise parameter value

The following parameter values are customised in ODK form to assist the field agents in capturing the registrants' data in Ethiopian calendar format.

<table><thead><tr><th width="92">type</th><th width="142">name</th><th width="129">label</th><th>required</th><th>appearance</th></tr></thead><tbody><tr><td>date</td><td>ethiopian_calendar</td><td>Ethiopian Calendar</td><td>yes</td><td>ethiopian</td></tr></tbody></table>

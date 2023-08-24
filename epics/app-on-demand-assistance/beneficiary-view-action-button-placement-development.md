# Beneficiary view action button placement: Development

## &#x20;Introduction-

Adding Verify & Enrol, Verify Eligibility and Deduplicate buttons to the beneficiaries header view

### Built With:

* XML: Used for creating the views and record rules
* Odoo: Used for providing a range of features and functionalities
* Python: Used for creating models which creates business logic

### Installation:

* Download g2p\_programs module. Add this module to the addons-path and run the Odoo server
* Go to Apps Menu and install the module

### Functionality:

* On click of beneficiaries list link, eligible beneficiaries list for that associated program will be displayed
* Click on beneficiary, beneficiary view will be displayed along with Verify Eligibility, Verify & Enrol and Deduplicate buttons for the Draft status. Verify & Enrol, Deduplicate buttons will be displayed for the Enrolled status beneficiaries.
* Verify Eligibility button will check eligibility of the respective beneficiary and change the status to **not eligible** status in case of not eligible. If beneficiary is eligible then message will get displayed on the window.
* Verify & Enrol button will check eligibility of respective beneficiary and change the status to enrolled status.
* Deduplicate button will check duplicate beneficiaries and change the status to duplicated status

### Conclusion

Verify Eligibility, Verify & Enrol and Deduplicate buttons added in Draft status. Verify & Enrol, Deduplicate buttons are added under the Enrolled status of the beneficiaries window.

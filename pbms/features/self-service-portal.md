---
layout:
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
---

# Self Service Portal

Self-Service Portal allows an individual registrant seeking assistance to register from any place and any device with internet connectivity. The individual registrant logs in using a foundational or functional ID and then applies for a program. \
![](<../../.gitbook/assets/image (1).png>)\
\
For self-registration, an OTP or QR code is typically used in addition to a unique ID number to log in. For assisted registration, to do biometric authentication, the assisting officer uses a biometric device connected to a machine which has access to the Self-Service Portal.\
\
![](<../../.gitbook/assets/image (2).png>)

The Self-Service Portal registration process assumes that an authentication service is available for ID verification. The portal allows an individual to perform the following functions:

**Program management**

* View the list of available programs
* Apply for a new program
* Upload supporting documents if required for a program
* View the registrant's enrolled programs
* Track the status of the application
* Track the entitlement status of the program

**Profile management**

* Update personal information and demographic details
* View all the demographic information submitted across programs

Depending on the program implementation, the registrant can seek assistance to apply for the same program multiple times. For example, a registrant seeks medical assistance for different treatments. It is assumed that Program administrators will apply mechanisms to prevent cases of double-dipping.

## Registration process

A program administrator must do these steps to allow registrants to apply for a program:

* Create a program: To learn the steps, click [here](../user-guides/eligibility-and-program-enrollment/program/create-a-program.md).
* Create a Self-Service Portal form: To learn the steps, click [here](../user-guides/eligibility-and-program-enrollment/website/create-portal-form.md).
* Map Self-Service Portal form: To learn the steps, click [here](../user-guides/eligibility-and-program-enrollment/program/map-self-service-portal-form.md).

Registrant's ID verification takes place during the login. The registrant also provides consent to share demographic details with the Self-Service Portal. Upon successful ID verification, the Self-Service Portal can automatically populates the registrant's demographic details based on the consent provided during login. The registrant fills in the rest of the details and applies for a program. Learn more about self-registration [here](../user-guides/registration/self-register-online.md).



**Features and its functionality(WIP)**

<table><thead><tr><th width="168">Features</th><th>Functionality</th><th data-hidden></th></tr></thead><tbody><tr><td>My Programs</td><td><ol><li>To show the list of programs which registrant has applied and enrolled</li><li>The enrolment status as applied talks about  the registrant applied to a program, when the eligibility is run and entitlements are approved for a program, it changes from applied to enrolled</li><li>The total funds awaited and total funds received represent the amount which registrant is eligible to get for a program and actual received amount</li></ol></td><td></td></tr><tr><td>All Programs</td><td><ol><li>To show the list of active and available program which registrant can apply/reapply </li></ol></td><td></td></tr><tr><td>My Application</td><td><ol><li>Here it shows the list of  applied programs</li><li>The applied status are applied and completed</li><li>The application ID generated with unique 10 digit number, which is show against each of the applied programs</li><li>It also show the date and time applied for a program, which enables the user to keep the track of the time and latest application</li></ol></td><td></td></tr><tr><td>My Benefits</td><td><ol><li>It shows the list of beneficiary enrolled for a program</li><li>A unique ER number is generated when the entitlement is approved and in case the entitlement is not approved, it shows “ entitlement not approved”</li><li>Funds Awaited-Entitlement (Amount in US Dollars): Shows the expected amount against each cycle and approved entitlement.</li><li>Funds Received (Amount in US Dollars): Displays the amount received by the beneficiary against the ER number.</li></ol></td><td></td></tr></tbody></table>

##

## OpenID Connect integration

The Self-Service Portal allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with [eSignet](https://docs.esignet.io/). To learn more about ID verification using e-Signet, click [here](broken-reference).

### OIDC integration

The Self-Service Portal can integrate with any OIDC server to provide user login.



**Jira Board(WIP)**\
Link the US on the SSP

\
\


{% embed url="https://openg2p.atlassian.net/jira/software/c/projects/G2P/issues/?filter=allissues&jql=project+=+%22G2P%22+and+type+=+Story+and+parent+=+G2P-1156+ORDER+BY+created+DESC" %}

\<image and demo video to be integrated>

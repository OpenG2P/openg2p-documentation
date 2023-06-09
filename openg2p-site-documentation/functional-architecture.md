# Functional Architecture

OpenG2P has a flexible architecture that allows governments and social benefit delivery systems to choose functionalities per their needs. The platform is built to allow inclusion and has supporting features. For example, beneficiaries in remote areas without any network connectivity can be registered offline. The platform enables bulk payments as well as on-demand payments. The payment approval can involve digital approval, multiple approvals as well as manual interventions and the platform is capable of supporting such disparate benefit disbursements.

<figure><img src="../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
**External System Integrations**

Digital authentication can be facilitated using MOSIP or any other ID system as the platform is agnostic of ID systems.&#x20;

The platform can integrate with payment systems other than the three payment systems shown in the diagram. &#x20;
{% endhint %}

## Configuring a benefits scheme

Each social benefits delivery scheme is configured as a program in the platform.

### Workflow

&#x20;The program uses these broad functions to achieve benefit disbursement:

1. Registration: Collect all the relevant information about the beneficiary. The relevant information fields are decided during program creation. The beneficiary can be an individual, family, or a group.
2. Enrollment and Entitlement: Registered beneficiaries are enrolled into a program after deduplicating the registered entries. Based on the eligibility criterion configured in the program such as age, gender, and income, the program manager will mark the beneficiary as entitled to receive the scheme benefits.
3. Notification: Beneficiaries can be notified through SMS/email based on program's notification configuration.
4. Benefit Disbursement: The benefit can be disbursed as cash, voucher/coupon, in-account, or in-kind. Program management allows various disbursements.&#x20;

### Technical architecture <a href="#technical-architecture" id="technical-architecture"></a>

<figure><img src="../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>

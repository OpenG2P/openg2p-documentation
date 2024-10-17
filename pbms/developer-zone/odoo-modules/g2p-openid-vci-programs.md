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

# G2P OpenID VCI: Programs

### Module name

g2p\_openid\_vci\_programs

### Module title

G2P OpenID VCI: Programs

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

* This module adds a new issuer type called `Beneficiary,`extending the _**G2P OpenID VCI**_ module functionality. It effectively adds the ability to issue VC for beneficiaries who are part of a program in PBMS.
* It adds a parameter to attach a Program to an Issuer. With this module, each Program in PBMS is an issuer.
  * For example, if three programs are operating on PBMS, 3 different issuers can be created with issuer\_type as "Beneficiary" and different programs.
    * Configure 3 different scopes for the three issuers. Example:
      * IssuerName: "SafetyNetIssuer", scope: "safety\_net\_program\_vc\_ldp", Program: "Safety Net Program".
      * IssuerName: "HumAidIssuer", scope: "hum\_aid\_program\_vc\_ldp", Program: "Humanitarian Aid Program", etc.
      * If the content of the credential is the same for all the 3 programs, then use a generic credential\_type and format across all three issuers, like "OpenG2PBeneficiaryVerifiableCredential". If the content is different in all programs, use different credential types.
* Unlike a Registry VC, a Beneficiary may contain additional data, like the name of the Program, the duration for which this beneficiary is part of the program, the last date till which this beneficiary is part of the program, etc. This module supports all of these.

Note:

* A credential will only be issued if the sub from auth JWT exists as one of the IDs in the registry against a registry entry, and the registrant is also an enrolled beneficiary of the said program.
* The rest of the functionality from the base module remains the same.

### Source code

[https://github.com/openg2p/openg2p-vci-beneficiary](https://github.com/openg2p/openg2p-vci-beneficiary)

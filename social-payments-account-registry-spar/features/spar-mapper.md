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

# spar-mapper

* Maintains a mapping between Beneficiary ID and the Beneficiary's Financial Address
* The Beneficiary ID can be anyone of the following
  * Beneficiary ID issued by a Country, that uniquely identifies the beneficiary
  * In the absence of a comprehensive National ID Program, the Beneficiary ID issued by the Department that administers a particular Social Program can be used
  * Any other ID, that is prevalent in the Country, that works reasonably to establish the identity of a beneficiary - e.g. Social Security Number, Income-Tax-ID, Passport ID etc. are examples that may be used
  * A token issued by a Token Issuing Platform, that issues a Token against a Beneficiary ID
* The Financial Address can be one of
  * Bank Account&#x20;
  * Mobile Wallet
* Many IDs to One FA, One ID to One FA --????? **TBD**
* [G2P Connect Compliant APIs](https://g2pconnect.cdpi.dev/protocol/interfaces/beneficiary-management/mapper-specs) - to
  * link - link a Beneficiary ID and Financial Address
  * unlink - unlink the existing mapping (delete the existing mapping)
  * modify - update the Financial Address&#x20;
  * resolve - given a beneficiary Id, query to retrieve the Financial Address
* Signature verification for clients (partners)  via integrations with MOSIP's Partnermanager & Keymanager - **TBD**

#### The Mapper can be visualized in a tabular depiction as follows

<table><thead><tr><th width="352.5">ID</th><th>Account Number</th></tr></thead><tbody><tr><td>234AFBC@mosip.openg2p</td><td>45678756456@branchOne@bankOne</td></tr><tr><td>DBCF34A@mosip.socialaccountregistry</td><td>9957585955@mpesa.ke</td></tr></tbody></table>

#### Usage in the G2P transfer chain


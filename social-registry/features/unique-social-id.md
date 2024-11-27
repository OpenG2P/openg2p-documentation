# Unique Social ID

### Description <a href="#description" id="description"></a>

OpenG2P's Social Registry supports the feature of generating randomized unique IDs both individuals and households that may be used to issue a "Social ID", "Family ID", "Famer ID", or any way that uniquely identifies a record in the SR.  This is essential for ensuring accurate and efficient tracking and updating of records.  The need arose to enhance data consistency and integration with other systems within the registry. We use MOSIP's sophisticated ID generator  which applies several rules before assigning an ID to a record.  Learn more about ID generator here:

{% embed url="https://docs.mosip.io/1.2.0/modules/commons/id-generator" %}

{% embed url="https://miro.com/app/board/uXjVKsusfaU=/?share_link_id=212808513356" %}

### Technical design

* It is implemented as an [Odoo](https://www.odoo.com/documentation/17.0/) module.
* It involves two new table creation.&#x20;
  * **g2p.reference.id.config** table for the Configurations.
  * **g2p.pending.reference\_id** table for storing the registrant if reference ID is not generated for them.

### Source Code

WIP

### Dependencies

It requires the MOSIP [id-generator](https://docs.mosip.io/1.1.5/modules/kernel/uin-and-vid-generation-service-functionality) service.


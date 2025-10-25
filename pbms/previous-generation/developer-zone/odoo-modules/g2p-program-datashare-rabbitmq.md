# G2P Program Datashare: RabbitMQ

### Module name

`g2p_program_datashare_rabbitmq`

### Module title

G2P Program Datashare: RabbitMQ

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module extends the core [RabbitMQ DataShare](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/~/changes/1370/social-registry/developer-zone/odoo-modules/g2p-registry-datashare-rabbitmq) module to support publishing **Beneficiary Registry** data from PBMS (`g2p.program_membership` to external systems via RabbitMQ.

Key enhancements:

* **New Data Source Type**: Introduces a new `data_source` value: `beneficiary_registry`, allowing RabbitMQ configurations specific to PBMS beneficiary data.
* **Program-Specific Configuration**: Introduces a `program_id` field in the RabbitMQ configuration to optionally scope data sharing to a specific program.
* **Automatic Publishing on Change**: Automatically triggers data publishing when a beneficiary is added to a program or when their record is updated.
* **Reuses Core Functionality**: Inherits and utilizes the base module’s RabbitMQ connection and JQ transformation capabilities.

With this module, key beneficiary information—such as program enrollment and participation details—can be streamed in real time to downstream systems for analytics, interoperability, or reporting purposes.

### Source code

[https://github.com/openg2p/openg2p-program](https://github.com/openG2P/openg2p-program)

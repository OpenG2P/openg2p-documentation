# G2P Registry Datashare: RabbitMQ

### Module name

`g2p_registry_datashare_rabbitmq`

### Module title&#x20;

G2P Registry Datashare: RabbitMQ

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module enables real-time data publishing from the Social Registry (`res.partner` model) to external systems via RabbitMQ. It is designed to:

* **Push Data on Change**: Automatically sends registrant data to RabbitMQ upon creation or update.
* **JQ-Based Transformation**: Applies a configurable JQ expression to format data before publishing.
* **Multiple Configurations**: Supports multiple RabbitMQ configurations to publish data to different exchanges and routing keys.

### Design notes

The core purpose of this module is to facilitate flexible data exchange from the Social Registry to external systems through RabbitMQ. This is achieved via the `g2p.datashare.config.rabbitmq` model, which defines:

* Connection parameters to RabbitMQ.
* Routing settings (exchange, routing key).
* Optional JQ expressions for data transformation.

The use of **JQ expressions** enables dynamic construction and filtering of outgoing payloads, tailored to downstream consumer requirements. Configurations can be toggled as active/inactive, allowing runtime control over which pipelines are enabled.

#### **Model: `g2p.datashare.config.rabbitmq`**

* Stores connection details, routing settings, and transformation logic.
* JQ transformation is applied via the `jq` Python library, using a default of `{}`.
* `_connect_to_rabbitmq()` establishes a `pika`-based connection to RabbitMQ.
* `publish(data)` serializes and sends the transformed data as a JSON message to the configured exchange/routing key.

#### **Model Extension: `res.partner`**

* `_push_to_rabbitmq()` is invoked on creation and write operations.
* It filters to only publish data for registrants (`is_registrant=True`).
* It loops through all active configs with `data_source = "registry"`, transforms data using the configured JQ expression, and publishes it.

### Configuration

* Create a rabbitMQ configuration record under `Settings` > `RabbitMQ Datashare`  page.
* General config properties:

<table><thead><tr><th width="221">Name</th><th width="174">Property name</th><th>Description</th></tr></thead><tbody><tr><td>Name</td><td>name</td><td>Name of the config.</td></tr><tr><td>Data Source</td><td>data_source</td><td>Source from which data will be shared</td></tr><tr><td>Active</td><td>active</td><td>Toggle to enable/disable the config</td></tr><tr><td>Host</td><td>host</td><td>RabbitMQ server address</td></tr><tr><td>Port</td><td>port</td><td>The TCP port number RabbitMQ is listening on (default is 5672).</td></tr><tr><td>Username</td><td>username</td><td>RabbitMQ credentials</td></tr><tr><td>Password</td><td>password</td><td>RabbitMQ credentials</td></tr><tr><td>VHost</td><td>vhost</td><td>Virtual host</td></tr><tr><td>Exchange Name</td><td>exchange</td><td>Name of the exchange to publish to</td></tr><tr><td>Routing Key</td><td>routing_key</td><td>Routing key used for message delivery</td></tr><tr><td>ID type</td><td>id_type</td><td>Select the ID Type that should be used in the data payload</td></tr><tr><td>Transform Data JQ</td><td>transform_data_jq</td><td><p><a href="https://jqlang.github.io/jq/manual/">Jq</a> filter to apply to the outgoing data.</p><p>If you want to reference the ID configured in the <code>id_type</code> field, use the <code>reg_id_value</code> variable in your JQ expression.</p><p>example: </p><p><code>{"nationalID": .reg_id_value}</code></p></td></tr></tbody></table>

### Source code

[https://github.com/openg2p/openg2p-registry](https://github.com/openg2p/openg2p-vci)

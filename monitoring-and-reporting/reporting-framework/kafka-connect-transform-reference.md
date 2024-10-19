# Kafka Connect Transform Reference

This document is the configuration reference guide for Kafka SMTs developed by OpenG2P, that can be used on [OpenSearch Sink Connectors](https://github.com/OpenG2P/openg2p-reporting).

Following is a list of some of the other transformations available on the OpenSearch Connectors, apart from the ones developed by OpenG2P:

* [Apache Kafka Connect SMTs](https://kafka.apache.org/documentation/#connect\_included\_transformation).
* [Debezium Kafka Connect Transformations](https://debezium.io/documentation/reference/stable/transformations/index.html).

## Transformations

### DynamicNewField

#### Class name:

* `org.openg2p.reporting.kafka.connect.DynamicNewField$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.DynamicNewField$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

* This transformation can be used to query external data sources to retrieve new fields and add them to the current record, based on the values of some existing fields of this record.
* Currently, only Elasticsearch-based queries are supported. This means any index on Elasticsearch(or OpenSearch) can be queried and some new fields can be populated based on fields from the current record.
  * Some selected from the current record will be taken. ES will be queried for records where the selected field values match. The top response will be picked. Fields from that response can be added back to the current record.

#### Configuration:

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>query.type</td><td>Query Type</td><td><p>This is the type of query made to retrieve new field values.</p><p>Supported values:</p><ul><li><code>es</code> (Elasticsearch based).</li></ul></td><td>es</td></tr><tr><td>input.fields</td><td>Input Fields</td><td><p>List of comma-separated fields that will be considered as input fields in the current record.</p><p>Nested input fields are supported, like: (where profile is json that contains name and birthdate fields)</p><pre class="language-json"><code class="lang-json">profile.name,profile.birthdate
</code></pre></td><td></td></tr><tr><td>output.fields</td><td>Output Fields</td><td>List of comma-separated fields to be added to this record.</td><td></td></tr><tr><td>input.default.values</td><td>Input Default Values</td><td>List of comma-separated values to give in place of the input fields when an input field is empty or null.<br>Length of this has to match that of <code>input.fields</code>.</td><td></td></tr><tr><td>es.index</td><td>ES Index</td><td>Elasticsearch(or OpenSearch) index to query for.</td><td></td></tr><tr><td>es.input.fields</td><td>ES Input Fields</td><td>List of comma-separated fields, to be queried on the ES index, each of which maps to the fields on <code>input.fields</code>.<br>Length of this has to match that of <code>input.fields</code>.</td><td></td></tr><tr><td>es.output.fields</td><td>ES Output Fields</td><td>List of comma-separated fields, to be retrieved from the ES query response document, each of which maps to the fields on <code>output.fields</code>. <br>Length of this has to match that of <code>output.fields</code>.</td><td></td></tr><tr><td>es.input.query.add.keyword</td><td>ES Input Query Add Keyword</td><td>Whether or not to add <code>.keyword</code> to the <code>es.input.fields</code> during the term query. Supported values: <code>true</code> / <code>false</code> .</td><td>false</td></tr><tr><td>es.security.enabled</td><td>ES Security Enabled</td><td>If this value is given as <code>true</code>, then Security is enabled on ES.</td><td></td></tr><tr><td>es.url</td><td>ES Url</td><td>Elasticsearch/OpenSearch base URL.</td><td></td></tr><tr><td>es.username</td><td>ES Username</td><td></td><td></td></tr><tr><td>es.password</td><td>ES Password</td><td></td><td></td></tr></tbody></table>

### DynamicNewFieldInsertBack

#### Class name:

* `org.openg2p.reporting.kafka.connect.DynamicNewFieldInsertBack$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.DynamicNewFieldInsertBack$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

* This transformation can be used to add additional data to documents of different index.
* If record matches the configured condition, the given data will be updated into the record with given id.

#### Configuration:

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>query.type</td><td>Query Type</td><td><p>This is the type of query made to retrieve new field values.</p><p>Supported values:</p><ul><li><code>es</code> (Elasticsearch based).</li></ul></td><td>es</td></tr><tr><td>id.expr</td><td>ID Jq Expression</td><td>Jq expression to evaluate the ID of the external document into which the data is supposed to be updated.</td><td></td></tr><tr><td>condition</td><td>Condition</td><td>Jq expression that evaluates to a boolean value which decides whether or not to update.</td><td></td></tr><tr><td>value</td><td>Value</td><td>Jq expression of the value, that evaluates to a JSON, that is to be updated into the external document.</td><td></td></tr><tr><td>es.index</td><td>ES Index</td><td>Elasticsearch(or OpenSearch) index to update into.</td><td></td></tr><tr><td>es.security.enabled</td><td>ES Security Enabled</td><td>If this value is given as <code>true</code>, then Security is enabled on ES.</td><td></td></tr><tr><td>es.url</td><td>ES Url</td><td>Elasticsearch/OpenSearch base URL.</td><td></td></tr><tr><td>es.username</td><td>ES Username</td><td></td><td></td></tr><tr><td>es.password</td><td>ES Password</td><td></td><td></td></tr></tbody></table>

### ApplyJq

#### Class name:

* `org.openg2p.reporting.kafka.connect.ApplyJq$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.ApplyJq$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

* This transformation applies the given Jq expression on the current record and replace the current record with the result from Jq.&#x20;
* This transformation can be used for operations like extracting, merging, removing, and/or renaming fields.
* For example:
  * `"expr": ".payload.after + {source_ts_ms: .payload.source.ts_ms}",` : The expr field should contain a valid Jq expression.

#### Configuration:

<table><thead><tr><th>Field name</th><th>Field title</th><th width="268">Description</th><th>Default value</th></tr></thead><tbody><tr><td>expr</td><td>Expression</td><td>Jq expression to be applied.</td><td></td></tr><tr><td>behavior.on.error</td><td>Behaviour on error</td><td><p>What to do when encountering error applying Jq expression. Possible values:</p><ul><li><code>halt</code> : Throws exception upon encountering error.</li><li><code>ignore</code> : Ignores any errors encountered.</li></ul></td><td>halt</td></tr></tbody></table>

### StringToJson

#### Class name:

* `org.openg2p.reporting.kafka.connect.StringToJson$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.StringToJson$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

*   This transformation can be used to convert JSON string, present in a field in the record, to JSON. Example:

    ```json
    {"profile": "{\"name\":\"Temp\"}"} -> {"profile": {"name": "Temp"}}
    ```
* Currently, this transform only works in schemaless mode. (`value.converter.schemas.enable=false`).

#### Configuration

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>input.field</td><td>Input Field</td><td>Input Field that contains JSON string.</td><td></td></tr></tbody></table>

### TimestampConverterAdv

#### Class name:

* `org.openg2p.reporting.kafka.connect.TimestampConverterAdv$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.TimestampConverterAdv$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

*   This transformation can be used to convert a Timestamp present in a field in the record, to another format. Example:

    ```json
    {"create_date": 1723667415} -> {"profile": "2024-08-14'T'20:30:50.069'Z'"}
    ```
* Currently, the output can only be in the form of a string.

#### Configuration

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>field</td><td>Input Field</td><td>Input Field that contains the Timestamp.</td><td></td></tr><tr><td>input.type</td><td>Input Type</td><td><p>Supported values:</p><ul><li>milli_sec (Input is present as milliseconds since epoch)</li><li>micro_sec (Input is present as microseconds since epoch. Useful for converting Datetime field of PostgreSQL)</li><li>days_epoch (Input is present as days since epoch. Useful for converting Date field of PostgreSQL)</li></ul></td><td>milli_sec</td></tr><tr><td>output.type</td><td>Output Type</td><td><p>Supported values:</p><ul><li>string (Gives output as string)</li></ul></td><td>string</td></tr><tr><td>output.format</td><td>Output Format</td><td>Format of string output</td><td><p></p><pre class="language-json"><code class="lang-json">yyyy-MM-dd'T'HH:mm:ss.SSS'Z'
</code></pre></td></tr></tbody></table>

### TimestampSelector

#### Class name:

* `org.openg2p.reporting.kafka.connect.TimestampSelector$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.TimestampSelector$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

*   This transformation can be used to create a new timestamp field, whose value can be selected from other fields, in the order of whichever is not empty first. Example: (when `ts.order` is `profile.write_date,profile.create_date`)

    ```json
    {"profile": {"create_date": 7415, "write_date": null}} -> {"@timestamp_gen": 7415, "profile": {"create_date": 7415, "write_date": null}}
    {"profile": {"create_date": 2945, "write_date": 3442}} -> {"@timestamp_gen": 3442, "profile": {"create_date": 2945, "write_date": 3442}}
    ```

#### Configuration

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>ts.order</td><td>Timestamp order</td><td>List of comma-separated fields to select output from. The output will be selected based on whichever field in the order is not null first. Nested fields are supported.</td><td></td></tr><tr><td>output.field</td><td>Output Field</td><td>Name of the output field into which the selected timestamp is put.</td><td><pre class="language-json"><code class="lang-json">@ts_generated
</code></pre></td></tr></tbody></table>

### TriggerDeduplication

#### Class name:

* `org.openg2p.reporting.kafka.connect.TriggerDeduplication$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.TriggerDeduplication$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

* This transformation can be used to trigger deduplication when there is a change in any one of the configured fields.
* This transformation is best used before applying any other transformation.

#### Configuration

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>deduplication.base.url</td><td>Base URL of Deduplicator Service</td><td></td><td></td></tr><tr><td>dedupe.config.name</td><td>Dedupe Config name</td><td>Name of config used for deduplication by deduplicator</td><td>default</td></tr><tr><td>id.expr</td><td>ID Jq Expression</td><td>Jq expression that evaluates the ID of the document that is to be deduplicated</td><td><pre><code>.payload.after.id
</code></pre></td></tr><tr><td>before.expr</td><td>Before Jq Expression</td><td>Jq expression that evaluates the before part of the change. (Used to compare fields with the after part of the change).</td><td><pre><code>.payload.before
</code></pre></td></tr><tr><td>after.expr</td><td>After Jq Expression</td><td>Jq expression that evaluates the after part of the change. (Used to compare fields with the before part of the change).</td><td><pre><code>.payload.after
</code></pre></td></tr><tr><td>wait.before.exec.secs</td><td>Wait before Exec (in secs)</td><td>Time to wait (in secs) before starting deduplication. Useful so that the transformations get applied and the record get indexed into OpenSearch</td><td>10</td></tr></tbody></table>

## Source code

[https://github.com/OpenG2P/openg2p-reporting/tree/develop/opensearch-kafka-connector](https://github.com/OpenG2P/openg2p-reporting/tree/develop/opensearch-kafka-connector)

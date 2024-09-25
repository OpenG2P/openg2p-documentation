# Kafka Connect Transform Reference

also supports the extraction of nested fieldsThis document is the configuration reference guide for Kafka SMTs developed by OpenG2P, that can be used on [OpenSearch Sink Connectors](https://github.com/OpenG2P/openg2p-reporting).

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

### ExtractFieldAdv

#### Class name:

* `org.openg2p.reporting.kafka.connect.ExtractFieldAdv$Key` - Applies transform only to the _Key_ of Kafka Connect Record.
* `org.openg2p.reporting.kafka.connect.ExtractFieldAdv$Value` - Applies transform only to the _Value_ of Kafka Connect Record.

#### Description:

* This transformation can be used to extract, merge, and/or rename fields in the record.
* This also supports the extraction of nested fields.
* For example:
  * `"field": "payload",` : The `payload` field is extracted and the record is replaced with the extracted value.
  * `"field": "payload.before",` : The `before` field inside `payload` field is extracted and the record is replaced with the extracted value.
  * `"field": "source,payload.before,payload.after",` : The `source` field and the `before` and `after` fields inside the `payload` field are merged, and the record is replaced with the final merged value. Fields in `after` will be prioritized over fields in `before`, and `before` is prioritized over `source` and so on from the config list. Maps or arrays inside the above fields will be merged.
  * `"field": "source.ts_ms->source_ts_ms,source.table->source_table",` : The `ts_ms` field in `source` will be extracted and renamed to `source_ts_ms`. The `table` field in `source` will be extracted and renamed to `source_table`. The final record contains only `source_ts_ms` and `source_table` fields.
  * `"field": "source.ts_ms->source_ts_ms,payload.before,payload.after",` : The `source_ts_ms` field is added to the merged value of `before` and `after` fields (from `payload` ), and the record is replaced with the final merged value. If the `source_ts_ms` field is already present in `after` , it will be prioritised over the one from `source`.
* This transformation extends from the `ExtractField` transform by Apache.[https://kafka.apache.org/documentation/#org.apache.kafka.connect.transforms.ExtractField](https://kafka.apache.org/documentation/#org.apache.kafka.connect.transforms.ExtractField)

#### Configuration:

<table><thead><tr><th>Field name</th><th>Field title</th><th width="268">Description</th><th>Default value</th></tr></thead><tbody><tr><td>field</td><td>Field name to extract</td><td>Name of the field (or list of fields) to be extracted and merged.</td><td></td></tr><tr><td>array.merge.strategy</td><td>Array merge strategy</td><td><ul><li>Strategy to merge nested arrays.</li><li><p>Available values:</p><ul><li><code>concat</code> : Merge two arrays.</li><li><code>replace</code> : Replace array with new array.</li></ul></li></ul></td><td>concat</td></tr><tr><td>map.merge.strategy</td><td>Map merge strategy</td><td><ul><li>Strategy to merge nested maps.</li><li><p>Available values:</p><ul><li><code>deep</code> : Deep merge two maps.</li><li><code>replace</code> : Replace map with new map.</li></ul></li></ul></td><td>deep</td></tr></tbody></table>

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

<table><thead><tr><th width="210">Field name</th><th width="138">Field title</th><th>Description</th><th width="100">Default Value</th></tr></thead><tbody><tr><td>ts.order</td><td>Timestamp order</td><td>List of comma-separated fields to select output from. The output will be selected based on whichever field in the order is not null first. Nested fields are supported.</td><td></td></tr><tr><td>output.field</td><td>Output Field</td><td>Name of the output field into which the selected timestamp is put.</td><td><p></p><pre class="language-json"><code class="lang-json">@ts_generated
</code></pre></td></tr></tbody></table>

## Source code

[https://github.com/OpenG2P/openg2p-reporting/tree/develop/opensearch-kafka-connector](https://github.com/OpenG2P/openg2p-reporting/tree/develop/opensearch-kafka-connector)

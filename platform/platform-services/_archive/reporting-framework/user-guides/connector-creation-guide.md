# 📔 Connector Creation Guide

Creating Dashboards for Reporting involves the following steps:

* Understanding what database tables are required to be indexed to OpenSearch for the dashboard.
* Creating a pipeline for the data flow to OpenSearch. This pipeline involves:
  * Creating one Debezium Connector containing the database table.
  * Creating one OpenSearch Connector for the database table.
* Creating a dashboard on OpenSearch

Follow the guides on this page to learn more about each step in the process above.

This document contains instructions for the developers (or dashboard creators) on creating the required connectors and dashboards to visualize reports on OpenSearch.

Follow the [Installation guide](installation-and-troubleshooting.md) to install/update the connector configuration.

## Prerequisites

* Create a GitHub repository (or create a new directory in an existing repository) which is going to store the configuration for the connectors and the dashboards for OpenSearch.
* Create a directory in the repository with these three folders `debezium-connectors` , `opensearch-connectors` and `opensearch-dashboards` .
* For example [https://github.com/OpenG2P/openg2p-reporting/tree/develop/scripts/social-registry](https://github.com/OpenG2P/openg2p-reporting/tree/develop/scripts/social-registry).
* Identify the tables from the database whose data will be required for the reports.

## Debezium connector creation

* One debezium connector is sufficient for indexing all the required tables of one database. So create one connector for each database (rather than one for each table).
*   Create a json file in the `debezium-connectors` . Each json file corresponds to one debezium connector. With the following contents:

    ```json
    {
        "name": "${DB_PREFIX_INDEX}_${DB_NAME}",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "plugin.name": "pgoutput",
            "publication.autocreate.mode": "filtered",
            "slot.name": "dbz_${DB_PREFIX_INDEX}_${DB_NAME}",
            "publication.name": "dbz_pub_${DB_PREFIX_INDEX}_${DB_NAME}",
            "database.hostname": "${DB_HOSTNAME}",
            "database.port": "${DB_PORT}",
            "database.user": "${DB_USER}",
            "database.password": "${DB_PASS}",
            "database.dbname": "${DB_NAME}",
            "topic.prefix": "${DB_PREFIX_INDEX}",
            "table.include.list": "",
            "heartbeat.interval.ms": "${DEFAULT_DEBEZIUM_CONNECTOR_HEARTBEAT_MS}",
            "decimal.handling.mode": "double",
            "tombstones.on.delete": false
        },
        "wait_after_init_secs": 20
    }
    ```

{% hint style="info" %}
Each `$` in the json file will be treated as an environment variable. Environment variables will be automatically picked up during installation. If you want to use a dollar in the file and not parse it as env variable during installation, replace your `$` with `${dollar}` .
{% endhint %}

*   Add the list of all tables required from this database into the `table.include.list` field (in no particular order) (Accepts regex). For example

    ```json
    "table.include.list": "public.res_partner,public.g2p_program_membership,public.g2p_programs"
    ```

    * This list needs to include relationship tables of the current table. For example: if you want to index `g2p_program_membership` but would also like to retrieve the name of the program in which the beneficiary belongs, then you have to add `g2p_program` as well.
* Example debezium connector [https://github.com/OpenG2P/openg2p-reporting/blob/develop/scripts/social-registry/debezium-connectors/default.json](https://github.com/OpenG2P/openg2p-reporting/blob/develop/scripts/social-registry/debezium-connectors/default.json)&#x20;
* [Debezium PostgreSQL Connector](https://debezium.io/documentation/reference/stable/connectors/postgresql.html) Reference.

## OpenSearch connector creation

*   Each json file in the `opensearch-connectors` folder will be considered a connector. Create one connector file for each table with the following content:

    ```json
    {
        "name": "res_partner_${DB_PREFIX_INDEX}",
        "config": {
            "connector.class": "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
            "connection.url": "${OPENSEARCH_URL}",
            "connection.username": "${OPENSEARCH_USERNAME}",
            "connection.password": "${OPENSEARCH_PASSWORD}",
            "tasks.max": "1",
            "topics": "${DB_PREFIX_INDEX}.public.res_partner",
            "index.write.method": "upsert",
            "key.ignore": "false",
            "schema.ignore": "true",
            "key.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "key.converter.schemas.enable": "true",
            "value.converter.schemas.enable": "false",

            "behavior.on.null.values": "delete",
            "behavior.on.malformed.documents": "warn",
            "behavior.on.version.conflict": "warn",

            "transforms": "keyExtId,valExt,tsconvert01,...",

            "transforms.keyExtId.type": "org.apache.kafka.connect.transforms.ExtractField${dollar}Key",
            "transforms.keyExtId.field": "id",

            "transforms.valExt.type": "org.openg2p.reporting.kafka.connect.transforms.ApplyJq${dollar}Value",
            "transforms.valExt.expr": ".payload.after + (if .payload.after then {source_ts_ms: .payload.source.ts_ms} else null end)",

            "transforms.tsconvert01.type": "org.openg2p.reporting.kafka.connect.transforms.TimestampConverterAdv${dollar}Value",
            "transforms.tsconvert01.field": "source_ts_ms",
            
            ...
    }
    ```
* Replace `name` with the appropriate table names.
*   Replace `topics` field with the name of table.

    ```json
    "topics": "${DB_PREFIX_INDEX}.public.g2p_program",
    ```
* After the base file is configured, you can now add transformations to your connector at the end of the file (denoted by `...` in the above example). Each transformation (SMT) will apply some change to the data or a particular field from the table, before pushing the entry to OpenSearch.
* Add the following transformations to your connector based on the data available in the table.
  *   For every Datetime field / Date field in the table add the following transform.

      ```json
      "transforms.tsconvert02.type": "org.openg2p.reporting.kafka.connect.transforms.TimestampConverterAdv${dollar}Value",
      "transforms.tsconvert02.field": "create_date",
      "transforms.tsconvert02.input.type": "micro_sec",
      ```
  *   At the end of all the transformations, add a TimestampSelector transform, which creates a new `@timestamp_gen` field whose value can be selected as any of the available Datetime fields in the table. This will be useful while creating a Dashboard on OpenSearch, where we can use this new `@timestamp_gen` field as the IndexPattern timestamp.

      ```json
      "transforms.tsSelect.type": "org.openg2p.reporting.kafka.connect.transforms.TimestampSelector${dollar}Value",
      "transforms.tsSelect.ts.order": "write_date,create_date",
      "transforms.tsSelect.output.field": "@timestamp_gen"
      ```
  *   If you want to pull data from another table (which is already indexed into OpenSearch) into this table that the connector is pointing to, use the DynamicNewField transform. For example; `g2p_program_membership` contains the beneficiary list. But the demographic info of the beneficiary is present in `res_partner` table. Say you want to pull gender, and address of the beneficiary, and name of the program that the beneficiary is part of, then create two transforms like this:

      ```json
      "transforms.join01.type": "org.openg2p.reporting.kafka.connect.transforms.DynamicNewField${dollar}Value",
      "transforms.join01.input.fields": "program_id",
      "transforms.join01.output.fields": "program_name",
      "transforms.join01.es.index": "${DB_PREFIX_INDEX}.public.g2p_program",
      "transforms.join01.es.input.fields": "id",
      "transforms.join01.es.output.fields": "name",
      "transforms.join01.es.security.enabled": "${OPENSEARCH_SECURITY_ENABLED}",
      "transforms.join01.es.url": "${OPENSEARCH_URL}",
      "transforms.join01.es.username": "${OPENSEARCH_USERNAME}",
      "transforms.join01.es.password": "${OPENSEARCH_PASSWORD}",

      "transforms.join02.type": "org.openg2p.reporting.kafka.connect.transforms.DynamicNewField${dollar}Value",
      "transforms.join02.input.fields": "partner_id",
      "transforms.join02.output.fields": "beneficiary_gender,beneficiary_address",
      "transforms.join02.es.index": "${DB_PREFIX_INDEX}.public.res_partner",
      "transforms.join02.es.input.fields": "id",
      "transforms.join02.es.output.fields": "gender,address",
      "transforms.join02.es.security.enabled": "${OPENSEARCH_SECURITY_ENABLED}",
      "transforms.join02.es.url": "${OPENSEARCH_URL}",
      "transforms.join02.es.username": "${OPENSEARCH_USERNAME}",
      "transforms.join02.es.password": "${OPENSEARCH_PASSWORD}",
      ```
  * If you want to add data/fields from one connector to another index on OpenSearch, use the DynamicNewFieldInsertBack transform. For example, see the `insertBack` section in [this sample connector](https://github.com/OpenG2P/openg2p-reporting/blob/develop/scripts/social-registry/opensearch-connectors/14.reg\_id.json).
  *   If you wish to apply a [Jq filter](https://jqlang.github.io/jq/manual/) on the record, use ApplyJq transform. The current record will be replaced with the result after applying Jq. Example:

      ```json
      "transforms.jqApply1.type": "org.openg2p.reporting.kafka.connect.transforms.ApplyJq{dollar}Value",
      "transforms.jqApply1.expr": "{new_field: .payload.old_field, operation: .source.op}"
      ```
  *   The connector by default indexes all the fields from the DB into OpenSearch. If you want to exclude fields from getting indexed, they must be explicitly deleted using a transform like given below. For example PII fields like name, phone number, address, etc. As a general rule, fields that are not required for dashboards must be excluded explicitly.

      ```json
      "transforms.excludeFields.type": "org.openg2p.reporting.kafka.connect.transforms.ApplyJq{dollar}Value",
      "transforms.excludeFields.expr": "del(.name,.address)",
      ```

      * `column.exclude.list` property can also be used to remove specific columns from being indexed (Not preferred method). The disadvantage is that this excludes the fields from Kafka topics itself. If there are multiple OpenSearch Connectors, referring to the same topic, each with different data requirements, then this is not possible to control at the SINK connector side.
  *   If you wish to change the name of the Index into which data is supposed to be inserted, use RenameTopic transform. The default index name before rename will be that of the topic name given in the `topics` config field. Example :

      ```json
      "transforms.renameTopic.type": "org.openg2p.reporting.kafka.connect.transforms.RenameTopic",
      "transforms.renameTopic.topic": "res_partner_new"
      ```
  *   After configuring all the transforms, add the names of all transforms, in the order in which they have to be applied, in the `transforms` field.

      ```json
      "transforms": "keyExtId,valExt1,valExt2,tsconvert01,tsconvert02,tsSelect,excludeFields,renameTopic",
      ```

{% hint style="info" %}
Each `$` in the json file will be treated as an environment variable. Environment variables will be automatically picked up during installation. If you want to use a dollar in the file and not parse it as env variable during installation, replace your `$` with `${dollar}` .
{% endhint %}

* Example OpenSearch Connector [https://github.com/OpenG2P/openg2p-reporting/blob/develop/scripts/pbms/opensearch-connectors/30.g2p\_program\_membership.json](https://github.com/OpenG2P/openg2p-reporting/blob/develop/scripts/pbms/opensearch-connectors/30.g2p\_program\_membership.json)
* For more info on basic connector configuration, refer to [Apacha Kafka Connect](https://kafka.apache.org/documentation/#connect).
* For detailed transform configuration, refer to [Apache Kafka Connect Transformations](https://kafka.apache.org/documentation/#connect\_transforms) doc.
* For a list of all available SMTs and their configs, refer to [Reporting Kafka Connect Transforms](../kafka-connect-transform-reference.md).

#### Capturing Record History

*   If you also wish to record the history of how records of a table have changed, create a new OpenSearch connector for the same topic as given in [this section](connector-creation-guide.md#opensearch-connector-creation) and change the following properties.

    ```json
    {
        "name": "res_partner_history_${DB_PREFIX_INDEX}",
        "config": {
            ...
            "key.ignore": "true",
            ...
            "behavior.on.null.values": "ignore",
            ...
            "transforms.renameTopic.type": "org.openg2p.reporting.kafka.connect.transforms.RenameTopic",
            "transforms.renameTopic.topic": "${DB_PREFIX_INDEX}.public.res_partner_history"
        }
    }
    ```
*   Remove this line from the configuration.

    ```json
    "index.write.method": "upsert",
    ```
* With this configuration, you will have two OpenSearch connectors. One that tracks the latest data of a table. And one that tracks the history. Correspondingly you have two indexes on OpenSearch (one with `_history` and one with regular data).

## OpenSearch dashboard creation

Refer to [OpenSearch Dashboard Creation Guide](dashboards-creation-guide.md).

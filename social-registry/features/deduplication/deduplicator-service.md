---
description: WORK IN PROGRESS
---

# Deduplicator Service

This deduplicator involves the computation of duplicates based on how closely the data from a record matches with other records (fuzziness). This system also ensures that duplicates are computed as and when a new record is created or an existing record is changed so that the retrieval of duplicates becomes easier. The deduplication process can be triggered manually as well.

## Design

### Architecture

{% embed url="https://miro.com/app/board/uXjVLY7r4VY=" %}

### OpenSearch Connector

* The connector will be set up in the following way.
  * Every record in the DB table contains only one equal record on the OpenSearch index.
  * The primary key of the record in DB ("database ID") will be equal to the ID of the document on OpenSearch ("document ID").
  * If a record is deleted from DB, it will be deleted from OpenSearch also.
* On every change of a record (or insertion of records), a Kafka Connect SMT triggers the deduplicate API of the deduplicator with given fields, fuzzinesses and weightages.

{% hint style="info" %}
The term "record" means an entry in the DB table. The term "document" means an entry on OpenSearch. Because of the way the connector is set up above, the terms "entry", "record", and "document" are used interchangeably for the rest of this document, since they all mean the same thing.
{% endhint %}

### Deduplication Service

* API Service - Based on FastAPI
* Interfaces only with OpenSearch backend (No database connection required).
* Exposes API that allows triggering deduplication for a record (by document ID) in OpenSearch.
  * API inputs:
    * Fields to be considered for deduplication
    * Allowed fuzziness of each field
    * Weightage of each field
    * Threshold of score to consider a result as duplicate
  * Output:
    * Deduplication Request ID (generated).
* Exposes API to retrieve duplicates of a record (by document ID).
* Exposes API to retrieve the status of deduplication request (by deduplication request ID).
* Deduplication of a record involves the following process:
  * Get field values from the current record.
  * Run an [OpenSearch match query](https://opensearch.org/docs/latest/query-dsl/full-text/match/) (multiple field match queries are wrapped inside a [boolean must query](https://opensearch.org/docs/latest/query-dsl/compound/bool/)) with given fuzziness and weightages.
  * Receives the list of duplicates from the above query response (and picks results with scores above the given threshold). Updates the list of duplicates and their match scores against each entry from the response, including the last deduplication request ID.

---
description: >-
  The integration layer between external data sources and the OpenG2P
  Registry. Receives or fetches data, verifies who sent it, reshapes each
  record, and delivers signed batches to the Registry Partner API.
---

# Connector

## Overview

Registry data rarely originates in the registry. It comes from household survey platforms, partner ministries, agency systems, and other registries that already hold information about the people a programme serves. The **Connector** is the component that brings that data in.

It accepts data from an external system, converts each record into the shape the registry expects, and delivers it to the registry **Partner API**, where it becomes a change request and enters the normal verification and approval workflow. The registry remains the authority on what is accepted. The connector's job is to get data to its door in a form it can act on, at a rate it can absorb, and to keep an accurate account of what happened to every record along the way.

Each integration is set up as a **pipeline**. A pipeline describes one source: how its data arrives, how the connector authenticates to it, how each record is reshaped, which partner the data is attributed to, and which register it belongs in. Operators create and adjust pipelines through the **Connector Admin UI**. Adding a source does not require a code change or a redeployment.

## Design at a glance

<figure><img src="../../../.gitbook/assets/connector-service-architecture.png" alt="Connector Service architecture"><figcaption><p>Connector Service architecture</p></figcaption></figure>

Data reaches the connector by push or by fetch. Partner signatures are validated on the way in, and anything that fails is rejected at the edge. Everything received is written to the connector database. The push worker reads from that database, signs each batch with the connector key, and delivers it to the registry, where the connector signature is validated before the Partner API accepts it.

## Scope

The connector is responsible for:

* accepting data over the supported transports and verifying that it came from a trusted sender
* keeping an unaltered copy of everything it receives
* breaking a payload into the individual records it contains and tracking each one separately
* reshaping records into the registry's format and, where configured, validating them before delivery
* sending records to the registry in controlled batches and recording the outcome
* retrying what can be retried and holding the rest for an operator to review

The connector does not decide whether a record is correct, does not deduplicate against registry contents, and does not approve anything. Those are registry responsibilities and happen after delivery. The connector also does not act as a long-term store of registry data; the copies it keeps exist to support tracing, retry, and replay.

## In this section

| Page                                                     | Covers                                                                                         |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [Functional Specifications](functional-specifications.md) | Pipelines, transports, partner trust, receiving, fetching, delivery, failure handling, operations |
| [Technical Architecture](technical-architecture.md)       | Components, the database and the task queue, background workers, stored data                    |
| [Deployment](deployment.md)                               | Runtime roles, scaling, dependencies, health checks                                             |

## Related documentation

* [OpenG2P Registry](../../../products/registry/registry/README.md)
* [Registry ingestion pipeline](../../../products/registry/registry/design/ingestion-pipeline.md)
* [Registry partner APIs](../../../products/registry/registry/design/partner-apis.md)

---
description: >-
  Partners search register records through a standard wire format. DCI is the
  adapter shipped today; the search engine itself is standard-neutral.
---

# Partner Register Search

Partners look up register records through the Partner API. They do not use staff
search screens or read registry tables. The same search can return in the HTTP
response or arrive later on a WebSub callback.

### What a partner can do

* **Search now.** A synchronous call returns matching records in the response.
* **Search and wait for a callback.** An asynchronous call returns an
  acknowledgement immediately. The records arrive later on the partner's WebSub
  topic.
* **Ask in more than one way.** The DCI adapter accepts an identifier lookup, a
  filter expression, an ordered predicate list, or a closed GraphQL filter.
* **Receive a standard payload.** Hits are rendered with the register's outgoing
  template, so the partner sees the agreed external shape rather than internal
  columns.
* **Share only what consent allows.** When consent enforcement is on, the
  registry checks the consent and removes rendered fields outside the effective
  data scopes.

Signature checks and consent checks apply to both delivery modes. Business
failures stay inside the protocol body, usually with HTTP 200.

### One engine, more than one standard

The registry separates three layers:

| Layer | What it owns |
| --- | --- |
| **Standard adapter** | Request and response bodies for one interoperability profile. |
| **Core search** | Allowlisted filters, SQL, sorting, pagination, and related-register loading. |
| **Extension** | Register tables, relationships, and the outgoing templates for a domain. |

DCI is the adapter implemented today. Its request and response follow the DCI
search envelope. A later adapter, such as an UNDP-style registry search, would
decode its own body into the same core search and render through its own
outgoing data model. It would not require a second SQL engine.

Register names, searchable columns, and template documents come from the
deployment and its extension. They are not hard-coded in the core search.

### How the pieces connect

Synchronous and asynchronous DCI calls are specified in
[DCI partner search](../design/partner-register-search/dci-search.md). The
shared engine is specified in
[Core register search](../design/partner-register-search/core-search.md).

Asynchronous results use a partner WebSub topic. Topic configuration belongs to
the [Outgestion Pipeline](outgestion-pipeline.md). Hub subscription, callback
verification, and deployment belong to
[WebSub](../../../../platform/platform-services/websub/README.md).

Consent behaviour is described in
[Consent-Aware Data Sharing](consent-aware-data-sharing.md).

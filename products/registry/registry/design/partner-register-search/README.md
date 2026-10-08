---
description: >-
  How partner register search is split between a standard adapter, the core
  search engine, and the domain extension.
---

# Partner Register Search

Partner register search is a read path on the Partner API. Staff search is a
separate implementation and is not covered here.

The design keeps the database search independent of any one interoperability
standard.

```mermaid
flowchart TB
    subgraph adapters [Standard adapters]
        DCI[DCI adapter]
        Future[Future adapter]
    end

    subgraph core [openg2p-registry-core]
        Search[PartnerRegisterSearch]
        Hierarchy[Hierarchy loader]
    end

    subgraph extension [Domain extension]
        Models[Register models]
        Templates[Outgoing templates]
    end

    Partner[Partner system] --> DCI
    Partner -.-> Future
    DCI --> Search
    Future -.-> Search
    Search --> Models
    Search --> Hierarchy
    Hierarchy --> Models
    Search --> Templates
```

| Piece | Lives in | Responsibility |
| --- | --- | --- |
| DCI controller, query decoders, envelopes, signing, consent calls | Partner API | Turn a DCI body into a core search, then build the DCI response. |
| `PartnerRegisterSearch` | `openg2p-registry-core` | Compile an allowlisted clause, page the root register, and load related rows in batches. |
| Register classes and Jinja templates | Domain extension and object storage | Supply the tables and the external payload shape. |

DCI is the only adapter shipped today. `POST /dci/sync/search` and
`POST /dci/async/search` both decode into the same core search. The difference
is delivery: the synchronous call returns the envelope, and the asynchronous
call publishes it to WebSub after an acknowledgement.

A future adapter would own its own routes and body format. It would still call
`PartnerRegisterSearch` and render through the outgoing template bound to its
data model. UNDP-style search is an example of that extension point. It is not
implemented.

## Pages

{% content-ref url="core-search.md" %}
[Core register search](core-search.md)
{% endcontent-ref %}

{% content-ref url="dci-search.md" %}
[DCI partner search](dci-search.md)
{% endcontent-ref %}

The feature overview is in
[Partner Register Search](../../features/partner-register-search.md). WebSub hub
behaviour is in
[WebSub](../../../../../platform/platform-services/websub/README.md). Register
change fan-out, which shares outgoing topics but not this search path, is in
[Outgestion Pipeline](../outgestion-pipeline.md).

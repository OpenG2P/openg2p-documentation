---
description: >-
  Counting partners' use of the Exchange so they can be charged per API call:
  why audit records are not enough, how API gateways meter, and a design built
  from open-source components
---

# API Metering and Billing

{% hint style="warning" %}
**Status: proposal, not built.** Planned for [Phase 2](README.md#phase-2-farmers-partners-and-the-open-agri-network). Today the Exchange limits partners' call rates but does not count calls for charging.
{% endhint %}

## The need

The Exchange may charge partners (banks, insurers, agritechs) for the data they
get through the Composite, per API call. That needs a count of each partner's
billable calls that is complete, counted once, priced by the partner's plan, and
that the partner can check. The departments may also want to share the revenue by
how often their registry answered.

Metering is not rate limiting. A [rate limit](../composite/rate-limiting.md) stops
a partner calling too fast; it keeps no record. Metering counts what was used, for
charging and for quotas.

## Why the audit records are not enough

The Composite already sends an event to the
[Audit Manager](../../platform/platform-services/audit-manager/README.md) for each
request, and keeps its own call log for the console. Neither is fit to bill on.

| | Audit Manager events | Composite call log |
| --- | --- | --- |
| **Complete?** | No. Events are sent in the background without waiting; when 1,000 are waiting the next ones are dropped, and a failed send is only logged. A lost event is an unbilled call that cannot be proven | Kept for 90 days (`activity_retention_days`), then deleted |
| **Counted once?** | Not guaranteed | Yes, one row per request |
| **What was billable?** | Not recorded: whether the response was usable, which registries answered, whether it repeated an earlier call | Outcome and per-source status, but no billable unit |

Audit answers *who did what*. Billing needs *what to charge, counted exactly once,
and provable*. Common practice keeps the two pipelines apart and **reconciles**
one against the other: the audit records then check the bill.

## How API gateways meter

* **Gateways that package APIs as products** (Apigee, Kong, Tyk, Azure API
  Management, AWS API Gateway usage plans): each API key belongs to a plan; the
  gateway counts calls per key and per product; a separate system prices the
  counts and invoices.
* **The current open approach:** each service emits a **usage event**
  (CloudEvents) → a durable queue → a **metering** service that aggregates the
  events into meters → a **billing** service that prices the meters and invoices.
  Open-source metering: OpenMeter (Kafka and ClickHouse). Open-source billing:
  Lago or Kill Bill. Hosted equivalents: Stripe Meters, Amberflo, Moesif.

The principles they share:

1. **Meter where the business meaning is.** Here that is the Composite, not the
   Istio gateway: only the Composite knows the partner, the use case and whether
   the response was usable.
2. **Never lose an event, never count one twice.** Write the event in the same
   database transaction as the call (an *outbox* table), and key it by the request
   ID so a resend is ignored.
3. **Keep counting, pricing and invoicing apart.** Prices change without touching
   the counts; a past month can be re-priced.
4. **One meter for quotas and billing**, so what a partner is allowed and what it
   is charged never disagree.
5. **Reconcile.** Compare usage with audit records each day and flag any
   difference.

## Design

```
Composite ──(same DB transaction)──► usage outbox (Composite's Postgres)
                                          │ relay
                                          ▼
                                   queue: Kafka (commons) or NATS JetStream
                                          │
                           metering: OpenMeter (Kafka + ClickHouse)
                            │                         │
          quotas: Redis (already holds         billing: Lago
          the rate-limit buckets)              price plan per partner and use case
                                                      │
                                    invoice / monthly statement · partner usage page
          reconciliation job: usage vs Audit Manager, daily
```

| Component | Open source | Role |
| --- | --- | --- |
| **Usage outbox** | PostgreSQL (the Composite's database) | One row per request, written in the same transaction as the call log; a relay sends rows to the queue and marks them sent. Nothing is lost if the queue is down |
| **Queue** | Apache Kafka (already an option in the commons base chart) or NATS JetStream | Durable, ordered delivery to the meter |
| **Metering** | OpenMeter (with ClickHouse) | Aggregates events into meters per partner, use case and registry, per hour, day and month; de-duplicates on the event ID; serves usage queries |
| **Quotas** | Redis (commons) | Daily or monthly allowances per partner and use case, read from the meter; the same Redis as the rate-limit buckets |
| **Billing** | Lago (or Kill Bill) | Price plans, rating, invoices, credit notes; partners as customers |
| **Reconciliation** | A scheduled job | Usage counts against Audit Manager events per partner and day; differences reported |
| **Dashboards** | Superset (commons) on ClickHouse | Usage per partner, use case and registry, for the Exchange and the departments |

### The usage event

One event per partner request, in CloudEvents format, with no personal data:

```json
{
  "specversion": "1.0",
  "id": "<request_id>",
  "source": "/openg2p/agri-composite",
  "type": "org.openg2p.agri-composite.usage",
  "subject": "PARTNER_BANK_A",
  "time": "2027-03-04T10:15:02Z",
  "data": {
    "use_case": "loan-profile@1",
    "outcome": "success",
    "status": "succ",
    "billable": true,
    "units": 1,
    "sources": {"farmer-registry": "ok", "crop-sown-registry": "ok"}
  }
}
```

The `id` is the request ID: a resent event is counted once.

### What is billable (to decide)

* Only successful responses (`succ`), or partial ones too, and at what price.
* Not billable: refusals (`403`, `429`), consent denials, the Exchange's own errors.
* Repeated queries for the same farmer within a short time: billed once or each time.
* The unit: per call, or per registry answered (a call that reads two registries
  counts two).

### Price plans

A partner's plan (free allowance, price per call, per use case, monthly minimum)
is kept in the billing service, linked to the partner's ID in
[Partner Management](../../platform/platform-services/partner-management/README.md).
Assigning a plan is part of onboarding, next to the use-case policies.

### What partners and departments see

* **Partners:** a usage API and a usage page in the partner portal (calls per use
  case, per day, against their allowance); a monthly statement, signed by the
  Exchange, that ties to the audit records.
* **Departments:** how often their registry answered, per partner and use case,
  for revenue sharing and capacity planning.

## Phases

1. **First step:** the usage outbox and relay in the Composite; a daily summary per
   partner and use case in PostgreSQL; the reconciliation job; usage shown in the
   Composite console. Enough to charge by hand.
2. **Metering:** Kafka and OpenMeter; quotas read from the meter; the partner usage
   API and portal page.
3. **Billing:** Lago with price plans and invoices; revenue-share reports for the
   departments.

## Open questions

* What is billable (above), and who sets the prices: the Exchange, or each
  department for its own registry.
* Whether partners pay the Exchange only, which then settles with the departments.
* Retention of usage and invoices (finance rules), separate from the call log's 90
  days.

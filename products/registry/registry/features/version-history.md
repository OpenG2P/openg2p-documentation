# Version History

OpenG2P Registry keeps an append-only **version history** of every approved change to primary and child register records. Staff can open a record’s Version History view to see what changed on a given date, which change request committed the change, and how the record evolved over time - supporting grievance redressal, audit, and point-in-time investigation.

{% hint style="info" %}
Version history stores **record snapshots** (and document promotion events). It is not the same as workflow audit (who verified or approved a change request) or platform write-operation audit. See Audit-ability & Trace-ability for the workflow trail.
{% endhint %}

### What is captured

| Artefact                 | What is stored                                                          | When                                                            |
| ------------------------ | ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| Register record versions | Snapshot rows in per-register history tables (`g2p_register_history_*`) | Change request approval, or intake form ingest into live tables |
| Supporting documents     | Promotion events in `g2p_register_document_history`                     | When pending attachments become live section documents          |
| Computed scores          | Separate score history table                                            | When a score compute job completes                              |

Program application registers do not participate in register version history.

### Capabilities

* **Full ledger of approved states** - previous versions remain queryable after later edits or child deletes (subject-scoped discovery).
* **Linked to change requests** - staff Version History navigates by date and change request; each CR-backed version retains initiator and approver metadata.
* **Intake-aware** - first creates via intake also write history, keyed by submission id when there is no change request.
* **Document promotions audited** - each promotion of a supporting document to a live section is recorded separately from the binary object catalog.
* **Permission-gated** - viewing version history requires `registerHistory:view`.

### Staff experience

On a register record in the Staff Portal:

1. Open **Version History**.
2. Choose a date that has committed changes.
3. Review sections and change requests for that date.
4. Open a change request to see the approved payload and approval context.

### How it relates to change management

All registry mutations still flow through Change Management & Approval Workflow (or the intake approval path). Version history is the **post-approval** ledger: the shadow / change-request stage holds the proposed state; only after approval is a history snapshot written and the live register updated.

# Change management & Approval workflow

All data modifications in the registry are processed through a centrally managed change request workflow. The Base Registry enforces that no record, including newly created records, can be introduced or modified without undergoing an approval process. When a user or system initiates a change, a new change request is created along with supporting evidence. The change request follows a structured workflow that includes domain validations, deduplication, manual verifications, and manual approval before the changes are committed to the registry.

#### Shadow Write Model

Changes are staged in a unified change log (shadow) table before being applied to the master registry. The system maintains a clear separation between the “proposed state” and the “approved state” of a registry record. Only after the change request is approved does the Base Registry write the updated values to the main registry table, ensuring strict governance around data modification. The shadow write model enables visibility into pending changes, concurrent approvals, and auditability of the decision-making process.

#### Versioned Record History

Every change that is approved results in a new entry in the registry’s version history table. Version history captures the state of the change record at the time of approval, the timestamp, and the actors involved in verification and approval. This provides a complete historical ledger of the registry’s evolution across time while ensuring that previous states remain accessible for audits, reporting, and roll-back scenarios. Version history is implemented at a **per-register level**, allowing records to maintain an independent state timeline.

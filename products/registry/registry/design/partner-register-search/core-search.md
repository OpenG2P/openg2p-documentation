---
description: >-
  Standard-neutral partner search in registry core: allowlisted columns, SQL
  compilation, pagination, and batched related-register loading.
---

# Core Register Search

`PartnerRegisterSearch` in `openg2p-registry-core` executes a search that does
not know about DCI, GraphQL, or any other wire format. An adapter decodes its
request into a `RegisterSearch` and, after the query, renders the rows.

A `RegisterSearch` contains:

* Register mnemonic
* Boolean filter clause
* Ordered sort keys
* Page number and page size

`search_batch` then:

1. Resolves the register definition and the SQLAlchemy model from the loaded extension.
2. Compiles the clause into SQLAlchemy conditions.
3. Counts matching root records.
4. Applies sort, offset, and limit.
5. Loads related records for that page in batches.
6. Returns the page and the full match count.

The adapter decides which columns may be named, how identifier types map to
columns, and how the result is wrapped. DCI's choices are in
[DCI partner search](dci-search.md).

## Allowlist and coercion

The adapter passes an allowlist of column names. The compiler rejects any
filter or sort field outside that list before it touches the model. The
allowlist does not declare types. Types come from the SQLAlchemy column.

Values are coerced to the column type:

* ISO dates and datetimes for date columns
* Integers and floats for numeric columns
* Booleans for boolean columns
* Strings for text columns

Unknown fields and failed coercion become an adapter-level invalid-criteria
error. They are not returned as database errors.

Dotted paths are not supported. A searchable attribute must be a concrete
column on the selected register model.

`search_text` is a special text column. Equality and contains use
case-insensitive substring matching. Starts-with and ends-with use prefix and
suffix matching. List operators are not valid on `search_text`.

## Default record status

When the clause does not mention `record_status`, the compiler adds
`record_status = ACTIVE`. An explicit status predicate replaces that default.

Related registers are loaded with `record_status = ACTIVE` when that column
exists. Search predicates are not copied onto related registers.

## Sorting and pagination

Every requested sort key is applied in order. `internal_record_id ASC` is
appended unless the caller already sorted by it.

When the adapter supplies no sort, the default is:

1. `last_approved_at DESC`, when the column exists
2. `internal_record_id ASC`, when the column exists

Pagination applies only to the root register. The page number and page size
must be at least 1. There is no server-side maximum page size. The returned
count is the number of matching root records, not the length of the page.
Related rows are loaded only for the root rows on the current page.

How those counts appear in a DCI header is specified in
[DCI partner search](dci-search.md).

## Batched hierarchy loading

Outgoing templates often need records around the searched row. A Farmer
template may need household members, land, crops, livestock, and inputs.
Loading those one row at a time would create an N+1 query pattern.

The loader plans the registers once:

1. Descendants of the searched register.
2. Parent registers, walking upward.
3. From each parent, sibling registers and their descendants.
4. The searched register is not attached again under a parent, which avoids cycles.

Each step is one `SELECT ... WHERE id IN (...)` per related register.
Identifier lists are chunked at 1,000 values. Query count follows the number of
related register types, not the number of root rows.

Stitched dictionaries use the snake-case register mnemonic:

* A child register is a list.
* A parent register is one object.

The domain extension defines which registers exist and how they relate. Core
does not hard-code a Farmer or Household graph.

## Rendering boundary

Core returns the stitched page. The adapter selects the outgoing template:

1. Resolve the data model for the adapter's standard.
2. Find the `OutgoingTemplate` for that register and data model.
3. Load the Jinja document from object storage.
4. Render each stitched root record.
5. Let the adapter apply consent field clamping and place the object in its response.

The DCI adapter uses the data model mnemonic `DCI` and writes the rendered
objects to `data.reg_records`. Another standard would bind its own data model
and response field. A missing template or unreadable document fails after a
successful SQL search.

## Limitations of the core engine

* No dotted or nested column paths.
* No result-size cap.
* Filters and pagination apply to the root register only.
* Staff search does not use this engine.

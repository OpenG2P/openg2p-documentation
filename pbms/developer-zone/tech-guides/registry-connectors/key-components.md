# Key Components

The `RegistryInterface` defines methods for summary, eligibility and entitlement computation, registry access, and query construction. See the attached Key details of the same are mentioned below

### Computations

**`get_summary`**

**Purpose:** Asynchronously retrieves summary statistics for a given beneficiary list.\
Used primarily in background tasks or async workflows.

**Arguments:**

* `beneficiary_list_id (str)`: The ID of the beneficiary list to summarize.
* `bg_task_session (AsyncSession)`: Async SQLAlchemy session for background operations.
* `formated (bool, optional)`: Whether to return formatted summary data. Defaults to `False`.

**Returns:**\
`BeneficiaryListSummaryPayload` — Contains computed summary metrics for the list.

***

**`get_summary_sync`**

**Purpose:** Retrieves summary statistics synchronously for a beneficiary list (non-async execution).

**Arguments:**

* `beneficiary_list_id (str)`: The beneficiary list identifier.
* `bg_task_session (Session)`: SQLAlchemy synchronous session.

**Returns:** `BeneficiaryListSummaryPayload`

***

**`compute_eligibility_statistics`**

**Purpose:** Computes and updates eligibility statistics for a given list of beneficiaries.

**Arguments:**

* `beneficiary_list_details (List[BeneficiaryListDetails])`: Details of beneficiaries in the list.
* `base_summary`: Type or class of base\_summary - e.g., `BeneficiaryListSummary` or custom model implementation
* `sr_session (Session)`: Session connected to the source registry database.
* `bg_task_session (Session)`: Session connected to the PBMS background task database.

**Returns:** None - Updates the summary table in place.

***

**`compute_entitlement_statistics`**

**Purpose:** Calculates entitlement statistics for the given beneficiary list and updates the relevant fields.

**Arguments:**

* `beneficiary_list_id (str)`: ID of the beneficiary list.
* `bg_task_session (Session)`: Background task DB session.
* `sr_session (Session)`: Registry DB session.

**Returns:** None - Updates the computed statistics in database

***

### Registry Methods

**`get_registrants_by_ids`**

**Purpose:** Fetches registrant records from the registry database based on their IDs.

**Arguments:**

* `registrant_ids (List[str])`: List of registrant IDs to fetch.
* `sr_session (Session)`: Registry database session.

**Returns:** `List[G2PRegistry]` - List of registry entries.

***

**`get_is_registant_entitled`**

**Purpose:** Checks whether a specific registrant is entitled based on a dynamically generated SQL query.

**Arguments:**

* `registrant_id (str)`: ID of the registrant.
* `sql_query (str)`: SQL query representing eligibility rules.
* `sr_session (Session)`: Registry session.

**Returns:** `bool` - `True` if entitled, otherwise `False`.

***

**`get_entitlement_multiplier`**

**Purpose:** Retrieves the multiplier value used in entitlement computation for a specific registrant.

**Arguments:**

* `multiplier (str)`: Field or SQL expression to compute multiplier.
* `registrant_id (str)`: ID of the registrant.
* `sr_session (Session)`: Registry session.

**Returns:** `int` - The computed multiplier value.

***

**`search_beneficiaries`**

**Purpose:** Searches for beneficiaries based on a search query and pagination parameters.

**Arguments:**

* `bg_task_session (AsyncSession)`: Async background session.
* `sr_session (AsyncSession)`: Async registry session.
* `beneficiary_list_id (str)`: Beneficiary list identifier.
* `target_registry (str)`: Registry name or identifier.
* `search_query`: _\[Placeholder: Expected structure or type, e.g., dict or SQL clause]_
* `page (int)`: Page number for pagination (default: `1`).
* `page_size (int)`: Results per page (default: `10`).
* `order_by (str)`: Sorting order (default: `"id asc"`).

**Returns:** `BeneficiarySearchResponsePayload` - Paginated list of beneficiaries matching the query.

***

### SQL Query Constructors (Utility Methods)

These helper methods generate SQL Alchemy-compatible `TextClause` objects to perform parameterized queries on registry data.&#x20;

{% hint style="info" %}
Custom implementations can directly use these methods by passing `target_registry`, given that table naming conventions are followed for registries.
{% endhint %}

**`construct_multiplier_sql_query`**

**Purpose:** Constructs a query to retrieve multiplier values for entitlement calculations.

**Arguments:**

* `multiplier (str)`: Column name representing the multiplier.
* `target_registry (str)`: Registry name.

**Returns:** `TextClause` - SQL query for retrieving multiplier values.

***

**`construct_beneficiary_search_sql_query`**

**Purpose:** Builds a SQL query for paginated beneficiary search with dynamic filters.

**Arguments:**

* `registrant_ids (List[str])`: List of registrant IDs to include.
* `target_registry (str)`: Target registry table.
* `where_clause (str)`: Additional SQL conditions.
* `order_by (str)`: Sorting criteria.
* `page_size (int)`: Number of records per page.
* `page (int)`: Page number.

**Returns:** `Tuple[TextClause, Dict[str, Any]]` - Query and its parameters.

***

**`construct_beneficiary_search_count_sql_query`**

**Purpose:** Builds a SQL query to count total search results (for pagination).

**Arguments:**

* `registrant_ids (List[str])`: List of registrant IDs.
* `target_registry (str)`: Registry table name.
* `where_clause (str)`: SQL filtering conditions.

**Returns:** `Tuple[TextClause, Dict[str, Any]]` - Count query and parameters.

***

**`construct_get_is_registrant_entitled_sql_query`**

**Purpose:** Generates a SQL query to check if a registrant meets entitlement conditions.

**Arguments:**

* `registrant_id (str)`: The registrant’s unique ID.
* `target_registry (str)`: Registry name.
* `sql_query (str)`: Base eligibility SQL.

**Returns:** `TextClause` - SQL query ready for execution with parameters.

***

### Data Models, Schemas and Dependencies

To implement this interface, the following models and schemas are typically imported from the G2P [PBMS](https://github.com/OpenG2P/openg2p-pbms-bg-tasks/tree/3.0/openg2p-pbms-models) and [PBMS Background Task](https://github.com/OpenG2P/openg2p-pbms-bg-tasks/tree/3.0/openg2p-bg-task-models) ecosystem:

* `G2PRegistry`: Core registry ORM model.
* `BeneficiaryListDetails`: Details of beneficiaries linked to lists.
* `BeneficiaryListSummaryPayload`: Schema for summary statistics.
* `BeneficiarySearchResponsePayload`: Schema for search results.
* `Disbursement`: Disbursement data schema.

_Additional dependencies include `sqlalchemy`, `sqlalchemy.ext.asyncio`, and `abc` for abstract base class definition._

{% hint style="info" %}
New data models and schemas created during custom implementation are expected to inherit their corresponding parent model/schema
{% endhint %}

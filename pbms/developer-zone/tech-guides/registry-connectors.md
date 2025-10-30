---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Registry Connector

This guide provides details on implementing the [Registry Connectors Interface](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions) for integration with PBMS Background Tasks.

## Overview

The `RegistryInterface` defines a standardized contract for interacting with various **G2P Registries** within the PBMS. It ensures consistent behavior across different registry integrations, including eligibility checks, summary computation, entitlement processing, and beneficiary search functionalities.

Custom implementations of this interface allow developers to integrate new registry types (for example, `farmer`, `student`, or `worker` registries) without modifying the PBMS core logic.

**Interface Code:** [Registry Interface](https://app.gitbook.com/u/21UJpMbIpqP7PKcbN5AOu80ESpo1) in OpenG2P PBMS Background Tasks Extensions\
**Example Implementation:** [`farmer` Implementation](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions/blob/3.0/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/registry_farmer.py), [`student` Implementation](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions/blob/3.0/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/registry_student.py)

## Key components of Registry Connector Interface

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

## Data Models, Schemas and Dependencies

To implement this interface, the following models and schemas are typically imported from the G2P [PBMS](https://app.gitbook.com/u/21UJpMbIpqP7PKcbN5AOu80ESpo1) and [PBMS Background Task](https://github.com/OpenG2P/openg2p-pbms-bg-tasks/tree/3.0/openg2p-bg-task-models/src/openg2p_bg_task_models) ecosystem:

* `G2PRegistry`: Core registry ORM model.
* `BeneficiaryListDetails`: Details of beneficiaries linked to lists.
* `BeneficiaryListSummaryPayload`: Schema for summary statistics.
* `BeneficiarySearchResponsePayload`: Schema for search results.
* `Disbursement`: Disbursement data schema.

_Additional dependencies include `sqlalchemy`, `sqlalchemy.ext.asyncio`, and `abc` for abstract base class definition._

{% hint style="info" %}
New data models and schemas created during custom implementation are expected to inherit their corresponding parent model/schema
{% endhint %}

## Example Implementation Workflow

The [`RegistryFarmer` class](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions/blob/3.0/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/registry_farmer.py) demonstrates a **custom implementation** of the `RegistryInterface`, tailored for integrating with a [**Farmer Registry**](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions/blob/3.0/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/models/registry_farmer.py) data source.

Below is the typical workflow for building a similar registry connector:

### Define a Custom Registry Class and Update Factory

Create a class (e.g., `RegistryFarmer`) that **inherits from** `RegistryInterface`.\
This ensures the connector implements all abstract methods required by the PBMS framework — including summaries, searches, and entitlement computations.

```python
class RegistryFarmer(RegistryInterface):
```

Update the `/factory/registry_factory.py` file to include this new registry class

```python
class RegistryFactory:
    """Get the appropriate summary computation class based on the registrant type"""

    @staticmethod
    def get_registry_class(
        target_registry,
    ) -> RegistryInterface:
        if target_registry == G2PRegistryType.FARMER.value:
            return RegistryFarmer()

        # add multiple interfaces using elif blocks 

        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
```

### Create Custom Schema (`/schemas`) and Model Definitions (`/models`)

Define a pydantic schema to structure registry-specific summary data. Each registry schema extends the base `BeneficiaryListSummaryPayload` to ensure the payload integrates seamlessly with existing response models.

```python
# /schemas/beneficiary_list_summary_farmer.py
from typing import Optional
from pydantic import BaseModel
from .beneficiary_list_summary import BeneficiaryListSummaryPayload

class BeneficiaryListSummaryFarmer(BaseModel):
    # ... registry-specific stats ...
    # computaion logic is expected in registry connector implementation

class BeneficiaryListSummaryFarmerPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryFarmer
```

Extend the base SQLAlchemy model `BeneficiaryListSummary` to persist registry-specific statistics. The inheritance ensures all common fields (e.g., `beneficiary_list_id`, timestamps) are available automatically.

```python
# /models/beneficiary_list_summary_farmer.py
from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import mapped_column

class BeneficiaryListSummaryFarmer(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_farmer"

    land_holding_mean = mapped_column(Float, default=0)
    annual_income_mean = mapped_column(Float, default=0)
    average_entitlement_female = mapped_column(JSON, nullable=True)
    average_entitlement_male = mapped_column(JSON, nullable=True)
    # ... other numeric/statistical columns ...
    # computaion logic is expected in registry connector implementation
```

After new model creation you are expected to update the migration script in [`migrate.py`](https://github.com/OpenG2P/openg2p-pbms-bg-tasks-extensions/blob/3.0/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/migrate.py) with the new models.

Implement the computation and registry methods, you can use the SQL utility methods provided in the interface by passing `target_registry` string to get a `TextClause` SQL query. Refer the Code Anatomy for Registry Connector Interface below to populate your custom interface with the current interface template.

<table data-full-width="false"><thead><tr><th>Method Name</th><th width="82">Type</th><th>Purpose</th><th width="148">Key Arguments</th><th>Returns</th><th>Implementation Notes</th></tr></thead><tbody><tr><td><code>get_summary</code></td><td>Async</td><td>Retrieves summary statistics for a given beneficiary list asynchronously.</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: AsyncSession</code>, <code>formated: bool</code></td><td><code>BeneficiaryListSummaryPayload</code></td><td>Used in API calls; fetches formatted summary metrics from summary table.</td></tr><tr><td><code>get_summary_sync</code></td><td>Sync</td><td>Same as <code>get_summary</code> but executed synchronously (for Celery or background tasks).</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: Session</code></td><td><code>BeneficiaryListSummaryPayload</code></td><td>Ideal for heavy computation where async isn’t needed.</td></tr><tr><td><code>compute_eligibility_statistics</code></td><td>Sync</td><td>Computes eligibility-based summary metrics for beneficiaries.</td><td><code>beneficiary_list_details: List[BeneficiaryListDetails]</code>, <code>base_summary</code>, <code>sr_session</code>, <code>bg_task_session</code></td><td>None</td><td>Uses NumPy for percentile and mean computations; updates summary model.</td></tr><tr><td><code>compute_entitlement_statistics</code></td><td>Sync</td><td>Computes entitlement statistics (e.g., payment distribution by gender).</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: Session</code>, <code>sr_session: Session</code></td><td>None</td><td>Groups entitlements by <code>benefit_code_id</code>; calculates mean, Q1, Q2, Q3.</td></tr><tr><td><code>get_registrants_by_ids</code></td><td>Sync</td><td>Fetches registrant data from the registry database.</td><td><code>registrant_ids: List[str]</code>, <code>sr_session: Session</code></td><td><code>List[G2PRegistry]</code></td><td>Uses chunked loading (<code>yield_per(500)</code>) for performance on large datasets.</td></tr><tr><td><code>get_is_registant_entitled</code></td><td>Sync</td><td>Checks if a registrant satisfies entitlement criteria using a SQL query.</td><td><code>registrant_id: str</code>, <code>sql_query: str</code>, <code>sr_session: Session</code></td><td><code>bool</code></td><td>Constructs validated dynamic SQL using <code>construct_get_is_registrant_entitled_sql_query</code>.</td></tr><tr><td><code>get_entitlement_multiplier</code></td><td>Sync</td><td>Retrieves multiplier value for entitlement scaling.</td><td><code>multiplier: str</code>, <code>registrant_id: str</code>, <code>sr_session: Session</code></td><td><code>int</code></td><td>Executes a SQL query; defaults to <code>1</code> if not found or multiplier is <code>"none"</code>.</td></tr><tr><td><code>search_beneficiaries</code></td><td>Async</td><td>Performs paginated and filtered beneficiary searches.</td><td><code>bg_task_session: AsyncSession</code>, <code>sr_session: AsyncSession</code>, <code>beneficiary_list_id: str</code>, <code>target_registry: str</code>, <code>search_query</code>, <code>page</code>, <code>page_size</code>, <code>order_by</code></td><td><code>BeneficiarySearchResponsePayload</code></td><td>Builds dynamic SQL queries with <code>construct_beneficiary_search_sql_query</code> and applies caching.</td></tr><tr><td><code>construct_multiplier_sql_query</code></td><td>Utility</td><td>Builds SQL query to fetch multiplier column from registry table.</td><td><code>multiplier: str</code>, <code>target_registry: str</code></td><td><code>TextClause</code></td><td>Returns a prepared SQLAlchemy <code>text()</code> object.</td></tr><tr><td><code>construct_beneficiary_search_sql_query</code></td><td>Utility</td><td>Constructs SQL for paginated search with WHERE and ORDER BY.</td><td><code>registrant_ids: List[str]</code>, <code>target_registry: str</code>, <code>where_clause: str</code>, <code>order_by: str</code>, <code>page_size: int</code>, <code>page: int</code></td><td><code>(TextClause, Dict[str, Any])</code></td><td>Replaces curly quotes in filters; dynamically injects pagination params.</td></tr><tr><td><code>construct_beneficiary_search_count_sql_query</code></td><td>Utility</td><td>Builds SQL query to count total search results.</td><td><code>registrant_ids: List[str]</code>, <code>target_registry: str</code>, <code>where_clause: str</code></td><td><code>(TextClause, Dict[str, Any])</code></td><td>Mirrors main query but replaces <code>SELECT *</code> with <code>SELECT COUNT(*)</code>.</td></tr><tr><td><code>construct_get_is_registrant_entitled_sql_query</code></td><td>Utility</td><td>Prepares validated entitlement SQL query with a dynamic <code>WHERE</code> clause.</td><td><code>registrant_id: str</code>, <code>target_registry: str</code>, <code>sql_query: str</code></td><td><code>TextClause</code></td><td>Validates SQL starts with <code>SELECT</code>; appends correct registry table reference.</td></tr></tbody></table>

After pushing this custom adapter code to GitHub, you can proceed to create a custom Docker image for your setup. Simply follow the existing [Docker creation guide](../pbms-docker.md#background-tasks) for **PBMS Background Tasks**, updating the path for the extensions package.

This approach ensures your environment remains consistent with the PBMS deployment standards while allowing flexibility to integrate your custom logic and components seamlessly.

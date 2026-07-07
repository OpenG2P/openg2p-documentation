# Example Implementation Workflow

The [`RegistryFarmer` class](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/registry_farmer.py) demonstrates a **custom implementation** of the `RegistryInterface`, tailored for integrating with a [**Farmer Registry**](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/models/registry_farmer.py) data source.

Below is the typical workflow for building a similar registry connector:

## Define a Custom Registry Class and Update Factory

Create a class (e.g., `RegistryFarmer`) that **inherits from** `RegistryInterface`.\
This ensures the connector implements all abstract methods required by the PBMS framework — including summaries, searches, and entitlement computations.

```python
# /computations/registry_farmer.py
class RegistryFarmer(RegistryInterface):
```

Update the `/factory/registry_factory.py` file to include this new registry class

<pre class="language-python"><code class="lang-python"># /factory/registry_factory.py
class RegistryFactory:
    """Get the appropriate summary computation class based on the registrant type"""

    @staticmethod
    def get_registry_class(
        target_registry,
    ) -> RegistryInterface:
<strong>        if target_registry == G2PRegistryType.FARMER.value:
</strong><strong>            return RegistryFarmer()
</strong>
        # add multiple interfaces using elif blocks 

        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
</code></pre>

## Create Custom Schema (`/schemas`) and Model Definitions (`/models`)

Define a pydantic schema to structure registry-specific summary data. Each registry schema extends its base schema to ensure the payload integrates seamlessly with existing response models.

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

After new model creation you are expected to update the migration script in [`migrate.py`](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/migrate.py) with the new models.

Similarly, `/models` and `/schema` should also be populated by adding the registry views created as models and related payloads. These models will be used in lookup from the registry database. [`registry_type.py`](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/models/registry_type.py) should house all the target model mappings.

<pre class="language-python"><code class="lang-python"># /schema/registry_farmer.py
<strong>class G2PFarmerRegistryPayload(G2PRegistryPayload):
</strong><strong>
</strong>    ## ... add fields from registry view defined ...
</code></pre>

<pre class="language-python"><code class="lang-python"># /models/registry_farmer.py
<strong>class G2PFarmerRegistry(G2PRegistry):
</strong>    __tablename__ = "g2p_register_farmer"    # table name in registry view

    ## ... add fields from registry view defined ...
</code></pre>

Implement the computation and registry methods, you can use the SQL utility methods provided in the interface by passing `target_registry` string to get a `TextClause` SQL query. Refer the Code Anatomy for Registry Connector Interface below to populate your custom interface with the current interface template.

<table data-full-width="false"><thead><tr><th>Method Name</th><th width="82">Type</th><th>Purpose</th><th width="148">Key Arguments</th><th>Returns</th><th>Implementation Notes</th></tr></thead><tbody><tr><td><code>get_summary</code></td><td>Async</td><td>Retrieves summary statistics for a given beneficiary list asynchronously.</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: AsyncSession</code>, <code>formated: bool</code></td><td><code>BeneficiaryListSummaryPayload</code></td><td>Used in API calls; fetches formatted summary metrics from summary table.</td></tr><tr><td><code>get_summary_sync</code></td><td>Sync</td><td>Same as <code>get_summary</code> but executed synchronously (for Celery or background tasks).</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: Session</code></td><td><code>BeneficiaryListSummaryPayload</code></td><td>Ideal for heavy computation where async isn’t needed.</td></tr><tr><td><code>compute_eligibility_statistics</code></td><td>Sync</td><td>Computes eligibility-based summary metrics for beneficiaries.</td><td><code>beneficiary_list_details: List[BeneficiaryListDetails]</code>, <code>base_summary</code>, <code>sr_session</code>, <code>bg_task_session</code></td><td>None</td><td>Uses NumPy for percentile and mean computations; updates summary model.</td></tr><tr><td><code>compute_entitlement_statistics</code></td><td>Sync</td><td>Computes entitlement statistics (e.g., payment distribution by gender).</td><td><code>beneficiary_list_id: str</code>, <code>bg_task_session: Session</code>, <code>sr_session: Session</code></td><td>None</td><td>Groups entitlements by <code>benefit_code_id</code>; calculates mean, Q1, Q2, Q3.</td></tr><tr><td><code>get_registrants_by_ids</code></td><td>Sync</td><td>Fetches registrant data from the registry database.</td><td><code>registrant_ids: List[str]</code>, <code>sr_session: Session</code></td><td><code>List[G2PRegistry]</code></td><td>Uses chunked loading (<code>yield_per(500)</code>) for performance on large datasets.</td></tr><tr><td><code>get_is_registant_entitled</code></td><td>Sync</td><td>Checks if a registrant satisfies entitlement criteria using a SQL query.</td><td><code>registrant_id: str</code>, <code>sql_query: str</code>, <code>sr_session: Session</code></td><td><code>bool</code></td><td>Constructs validated dynamic SQL using <code>construct_get_is_registrant_entitled_sql_query</code>.</td></tr><tr><td><code>get_entitlement_multiplier</code></td><td>Sync</td><td>Retrieves multiplier value for entitlement scaling.</td><td><code>multiplier: str</code>, <code>registrant_id: str</code>, <code>sr_session: Session</code></td><td><code>int</code></td><td>Executes a SQL query; defaults to <code>1</code> if not found or multiplier is <code>"none"</code>.</td></tr><tr><td><code>search_beneficiaries</code></td><td>Async</td><td>Performs paginated and filtered beneficiary searches.</td><td><code>bg_task_session: AsyncSession</code>, <code>sr_session: AsyncSession</code>, <code>beneficiary_list_id: str</code>, <code>target_registry: str</code>, <code>search_query</code>, <code>page</code>, <code>page_size</code>, <code>order_by</code></td><td><code>BeneficiarySearchResponsePayload</code></td><td>Builds dynamic SQL queries with <code>construct_beneficiary_search_sql_query</code> and applies caching.</td></tr><tr><td><code>construct_multiplier_sql_query</code></td><td>Utility</td><td>Builds SQL query to fetch multiplier column from registry table.</td><td><code>multiplier: str</code>, <code>target_registry: str</code></td><td><code>TextClause</code></td><td>Returns a prepared SQLAlchemy <code>text()</code> object.</td></tr><tr><td><code>construct_beneficiary_search_sql_query</code></td><td>Utility</td><td>Constructs SQL for paginated search with WHERE and ORDER BY.</td><td><code>registrant_ids: List[str]</code>, <code>target_registry: str</code>, <code>where_clause: str</code>, <code>order_by: str</code>, <code>page_size: int</code>, <code>page: int</code></td><td><code>(TextClause, Dict[str, Any])</code></td><td>Replaces curly quotes in filters; dynamically injects pagination params.</td></tr><tr><td><code>construct_beneficiary_search_count_sql_query</code></td><td>Utility</td><td>Builds SQL query to count total search results.</td><td><code>registrant_ids: List[str]</code>, <code>target_registry: str</code>, <code>where_clause: str</code></td><td><code>(TextClause, Dict[str, Any])</code></td><td>Mirrors main query but replaces <code>SELECT *</code> with <code>SELECT COUNT(*)</code>.</td></tr><tr><td><code>construct_get_is_registrant_entitled_sql_query</code></td><td>Utility</td><td>Prepares validated entitlement SQL query with a dynamic <code>WHERE</code> clause.</td><td><code>registrant_id: str</code>, <code>target_registry: str</code>, <code>sql_query: str</code></td><td><code>TextClause</code></td><td>Validates SQL starts with <code>SELECT</code>; appends correct registry table reference.</td></tr></tbody></table>

After pushing this custom adapter code to GitHub, you can proceed to create a custom Docker image for your setup. Simply follow the existing [Docker creation guide](../../pbms-docker.md#background-tasks) for **PBMS Background Tasks**, updating the path for the extensions package.

This approach ensures your environment remains consistent with the PBMS deployment standards while allowing flexibility to integrate your custom logic and components seamlessly.

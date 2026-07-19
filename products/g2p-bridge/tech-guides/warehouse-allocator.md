---
description: Design & Implementation
---

# Warehouse allocator

{% hint style="info" %}
Part of writing a connector — for the end-to-end flow (implement the interface → extend the published Bridge Docker image → configure → deploy) see [How to write your own connector](../design-specifications/connectors-and-extensibility.md).
{% endhint %}

### Module Information

* **Module Name**: `openg2p-g2p-bridge-warehouse-allocator`
* **Location**: `/openg2p-g2p-bridge-warehouse-allocator/`
* **Primary Implementation**: `WarehouseAllocatorRefImpl`

***

### Interface Definition

**File**: `interface/warehouse_allocator_interface.py`

```python
class WarehouseAllocator(BaseService):
    def allocate_warehouse(
        self,
        large_geo_list: List[Dict],
        benefit_code_id: str,
        program_id: str,
    ) -> List[Dict]:
        """
        Allocates warehouses to geographic zones.
        
        Args:
            large_geo_list: List of dicts with keys:
                - batch_control_geo_id
                - administrative_zone_id_large  
                - large_geo_Mnemonic (appears to be typo in actual code)
                
            benefit_code_id: str - Benefit code identifier
            program_id: str - Program identifier
        
        Returns:
            List of dicts with warehouse allocation info for each geo.
        """
        raise NotImplementedError()
```

#### Key Differences from Agency Allocator

* Uses **large\_geo\_list** instead of small\_geo\_list
* Takes **benefit\_code\_id and program\_id as strings**, not as Dict objects
* Allocates to warehouses (not agencies)

***

### Reference Implementation: WarehouseAllocatorRefImpl

**File**: `implementations/warehouse_allocator_ref_impl.py`

#### Database Models Used

* `G2PWarehouse` - Warehouse master data
* `G2PWarehouses ProgramBenefitCode` - Authorization matrix (which warehouses handle which programs/benefits)
* `G2PAdministrativeAreaLargeWarehouseRel` - Geographic zone (large) to warehouse mapping

#### Algorithm

Similar to Agency Allocator but for large geographic zones:

```
1. Get all warehouses authorized for the given program + benefit_code
   Query: G2PWarehouseProgramBenefitCode where program_id and benefit_code_id match
   Result: Set of authorized warehouse IDs
   
2. For each large geographic zone:
   a. Get all warehouses serving that large geographic zone
      Query: G2PAdministrativeAreaLargeWarehouseRel where large geo ID matches
      Result: Set of geographic warehouse IDs
      
   b. Intersect the two sets
      Result: Eligible warehouses = authorized AND geographic coverage
      
   c. If eligible warehouses found:
      - Randomly select one warehouse
      - Fetch warehouse details from G2PWarehouse table
      - Fetch additional attributes from G2PWarehouseProgramBenefitCode
      - Return allocation record
      
   d. If no eligible warehouses:
      - Log warning/info message
      - Continue to next geo (does NOT raise exception)
```

#### Key Characteristics

1. **Random Selection**: Uses Python's `random.choice()` to select from eligible warehouses
2. **No Exception on Empty**: Logs info message if no eligible warehouse, continues processing
3. **Database Engines**: Uses PBMS database connection
   * `db_engine_pbms` - PBMS database for warehouse master data
4. **Logging**: Uses Python logging with logger name "warehouse\_allocator\_ref\_impl"

#### Response Format

The exact return structure is partially visible but includes:

* batch\_control\_geo\_id
* administrative\_zone\_id\_large
* warehouse-related information (exact fields from code review)

***

### Factory Pattern

**File**: `factory/warehouse_allocator_factory.py`

```python
class WarehouseAllocatorFactory(BaseService):
    @staticmethod
    def get_warehouse_allocator() -> WarehouseAllocator:
        return WarehouseAllocatorRefImpl.get_component()
```

***

### Database Dependencies

#### Tables Required

1. **G2PWarehouse**
   * Similar structure to G2PAgency but for warehouses
2. **G2PWarehouseProgramBenefitCode**
   * Fields: warehouse\_id, program\_id, benefit\_code\_id, additional\_info (JSON)
3. **G2PAdministrativeAreaLargeWarehouseRel**
   * Fields: g2p\_administrative\_area\_large\_id, g2p\_warehouse\_id
   * Note: Uses LARGE geographic zones (not small like agency allocator)

#### Connection

* Engine key: `db_engine_pbms`
* Uses SQLAlchemy sessionmaker with expire\_on\_commit=False

***

### Key Differences from Agency Allocator

| Aspect              | Agency Allocator                  | Warehouse Allocator           |
| ------------------- | --------------------------------- | ----------------------------- |
| Geographic Level    | **small\_geo\_list**              | **large\_geo\_list**          |
| Benefit/Program     | Dict objects with id/mnemonic     | String IDs directly           |
| Exception on Empty  | Raises exception                  | Logs and continues            |
| Master Data         | G2PAgency                         | G2PWarehouse                  |
| Geographic Relation | Small area to agency              | Large area to warehouse       |
| Use Case            | Operational agencies for payments | Physical distribution centers |

***

### Logging

All logging uses logger name: `warehouse_allocator_ref_impl`

* INFO: Warehouse allocation start, intersections found
* WARNING: When no warehouse found for a geo (but continues processing)

***

### Error Handling

* **No Exception Raised**: Unlike Agency Allocator, does NOT raise exception if no warehouse found
* **Logs and Continues**: For geos with no eligible warehouse, logs info and moves to next
* **Exception on Invalid Inputs**: Would raise exception if inputs are invalid (based on SQLAlchemy usage)

***

### Implementation Notes

1. Uses same set intersection pattern as Agency Allocator, but for large geographic zones
2. Selection strategy is random (no load balancing in reference implementation)
3. Additional attributes stored in warehouse program-benefit code table
4. The implementation gracefully handles missing warehouse allocation (logs and continues)
5. No response structure validation - returns whatever intersection logic produces

***

### Expected Output Structure (Based on Code)

```python
{
    "batch_control_geo_id": str,
    "administrative_zone_id_large": str,
    # ... warehouse allocation details
}
```

Exact return fields need verification from actual database schema.

---
description: Design & Implementation
---

# Agency alloctor

### Module Information

* **Module Name**: `openg2p-g2p-bridge-agency-allocator`
* **Location**: `/openg2p-g2p-bridge-agency-allocator/`
* **Primary Implementation**: `AgencyAllocatorRefImpl`

***

### Interface Definition

**File**: `interface/agency_allocator_interface.py`

```python
class AgencyAllocator(BaseService):
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code: Dict,
        program: Dict,
    ) -> List[Dict]:
        """
        Allocates agencies to geographic zones.
        
        Args:
            small_geo_list: List of dicts with keys:
                - batch_control_geo_id
                - administrative_zone_id_small
                - administrative_zone_mnemonic_small
                
            benefit_code: Dict with keys:
                - id
                - mnemonic
                
            program: Dict with keys:
                - id
                - mnemonic
        
        Returns:
            List of dicts with keys:
                - batch_control_geo_id
                - administrative_zone_id_small
                - administrative_zone_mnemonic_small
                - benefit_code_id
                - program_id
                - agency_id
                - agency_mnemonic
                - agency_name
                - agency_admin_name
                - agency_admin_email
                - agency_admin_phone
                - agency_additional_attributes
        """
        raise NotImplementedError()
```

***

### Reference Implementation: AgencyAllocatorRefImpl

**File**: `implementations/agency_allocator_ref_impl.py`

#### Database Models Used

* `G2PAgency` - Agency master data
* `G2PAgencyProgramBenefitCode` - Authorization matrix (which agencies handle which programs/benefits)
* `G2PAdministrativeAreaSmallAgencyRel` - Geographic zone to agency mapping

#### Algorithm

The implementation uses a two-set intersection approach:

```
1. Get all agencies authorized for the given program + benefit_code
   Query: G2PAgencyProgramBenefitCode where program_id and benefit_code_id match
   Result: Set of authorized agency IDs
   
2. For each geographic zone:
   a. Get all agencies serving that geographic zone
      Query: G2PAdministrativeAreaSmallAgencyRel where geo ID matches
      Result: Set of geographic agency IDs
      
   b. Intersect the two sets
      Result: Eligible agencies = authorized AND geographic coverage
      
   c. If eligible agencies found:
      - Randomly select one agency
      - Fetch agency details from G2PAgency table
      - Fetch additional attributes from G2PAgencyProgramBenefitCode
      - Return allocation record
      
   d. If no eligible agencies:
      - Log warning
      - Raise Exception
```

#### Key Characteristics

1. **Random Selection**: Uses Python's `random.choice()` to select from eligible agencies
2. **Exception Handling**: Raises exception if no eligible agency found for any geo
3. **Database Engines**: Uses separate database connections:
   * `db_engine_pbms` - PBMS database for agency master data
4. **Logging**: Uses Python logging with logger name "agency\_allocator\_ref\_impl"

#### Data Types in Response

```python
{
    "batch_control_geo_id": str,
    "administrative_zone_id_small": str,
    "administrative_zone_mnemonic_small": str,
    "benefit_code_id": str,  # From input parameter
    "program_id": str,  # From input parameter
    "agency_id": str,
    "agency_mnemonic": str,  # From G2PAgency.agency_mnemonic
    "agency_name": str,  # From G2PAgency.name
    "agency_admin_name": str,  # From G2PAgency.admin_name
    "agency_admin_email": str,  # From G2PAgency.admin_email
    "agency_admin_phone": str,  # From G2PAgency.admin_mobile
    "agency_additional_attributes": Optional[dict]  # From G2PAgencyProgramBenefitCode.additional_info
}
```

***

### Factory Pattern

**File**: `factory/agency_allocator_factory.py`

```python
class AgencyAllocatorFactory(BaseService):
    @staticmethod
    def get_agency_allocator() -> AgencyAllocator:
        return AgencyAllocatorRefImpl.get_component()
```

The factory returns the reference implementation. Custom implementations would be substituted here.

***

### Configuration

**File**: `config.py`

Configuration is handled through `Settings` class (inherits from `BaseSettings`). Uses standard OpenG2P configuration pattern via environment variables.

***

### Database Dependencies

#### Tables Required

1. **G2PAgency**
   * Fields: id, agency\_mnemonic, name, admin\_name, admin\_email, admin\_mobile
2. **G2PAgencyProgramBenefitCode**
   * Fields: agency\_id, program\_id, benefit\_code\_id, additional\_info (JSON)
3. **G2PAdministrativeAreaSmallAgencyRel**
   * Fields: g2p\_administrative\_area\_small\_id, g2p\_agency\_id

#### Connection

* Engine key: `db_engine_pbms`
* Uses SQLAlchemy sessionmaker with expire\_on\_commit=False

***

### Integration Points

#### Celery Worker Integration

Called from Celery workers in the main bridge via the Factory pattern.

**Typical Celery Task Pattern**:

```python
allocator = AgencyAllocatorFactory.get_agency_allocator()
allocations = allocator.allocate_agency(
    small_geo_list=geos,
    benefit_code={'id': batch.benefit_code_id, 'mnemonic': batch.benefit_code_mnemonic},
    program={'id': batch.program_id, 'mnemonic': batch.program_mnemonic}
)
```

***

### Error Handling

* **Raises Exception** if no eligible agency found for a geographic zone
* Logs warnings for missing agencies
* No granular error codes - uses generic Exception

***

### Implementation Notes

1. The function processes all geographic zones in a batch, but if ANY zone has no eligible agency, it raises an exception for the entire batch
2. The algorithm uses set intersection, which is efficient for large datasets
3. Agency selection is random - no load balancing or priority logic in reference implementation
4. Additional attributes are pulled from the authorization table, not the agency master
5. The implementation does NOT handle the case where program/benefit\_code parameters contain None values

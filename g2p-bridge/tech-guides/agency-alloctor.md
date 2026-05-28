# Agency alloctor

## Agency Allocation - Design and Flow Document

### Table of Contents

1. Overview
2. Purpose and Use Case
3. Interface Definition
4. Data Models
5. Architecture and Design
6. Process Flow
7. Reference Implementation
8. Configuration
9. Error Handling
10. Integration with Celery Workers
11. Usage Examples

***

### Overview

**Agency Allocation** determines which agency (implementing organization) should handle the disbursement for a beneficiary in a specific geographic location. When multiple agencies operate in the same area for the same benefit program, the allocator selects the appropriate one.

**Module:** `openg2p-g2p-bridge-agency-allocator`

***

### Purpose and Use Case

#### Why Agency Allocation?

In many countries, government benefits are distributed through multiple implementing agencies:

* Different agencies handle different geographic regions
* Different agencies may specialize in different benefit programs
* Agencies may have specific authorization for certain beneficiary categories
* Load balancing across agencies

#### Real-World Example

```
Benefit Program: Cash Transfer Program (CTP)
Benefit Code: BEN-001

Geographic Distribution:
├─ State A
│  ├─ District A1 → Allocated to Agency X
│  └─ District A2 → Allocated to Agency Y
├─ State B
│  ├─ District B1 → Allocated to Agency X
│  └─ District B2 → Allocated to Agency Z
└─ State C
   └─ District C1 → Allocated to Agency W

The Agency Allocation service determines:
- For a beneficiary in State A, District A1 → Use Agency X
- For a beneficiary in State B, District B1 → Use Agency X or Z (selection logic)
- For a beneficiary in State C, District C1 → Use Agency W
```

#### Key Questions It Answers

1. **Which agency can handle this beneficiary?**
   * Geographic coverage
   * Program authorization
   * Benefit code eligibility
2. **If multiple agencies can handle it, which one?**
   * Load balancing
   * Specialization
   * Preference order
   * Random selection
3. **What additional agency metadata is needed?**
   * Agency contact info
   * Bank account details
   * Processing preferences
   * Rate limiting

***

### Interface Definition

#### AgencyAllocator Interface

```python
from typing import Dict, List
from openg2p_fastapi_common.service import BaseService

class AgencyAllocator(BaseService):
    """
    Interface for allocating agencies to beneficiaries
    
    The allocator receives a list of geographic zones (small geo) and
    determines which agency should handle each zone for a given benefit
    program and benefit code.
    """
    
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code: Dict,
        program: Dict,
    ) -> List[Dict]:
        """
        Allocate agencies for each geographic zone.
        
        Args:
            small_geo_list: List of dicts with structure:
                {
                    'batch_control_geo_id': str,  # Unique geo reference
                    'administrative_zone_id_small': str,  # Geographic zone ID
                    'administrative_zone_mnemonic_small': str,  # Zone code/name
                }
            
            benefit_code: Dict with structure:
                {
                    'id': str,  # Unique benefit code ID
                    'mnemonic': str,  # Human-readable code (e.g., 'BEN-001')
                }
            
            program: Dict with structure:
                {
                    'id': str,  # Unique program ID
                    'mnemonic': str,  # Human-readable program name
                }
        
        Returns:
            List of dicts with structure:
            [
                {
                    'batch_control_geo_id': str,  # Original geo reference
                    'administrative_zone_id_small': str,  # Geographic zone
                    'administrative_zone_mnemonic_small': str,  # Zone code
                    'benefit_code_id': str,  # Benefit code
                    'program_id': str,  # Program
                    'g2p_agency_id': str,  # Allocated agency ID
                    'g2p_agency_name': str,  # Agency name
                    'g2p_agency_code': str,  # Agency code
                    'additional_info': Dict,  # Agency-specific metadata
                }
            ]
        
        Raises:
            NoAgencyAvailableError: If no agency can handle the allocation
            InvalidGeographyError: If geographic zone is invalid
            InvalidProgramError: If program is invalid
        """
        raise NotImplementedError()
```

***

### Data Models

#### Input Models

**GeographicZone (Input)**

```python
class GeographicZone(BaseModel):
    batch_control_geo_id: str  # Reference for batch tracking
    administrative_zone_id_small: str  # Small geo zone ID
    administrative_zone_mnemonic_small: str  # Zone code
```

**BenefitCode (Input)**

```python
class BenefitCode(BaseModel):
    id: str  # Unique identifier
    mnemonic: str  # Human-readable code (BEN-001, etc.)
```

**Program (Input)**

```python
class Program(BaseModel):
    id: str  # Unique identifier
    mnemonic: str  # Program name (CTP, etc.)
```

#### Output Models

**AgencyAllocation (Output)**

```python
class AgencyAllocation(BaseModel):
    batch_control_geo_id: str
    administrative_zone_id_small: str
    administrative_zone_mnemonic_small: str
    benefit_code_id: str
    program_id: str
    g2p_agency_id: str
    g2p_agency_name: str
    g2p_agency_code: str
    additional_info: Optional[Dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "batch_control_geo_id": "BATCH-001-GEO-001",
                "administrative_zone_id_small": "ZONE-123",
                "administrative_zone_mnemonic_small": "DIST-A1",
                "benefit_code_id": "BEN-001",
                "program_id": "PROG-001",
                "g2p_agency_id": "AGENCY-X",
                "g2p_agency_name": "State Agency X",
                "g2p_agency_code": "SA-X",
                "additional_info": {
                    "account_number": "1234567890",
                    "bank_code": "BANK-001",
                    "contact_email": "admin@agency-x.gov"
                }
            }
        }
```

#### Database Models (Reference Implementation)

```python
# From openg2p_g2p_bridge_agency_allocator.models

class G2PAgency(Base):
    """Agency/Implementing Organization"""
    __tablename__ = "g2p_agency"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    status = Column(String)  # ACTIVE, INACTIVE

class G2PAdministrativeAreaSmallAgencyRel(Base):
    """Mapping between geographic zones and agencies"""
    __tablename__ = "g2p_admin_area_small_agency_rel"
    
    g2p_administrative_area_small_id = Column(String, primary_key=True)
    g2p_agency_id = Column(String, ForeignKey('g2p_agency.id'))
    
class G2PAgencyProgramBenefitCode(Base):
    """Authorization matrix: which agencies handle which programs/benefits"""
    __tablename__ = "g2p_agency_program_benefit_code"
    
    agency_id = Column(String, ForeignKey('g2p_agency.id'), primary_key=True)
    program_id = Column(String, primary_key=True)
    benefit_code_id = Column(String, primary_key=True)
    additional_info = Column(JSON)  # Extra agency-specific data
```

***

### Architecture and Design

#### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│  Celery Worker: agency_allocation_beat_producer     │
│  (in openg2p-g2p-bridge-celery-workers)            │
└────────────────┬────────────────────────────────────┘
                 │
                 │ 1. Queries pending allocations
                 │ 2. Calls Factory
                 ▼
┌─────────────────────────────────────────────────────┐
│  AgencyAllocatorFactory                             │
│  ├─ Reads environment config                        │
│  └─ Returns implementation instance                 │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Returns implementation
                 ▼
┌─────────────────────────────────────────────────────┐
│  AgencyAllocatorInterface                           │
│  (Abstract)                                         │
└────────────────▲────────────────────────────────────┘
                 │
       ┌─────────┴─────────┬──────────────┐
       │                   │              │
       ▼                   ▼              ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────┐
│ RefImpl         │ │ CustomImpl1     │ │ CustomImpl2   │
│ (Reference)    │ │ (Load Balance) │ │ (Preference) │
│                │ │                │ │              │
│ Random Select  │ │ Round Robin    │ │ Priority     │
│                │ │                │ │ Based        │
└────────┬───────┘ └────────┬───────┘ └──────┬───────┘
         │                  │                │
         │ Accesses         │ Accesses       │ Accesses
         ▼                  ▼                ▼
    ┌──────────────────────────────────────────┐
    │  PostgreSQL Database                     │
    │  ├─ g2p_agency                           │
    │  ├─ g2p_admin_area_small_agency_rel      │
    │  └─ g2p_agency_program_benefit_code      │
    └──────────────────────────────────────────┘
```

#### Key Design Patterns

**1. Strategy Pattern**

Different allocation strategies can be implemented:

* Random selection (reference)
* Round-robin load balancing
* Priority-based selection
* Preference matrix-based

**2. Factory Pattern**

```
AgencyAllocatorFactory
  ├─ Returns AgencyAllocatorRefImpl (random)
  ├─ Or returns LoadBalancingAllocator
  ├─ Or returns PreferenceBasedAllocator
  └─ Or returns CustomAllocator
```

**3. Single Responsibility**

Each allocator implementation focuses only on:

* Finding eligible agencies
* Applying selection logic
* Returning allocation result

**4. Immutability**

Input data (geographic zones, benefit codes) are not modified. A new allocation result is returned.

***

### Process Flow

#### High-Level Flow

```
┌─────────────────────────────────────────────┐
│  Disbursement Batch Initiated               │
│  - Program: Cash Transfer                   │
│  - Benefit Code: BEN-001                    │
│  - Geographic Zones: [Z1, Z2, Z3]           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Beat Producer Task │
        │ (Runs periodically)│
        └────────┬───────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Query Pending Allocations                  │
│  Status: PENDING_ALLOCATION                 │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ For Each Batch:     │
        │ - Get GEOs          │
        │ - Get Program/Benefit
        │   Code              │
        └────────┬────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Call Factory.get_agency_allocator()        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  allocator.allocate_agency(                 │
│    small_geo_list,                          │
│    benefit_code,                            │
│    program                                  │
│  )                                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ For Each GEO Zone:  │
        │ - Find eligible     │
        │   agencies          │
        │ - Select one        │
        │ - Get metadata      │
        │ - Return allocation │
        └────────┬────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Save Allocations to Database               │
│  Update Batch Status                        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Next Task (e.g.,     │
        │ Warehouse Allocation)│
        └──────────────────────┘
```

#### Detailed Allocation Flow (For Each Geographic Zone)

```
Input: 
  - Zone ID: "ZONE-123"
  - Benefit Code: "BEN-001"
  - Program: "PROG-001"

┌────────────────────────────────────────────┐
│ Step 1: Find Authorized Agencies           │
│ Query g2p_agency_program_benefit_code      │
│ WHERE program_id = "PROG-001"              │
│   AND benefit_code_id = "BEN-001"          │
│ Result: [AGENCY-X, AGENCY-Y, AGENCY-Z]    │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 2: Find Agencies in Geographic Zone   │
│ Query g2p_admin_area_small_agency_rel      │
│ WHERE administrative_zone_id_small         │
│     = "ZONE-123"                           │
│ Result: [AGENCY-X, AGENCY-W, AGENCY-Q]    │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 3: Intersect Both Sets                │
│ Authorized: [X, Y, Z]                      │
│ Geographic: [X, W, Q]                      │
│ Intersection: [X]                          │
│ Eligible Agencies: [X]                     │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 4: Select One Agency                  │
│ If only one: Select it                     │
│ If multiple: Apply selection logic         │
│ - Random (reference)                       │
│ - Round-robin                              │
│ - Priority-based                           │
│ Selected: AGENCY-X                         │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 5: Get Agency Metadata                │
│ Query g2p_agency WHERE id = "AGENCY-X"     │
│ Query additional_info from                 │
│   g2p_agency_program_benefit_code          │
│ Fetch:                                     │
│   - Agency name, code, status              │
│   - Bank account details                   │
│   - Contact info                           │
│   - Special handling instructions          │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 6: Return Allocation                  │
│ {                                          │
│   batch_control_geo_id: "B001-G001",      │
│   administrative_zone_id_small: "Z123",   │
│   g2p_agency_id: "AGENCY-X",              │
│   g2p_agency_name: "State Agency X",      │
│   additional_info: {                       │
│     account_number: "1234567890",         │
│     ...                                    │
│   }                                        │
│ }                                          │
└────────────────────────────────────────────┘
```

***

### Reference Implementation

#### AgencyAllocatorRefImpl

```python
import logging
import random
from typing import Dict, List
from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface import AgencyAllocator
from ..models import (
    G2PAdministrativeAreaSmallAgencyRel,
    G2PAgency,
    G2PAgencyProgramBenefitCode,
)

_logger = logging.getLogger("agency_allocator_ref_impl")
_engine = get_engine()

class AgencyAllocatorRefImpl(AgencyAllocator):
    """
    Reference implementation of Agency Allocator.
    Uses random selection when multiple agencies are available.
    """
    
    def __init__(self):
        self.session_maker = sessionmaker(
            bind=_engine.get("db_engine_pbms"),
            expire_on_commit=False
        )
    
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code: Dict,
        program: Dict,
    ) -> List[Dict]:
        """
        Allocate agencies using random selection strategy.
        """
        _logger.info(
            f"Allocating agencies for program={program.get('id')}, "
            f"benefit_code={benefit_code.get('id')}, "
            f"geos={len(small_geo_list)}"
        )
        
        results = []
        
        with self.session_maker() as pbms_session:
            try:
                # Step 1: Get agencies authorized for this program/benefit
                program_benefit_agency_ids = self._get_authorized_agencies(
                    pbms_session,
                    benefit_code['id'],
                    program['id']
                )
                
                _logger.debug(
                    f"Authorized agencies: {program_benefit_agency_ids}"
                )
                
                if not program_benefit_agency_ids:
                    _logger.warning(
                        f"No agencies authorized for "
                        f"program={program['id']}, "
                        f"benefit_code={benefit_code['id']}"
                    )
                    raise NoAgencyAvailableError(
                        f"No agencies authorized for "
                        f"program {program['id']}"
                    )
                
                # Step 2: For each geographic zone, allocate an agency
                for geo in small_geo_list:
                    allocation = self._allocate_for_geo(
                        pbms_session,
                        geo,
                        benefit_code['id'],
                        program['id'],
                        program_benefit_agency_ids
                    )
                    
                    if allocation:
                        results.append(allocation)
                    else:
                        _logger.warning(
                            f"No agency available for geo "
                            f"{geo.get('administrative_zone_id_small')}"
                        )
                
                _logger.info(f"Successfully allocated {len(results)} geos")
                return results
                
            except Exception as e:
                _logger.error(f"Agency allocation failed: {str(e)}")
                raise
    
    def _get_authorized_agencies(
        self,
        session,
        benefit_code_id: str,
        program_id: str
    ) -> set:
        """Get agencies authorized for this program/benefit combo"""
        
        agency_ids = {
            row.agency_id
            for row in session.query(G2PAgencyProgramBenefitCode)
            .filter(
                G2PAgencyProgramBenefitCode.program_id == program_id,
                G2PAgencyProgramBenefitCode.benefit_code_id == benefit_code_id,
            )
            .all()
        }
        
        return agency_ids
    
    def _get_agencies_in_geo(
        self,
        session,
        zone_id: str
    ) -> set:
        """Get agencies operating in this geographic zone"""
        
        agency_ids = {
            row.g2p_agency_id
            for row in session.query(G2PAdministrativeAreaSmallAgencyRel)
            .filter(
                G2PAdministrativeAreaSmallAgencyRel.g2p_administrative_area_small_id
                == zone_id
            )
            .all()
        }
        
        return agency_ids
    
    def _allocate_for_geo(
        self,
        session,
        geo: Dict,
        benefit_code_id: str,
        program_id: str,
        program_benefit_agency_ids: set
    ) -> Dict or None:
        """
        Allocate a single geographic zone to an agency.
        Steps:
        1. Get agencies in this geographic zone
        2. Intersect with authorized agencies
        3. Select one (random)
        4. Get agency metadata
        5. Return allocation
        """
        
        # Get agencies in this geographic zone
        geo_agency_ids = self._get_agencies_in_geo(
            session,
            geo['administrative_zone_id_small']
        )
        
        _logger.debug(
            f"Agencies in geo {geo['administrative_zone_id_small']}: "
            f"{geo_agency_ids}"
        )
        
        # Find intersection (authorized AND in geography)
        eligible_agency_ids = list(program_benefit_agency_ids & geo_agency_ids)
        
        _logger.debug(
            f"Eligible agencies for geo "
            f"{geo['administrative_zone_id_small']}: "
            f"{eligible_agency_ids}"
        )
        
        if not eligible_agency_ids:
            _logger.warning(
                f"No eligible agencies for geo "
                f"{geo['administrative_zone_id_small']}"
            )
            return None
        
        # Select one agency (random in reference implementation)
        selected_agency_id = random.choice(eligible_agency_ids)
        
        _logger.debug(
            f"Selected agency {selected_agency_id} "
            f"for geo {geo['administrative_zone_id_small']}"
        )
        
        # Get agency details
        g2p_agency = session.query(G2PAgency).filter(
            G2PAgency.id == selected_agency_id
        ).first()
        
        if not g2p_agency:
            _logger.error(f"Agency {selected_agency_id} not found")
            return None
        
        # Get additional info from authorization record
        benefit_code_entry = (
            session.query(G2PAgencyProgramBenefitCode)
            .filter(
                G2PAgencyProgramBenefitCode.agency_id == selected_agency_id,
                G2PAgencyProgramBenefitCode.program_id == program_id,
                G2PAgencyProgramBenefitCode.benefit_code_id == benefit_code_id,
            )
            .first()
        )
        
        additional_info = (
            benefit_code_entry.additional_info
            if benefit_code_entry
            else None
        )
        
        # Build and return allocation
        allocation = {
            'batch_control_geo_id': geo['batch_control_geo_id'],
            'administrative_zone_id_small': geo['administrative_zone_id_small'],
            'administrative_zone_mnemonic_small': geo['administrative_zone_mnemonic_small'],
            'benefit_code_id': benefit_code_id,
            'program_id': program_id,
            'g2p_agency_id': g2p_agency.id,
            'g2p_agency_name': g2p_agency.name,
            'g2p_agency_code': g2p_agency.code,
            'additional_info': additional_info,
        }
        
        return allocation
```

#### Key Features of Reference Implementation

1. **Two-Step Intersection**
   * Find authorized agencies (program + benefit level)
   * Find geographic agencies (geography level)
   * Use set intersection to find eligible agencies
2. **Random Selection**
   * When multiple agencies available, randomly choose
   * Simple, fair, and scalable
3. **Metadata Enrichment**
   * Includes agency details (name, code)
   * Includes additional\_info (bank details, preferences)
4. **Comprehensive Logging**
   * Debug-level logging for each step
   * Warning logs when no agencies available
   * Error logs with full context
5. **Error Handling**
   * Raises exception if no authorized agencies
   * Returns None per-geo if no agency available
   * Includes meaningful error messages

***

### Configuration

#### Environment Variables

```bash
# Agency Allocator Implementation Selection
AGENCY_ALLOCATOR_IMPL=reference  # Options: reference, load_balance, preference_based

# Database Configuration
PBMS_DATABASE_URL=postgresql://user:pass@host:5432/pbms_db

# Logging Configuration
AGENCY_ALLOCATOR_LOG_LEVEL=INFO

# Allocation Parameters
AGENCY_ALLOCATOR_ENABLE_CACHING=false
AGENCY_ALLOCATOR_CACHE_TTL_SECONDS=3600
```

#### Configuration Class

```python
from pydantic import BaseSettings

class AgencyAllocatorSettings(BaseSettings):
    """Agency Allocator Configuration"""
    
    implementation: str = "reference"
    pbms_database_url: str
    enable_caching: bool = False
    cache_ttl_seconds: int = 3600
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "AGENCY_ALLOCATOR_"
        env_file = ".env"
```

***

### Error Handling

#### Error Scenarios

```
1. No Authorized Agencies
   ├─ Cause: No agencies configured for program/benefit combo
   ├─ Error: NoAgencyAvailableError
   └─ Action: Fail batch, log error, notify admin

2. No Geographic Coverage
   ├─ Cause: No agencies in specified geographic zone
   ├─ Error: Partial allocation (some geos fail)
   └─ Action: Skip geo, continue with others, report

3. Database Connection Error
   ├─ Cause: PBMS database unavailable
   ├─ Error: DatabaseConnectionError
   └─ Action: Retry with backoff, fail batch

4. Invalid Input Data
   ├─ Cause: Missing/invalid geographic zone IDs
   ├─ Error: ValidationError
   └─ Action: Log and skip, continue

5. Agency Data Inconsistency
   ├─ Cause: Agency authorized but not in geography mapping
   ├─ Error: InconsistencyError
   └─ Action: Log warning, use fallback
```

#### Exception Hierarchy

```python
class AgencyAllocationException(Exception):
    """Base exception for agency allocation"""
    pass

class NoAgencyAvailableError(AgencyAllocationException):
    """No agency available for allocation"""
    pass

class InvalidGeographyError(AgencyAllocationException):
    """Invalid geographic zone"""
    pass

class InvalidProgramError(AgencyAllocationException):
    """Invalid program"""
    pass

class DatabaseError(AgencyAllocationException):
    """Database operation failed"""
    pass
```

#### Error Handling Pattern

```python
def allocate_agency(self, small_geo_list, benefit_code, program):
    try:
        # Main logic
        agencies = self._get_authorized_agencies(...)
        if not agencies:
            raise NoAgencyAvailableError(
                f"No agencies for program {program['id']}"
            )
        
        results = []
        for geo in small_geo_list:
            try:
                allocation = self._allocate_for_geo(...)
                results.append(allocation)
            except Exception as e:
                _logger.warning(f"Geo allocation failed: {e}")
                # Continue with next geo
        
        return results
        
    except NoAgencyAvailableError as e:
        _logger.error(f"Critical error: {e}")
        raise  # Re-raise critical errors
    except Exception as e:
        _logger.error(f"Unexpected error: {e}")
        raise
```

***

### Integration with Celery Workers

#### Celery Task in Main Bridge

**File:** `openg2p-g2p-bridge-celery-workers/src/.../tasks/agency_allocation.py`

```python
from celery import shared_task
import logging

from openg2p_g2p_bridge_models.models import (
    DisbursementBatchControl,
    BatchBeneficiary,
    BeneficiaryAllocation,
)
from openg2p_g2p_bridge_agency_allocator.factory import (
    AgencyAllocatorFactory
)

_logger = logging.getLogger(__name__)

@shared_task(name="agency_allocation_worker")
def agency_allocation_worker(batch_id: str):
    """
    Celery task to allocate agencies for a disbursement batch.
    
    Flow:
    1. Get batch details (program, benefit_code)
    2. Get all beneficiaries in batch with their geo zones
    3. Call allocator to get agency allocations
    4. Save allocations to database
    5. Update batch status
    """
    
    _logger.info(f"Starting agency allocation for batch {batch_id}")
    
    session = SessionLocal()
    
    try:
        # Step 1: Get batch details
        batch = session.query(DisbursementBatchControl).filter(
            DisbursementBatchControl.id == batch_id
        ).first()
        
        if not batch:
            _logger.error(f"Batch {batch_id} not found")
            return {"status": "failed", "reason": "batch_not_found"}
        
        # Step 2: Get beneficiaries grouped by geographic zone
        beneficiaries = session.query(BatchBeneficiary).filter(
            BatchBeneficiary.batch_id == batch_id
        ).all()
        
        # Build geographic zone list
        small_geo_list = []
        geo_set = set()
        
        for beneficiary in beneficiaries:
            geo_tuple = (
                beneficiary.administrative_zone_id_small,
                beneficiary.administrative_zone_mnemonic_small,
            )
            if geo_tuple not in geo_set:
                geo_set.add(geo_tuple)
                small_geo_list.append({
                    'batch_control_geo_id': f"{batch_id}-{beneficiary.administrative_zone_id_small}",
                    'administrative_zone_id_small': beneficiary.administrative_zone_id_small,
                    'administrative_zone_mnemonic_small': beneficiary.administrative_zone_mnemonic_small,
                })
        
        _logger.info(f"Found {len(small_geo_list)} unique geographic zones")
        
        # Step 3: Get allocator from factory
        allocator = AgencyAllocatorFactory.get_agency_allocator()
        
        # Step 4: Call allocator
        allocations = allocator.allocate_agency(
            small_geo_list=small_geo_list,
            benefit_code={
                'id': batch.benefit_code_id,
                'mnemonic': batch.benefit_code_mnemonic,
            },
            program={
                'id': batch.program_id,
                'mnemonic': batch.program_mnemonic,
            }
        )
        
        _logger.info(f"Allocator returned {len(allocations)} allocations")
        
        # Step 5: Build allocation map
        allocation_map = {
            alloc['administrative_zone_id_small']: alloc
            for alloc in allocations
        }
        
        # Step 6: Save allocations and update beneficiaries
        for beneficiary in beneficiaries:
            zone_id = beneficiary.administrative_zone_id_small
            if zone_id in allocation_map:
                allocation = allocation_map[zone_id]
                
                beneficiary.g2p_agency_id = allocation['g2p_agency_id']
                beneficiary.g2p_agency_name = allocation['g2p_agency_name']
                beneficiary.g2p_agency_code = allocation['g2p_agency_code']
                
                # Save allocation metadata
                session.add(
                    BeneficiaryAllocation(
                        beneficiary_id=beneficiary.id,
                        agency_id=allocation['g2p_agency_id'],
                        allocation_details=allocation['additional_info'],
                    )
                )
        
        session.commit()
        
        # Step 7: Update batch status
        batch.allocation_status = "COMPLETED"
        batch.updated_at = datetime.now()
        session.commit()
        
        _logger.info(f"Agency allocation completed for batch {batch_id}")
        return {"status": "success", "allocations": len(allocations)}
        
    except Exception as e:
        session.rollback()
        _logger.error(f"Agency allocation failed: {str(e)}", exc_info=True)
        
        # Update batch status to failed
        batch.allocation_status = "FAILED"
        batch.allocation_error = str(e)
        session.commit()
        
        return {"status": "failed", "reason": str(e)}
    
    finally:
        session.close()
```

#### Beat Producer Task

**File:** `openg2p-g2p-bridge-celery-beat-producers/src/.../tasks/agency_allocation.py`

```python
from celery import shared_task
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from openg2p_g2p_bridge_models.models import (
    DisbursementBatchControl,
    ProcessStatus,
)

@shared_task(name="agency_allocation_beat_producer")
def agency_allocation_beat_producer():
    """
    Beat producer: Finds pending batches and creates allocation tasks
    """
    
    session_maker = sessionmaker(bind=engine)
    
    with session_maker() as session:
        # Reset stale PROCESSING batches
        stale_at = datetime.now() - timedelta(minutes=30)
        session.query(DisbursementBatchControl).filter(
            DisbursementBatchControl.allocation_status == ProcessStatus.PROCESSING,
            DisbursementBatchControl.updated_at < stale_at,
        ).update({
            DisbursementBatchControl.allocation_status: ProcessStatus.PENDING
        })
        session.commit()
        
        # Get pending batches
        pending_batches = session.query(DisbursementBatchControl).filter(
            DisbursementBatchControl.allocation_status == ProcessStatus.PENDING
        ).limit(10).all()
        
        # For each batch, create a worker task
        for batch in pending_batches:
            # Mark as processing to prevent duplicates
            batch.allocation_status = ProcessStatus.PROCESSING
            session.commit()
            
            # Send task to worker
            agency_allocation_worker.delay(batch.id)
```

***

### Usage Examples

#### Example 1: Simple Allocation Request

```python
from openg2p_g2p_bridge_agency_allocator.factory import (
    AgencyAllocatorFactory
)

# Get the allocator
allocator = AgencyAllocatorFactory.get_agency_allocator()

# Prepare inputs
small_geos = [
    {
        'batch_control_geo_id': 'BATCH-001-GEO-001',
        'administrative_zone_id_small': 'ZONE-001',
        'administrative_zone_mnemonic_small': 'DISTRICT-A',
    },
    {
        'batch_control_geo_id': 'BATCH-001-GEO-002',
        'administrative_zone_id_small': 'ZONE-002',
        'administrative_zone_mnemonic_small': 'DISTRICT-B',
    },
]

benefit_code = {
    'id': 'BEN-001',
    'mnemonic': 'CASH-TRANSFER',
}

program = {
    'id': 'PROG-001',
    'mnemonic': 'CTP',
}

# Call allocator
allocations = allocator.allocate_agency(
    small_geo_list=small_geos,
    benefit_code=benefit_code,
    program=program,
)

# Process results
for allocation in allocations:
    print(f"Zone: {allocation['administrative_zone_mnemonic_small']}")
    print(f"Allocated to: {allocation['g2p_agency_name']}")
```

#### Example 2: Error Handling

```python
from openg2p_g2p_bridge_agency_allocator.factory import (
    AgencyAllocatorFactory
)
from openg2p_g2p_bridge_agency_allocator.exceptions import (
    NoAgencyAvailableError
)

try:
    allocator = AgencyAllocatorFactory.get_agency_allocator()
    allocations = allocator.allocate_agency(
        small_geo_list=geos,
        benefit_code=benefit_code,
        program=program,
    )
except NoAgencyAvailableError as e:
    print(f"No agencies available: {e}")
    # Escalate to admin
except Exception as e:
    print(f"Allocation error: {e}")
    # Log and retry
```

#### Example 3: Custom Implementation

```python
from openg2p_g2p_bridge_agency_allocator.interface import (
    AgencyAllocator
)
from typing import Dict, List

class LoadBalancingAllocator(AgencyAllocator):
    """
    Custom allocator that distributes load evenly
    """
    
    def allocate_agency(
        self,
        small_geo_list: List[Dict],
        benefit_code: Dict,
        program: Dict,
    ) -> List[Dict]:
        
        results = []
        agency_load = {}  # Track allocation count per agency
        
        for geo in small_geo_list:
            # Get eligible agencies
            eligible_agencies = self._get_eligible_agencies(
                geo, benefit_code, program
            )
            
            # Select agency with lowest load
            selected_agency = min(
                eligible_agencies,
                key=lambda a: agency_load.get(a['id'], 0)
            )
            
            # Update load counter
            agency_load[selected_agency['id']] = (
                agency_load.get(selected_agency['id'], 0) + 1
            )
            
            # Create allocation
            allocation = {
                'batch_control_geo_id': geo['batch_control_geo_id'],
                'administrative_zone_id_small': geo['administrative_zone_id_small'],
                'g2p_agency_id': selected_agency['id'],
                'g2p_agency_name': selected_agency['name'],
                # ... other fields
            }
            
            results.append(allocation)
        
        return results
```

***

### Summary

**Agency Allocation** is a critical extension point that determines which implementation organizations handle payments in specific geographic areas. The extension provides:

* **Flexible allocation logic** through pluggable implementations
* **Clear interface** defining inputs/outputs
* **Reference implementation** using random selection
* **Database integration** with agency and geography mappings
* **Seamless Celery integration** through factory pattern
* **Extensibility** for custom allocation strategies

Key points:

* Uses two-step intersection (authorization + geography)
* Handles partial failures gracefully
* Supports multiple custom implementations
* Integrates seamlessly with worker tasks
* Provides comprehensive error handling and logging

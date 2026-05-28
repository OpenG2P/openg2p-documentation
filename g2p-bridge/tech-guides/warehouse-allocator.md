# Warehouse allocator

## Warehouse Allocation - Design and Flow Document

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

**Warehouse Allocation** determines which warehouse(s) will distribute physical cash or in-kind benefits to beneficiaries in specific geographic regions. When cash benefits are physically distributed through a network of warehouses or distribution centers, this extension decides which warehouse handles which geographic area and allocates the required inventory/cash.

**Module:** `openg2p-g2p-bridge-warehouse-allocator`

***

### Purpose and Use Case

#### Why Warehouse Allocation?

In many government benefit systems, especially where cash distribution is physical:

**Physical Cash Distribution Network:**

* Central warehouses store bulk cash
* Regional warehouses serve districts/blocks
* Local collection points for beneficiary pickups
* Need to balance: Geographic coverage, Capacity, Security

**Inventory Management:**

* Warehouses have limited cash/goods capacity
* Need to ensure sufficient stock at each location
* Prevent stockouts in high-demand areas
* Minimize excess inventory holding costs

#### Real-World Example

```
National Cash Transfer Program
├─ Total Disbursement: 10,000,000 USD
├─ Beneficiaries: 5,000,000
├─ Geographic Coverage:
│  ├─ State A
│  │  ├─ District A1 (500,000 beneficiaries, 5M USD)
│  │  │  └─ Warehouse A1 (capacity: 3M) + Warehouse A1b (capacity: 2M)
│  │  └─ District A2 (300,000 beneficiaries, 3M USD)
│  │     └─ Warehouse A2 (capacity: 3.5M)
│  └─ State B
│     ├─ District B1 (400,000 beneficiaries, 4M USD)
│     │  └─ Warehouse B1 (capacity: 4.5M)
│     └─ District B2 (200,000 beneficiaries, 2M USD)
│        └─ Warehouse B2 (capacity: 2.5M)

Warehouse Allocator determines:
- Which warehouse serves each district
- How much cash to allocate to each warehouse
- Backup warehouses if primary is insufficient
- Cash movement schedule between warehouses
```

#### Key Questions It Answers

1. **Which warehouse serves this geographic area?**
   * Geographic coverage area
   * Distance/accessibility
   * Capacity constraints
2. **How much cash/inventory to allocate?**
   * Number of beneficiaries in area
   * Average benefit amount
   * Safety stock percentage
3. **What if warehouse capacity is insufficient?**
   * Use multiple warehouses
   * Staged distribution
   * Secondary allocation
4. **What are the warehouse-specific requirements?**
   * Security measures
   * Operating hours
   * Contact details
   * Special handling instructions

***

### Interface Definition

#### WarehouseAllocator Interface

```python
from typing import Dict, List
from openg2p_fastapi_common.service import BaseService

class WarehouseAllocator(BaseService):
    """
    Interface for allocating warehouses to geographic areas
    for physical distribution of benefits.
    
    The allocator receives information about beneficiary distribution
    and determines which warehouse(s) should handle distribution in
    each geographic area.
    """
    
    def allocate_warehouse(
        self,
        small_geo_list: List[Dict],
        beneficiary_count_per_geo: Dict,
        benefit_amount_per_beneficiary: float,
        total_benefit_amount: float,
    ) -> List[Dict]:
        """
        Allocate warehouses to geographic areas.
        
        Args:
            small_geo_list: List of geographic zones with structure:
                [
                    {
                        'batch_control_geo_id': str,  # Reference ID
                        'administrative_zone_id_small': str,  # Zone ID
                        'administrative_zone_mnemonic_small': str,  # Zone code
                    }
                ]
            
            beneficiary_count_per_geo: Dict mapping zone ID to count:
                {
                    'ZONE-001': 500000,  # 500k beneficiaries in this zone
                    'ZONE-002': 300000,
                }
            
            benefit_amount_per_beneficiary: Individual benefit amount
                e.g., 100.00 USD per beneficiary
            
            total_benefit_amount: Total cash/amount for entire batch
                e.g., 80000000.00 USD
        
        Returns:
            List of warehouse allocation records:
            [
                {
                    'batch_control_geo_id': str,
                    'administrative_zone_id_small': str,
                    'warehouse_id': str,
                    'warehouse_name': str,
                    'warehouse_code': str,
                    'warehouse_location': str,
                    'allocated_beneficiary_count': int,
                    'allocated_amount': float,
                    'currency': str,
                    'warehouse_capacity': float,
                    'allocation_sequence': int,  # In case of multiple warehouses per geo
                    'additional_info': Dict,  # Warehouse-specific metadata
                }
            ]
        
        Raises:
            NoWarehouseAvailableError: If no warehouse can serve the area
            InsufficientCapacityError: If total warehouse capacity < required amount
            InvalidGeographyError: If geographic zone is invalid
        """
        raise NotImplementedError()
    
    def validate_warehouse_capacity(
        self,
        warehouse_id: str,
        required_amount: float,
    ) -> bool:
        """
        Check if warehouse has sufficient capacity for allocation.
        
        Args:
            warehouse_id: Warehouse to check
            required_amount: Amount needed
        
        Returns:
            True if capacity sufficient, False otherwise
        """
        raise NotImplementedError()
    
    def get_warehouse_utilization(
        self,
        warehouse_id: str,
    ) -> Dict:
        """
        Get current utilization status of a warehouse.
        
        Returns:
            {
                'warehouse_id': str,
                'total_capacity': float,
                'allocated_amount': float,
                'available_capacity': float,
                'utilization_percentage': float,
            }
        """
        raise NotImplementedError()
```

***

### Data Models

#### Input Models

```python
class GeographicZone(BaseModel):
    batch_control_geo_id: str
    administrative_zone_id_small: str
    administrative_zone_mnemonic_small: str

class BeneficiaryDistribution(BaseModel):
    """Distribution of beneficiaries across zones"""
    zone_id: str
    beneficiary_count: int
    geographic_spread_km: float = None  # Area in km²
```

#### Output Models

```python
class WarehouseAllocation(BaseModel):
    """Single warehouse allocation record"""
    batch_control_geo_id: str
    administrative_zone_id_small: str
    warehouse_id: str
    warehouse_name: str
    warehouse_code: str
    warehouse_location: str
    
    allocated_beneficiary_count: int
    allocated_amount: float
    currency: str = "USD"
    
    warehouse_capacity: float
    allocation_sequence: int  # For multi-warehouse zones
    
    additional_info: Optional[Dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "batch_control_geo_id": "BATCH-001-GEO-001",
                "administrative_zone_id_small": "ZONE-001",
                "warehouse_id": "WH-001",
                "warehouse_name": "Central Warehouse",
                "warehouse_code": "CW-001",
                "warehouse_location": "New Delhi",
                "allocated_beneficiary_count": 500000,
                "allocated_amount": 50000000.00,
                "currency": "INR",
                "warehouse_capacity": 100000000.00,
                "allocation_sequence": 1,
                "additional_info": {
                    "contact_phone": "+91-11-xxxx",
                    "security_level": "HIGH",
                    "operating_hours": "24/7"
                }
            }
        }

class WarehouseUtilization(BaseModel):
    """Warehouse capacity/utilization info"""
    warehouse_id: str
    warehouse_name: str
    total_capacity: float
    allocated_amount: float
    available_capacity: float
    utilization_percentage: float
```

#### Database Models (Reference Implementation)

```python
class G2PWarehouse(Base):
    """Physical warehouse/distribution center"""
    __tablename__ = "g2p_warehouse"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    location = Column(String)  # Geographic location
    
    total_capacity = Column(Float)  # Storage capacity in currency units
    current_balance = Column(Float, default=0)  # Current stock
    
    operational_status = Column(String)  # ACTIVE, MAINTENANCE, CLOSED
    contact_phone = Column(String)
    contact_email = Column(String)
    operating_hours = Column(String)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class G2PAdministrativeAreaSmallWarehouseRel(Base):
    """Mapping between geographic zones and warehouses"""
    __tablename__ = "g2p_admin_area_small_warehouse_rel"
    
    g2p_administrative_area_small_id = Column(String, primary_key=True)
    g2p_warehouse_id = Column(String, ForeignKey('g2p_warehouse.id'))
    
    priority = Column(Integer, default=1)  # Priority for selection
    distance_km = Column(Float)  # Distance from zone to warehouse
    
class WarehouseAllocationRecord(Base):
    """Record of warehouse allocations for batch"""
    __tablename__ = "warehouse_allocation_record"
    
    id = Column(String, primary_key=True)
    batch_id = Column(String, ForeignKey('disbursement_batch.id'))
    warehouse_id = Column(String, ForeignKey('g2p_warehouse.id'))
    administrative_zone_id_small = Column(String)
    
    allocated_amount = Column(Float)
    allocated_beneficiary_count = Column(Integer)
    
    allocation_status = Column(String)  # ALLOCATED, DELIVERED, FAILED
    created_at = Column(DateTime, default=datetime.now)
```

***

### Architecture and Design

#### Component Diagram

```
┌──────────────────────────────────────────────────────┐
│  Celery Worker: warehouse_allocation_beat_producer   │
│  (in openg2p-g2p-bridge-celery-workers)             │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ 1. Gets batch details
                  │ 2. Calculates beneficiary counts per zone
                  │ 3. Calls Factory
                  ▼
┌──────────────────────────────────────────────────────┐
│  WarehouseAllocatorFactory                           │
│  ├─ Reads environment config                         │
│  └─ Returns implementation instance                  │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ Returns implementation
                  ▼
┌──────────────────────────────────────────────────────┐
│  WarehouseAllocatorInterface                         │
│  (Abstract)                                          │
└─────────────────▲────────────────────────────────────┘
                  │
        ┌─────────┴──────────┬───────────────┐
        │                    │               │
        ▼                    ▼               ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────┐
│ RefImpl         │ │ CapacityBased  │ │ Custom       │
│ (Reference)    │ │ (Weighted)     │ │              │
│                │ │                │ │              │
│ Simple Round   │ │ Smart Capacity │ │ Specialized  │
│ Robin          │ │ Balancing      │ │ Logic        │
└────────┬───────┘ └────────┬───────┘ └──────┬───────┘
         │                  │                │
         │ Accesses         │ Accesses       │ Accesses
         ▼                  ▼                ▼
    ┌────────────────────────────────────────────┐
    │  PostgreSQL Database                       │
    │  ├─ g2p_warehouse                          │
    │  ├─ g2p_admin_area_small_warehouse_rel     │
    │  └─ warehouse_allocation_record            │
    └────────────────────────────────────────────┘
```

#### Key Design Patterns

**1. Capacity-Based Allocation**

```
Available Warehouse Capacity: 100M
Required: 80M
Allocation: 80M (80% utilization)
```

**2. Multi-Warehouse Support**

```
Zone A: 100M required
  Warehouse 1: 60M capacity → allocate 60M (allocation_sequence=1)
  Warehouse 2: 50M capacity → allocate 20M (allocation_sequence=2)
  Warehouse 3: 30M capacity → allocate 20M (allocation_sequence=3)
```

**3. Load Balancing**

```
Distribute across warehouses proportionally:
  Warehouse 1 (100M capacity): 40%
  Warehouse 2 (80M capacity): 32%
  Warehouse 3 (60M capacity): 24%
  Warehouse 4: 4%
```

**4. Priority-Based Selection**

```
Geographic zone has warehouses with priorities:
  Priority 1: Primary warehouse (distance 5km)
  Priority 2: Secondary warehouse (distance 25km)
  Priority 3: Tertiary warehouse (distance 50km)

Selection:
  Try primary → if insufficient, add secondary → if still insufficient, add tertiary
```

***

### Process Flow

#### High-Level Flow

```
┌──────────────────────────────────────────┐
│  Disbursement Batch Created              │
│  - Total Beneficiaries: 5,000,000        │
│  - Total Amount: 500,000,000 USD         │
│  - Geographic Distribution: [Z1, Z2...]  │
└─────────────┬──────────────────────────┘
              │
              ▼
      ┌───────────────────┐
      │ Beat Producer     │
      │ (Every 1 hour)    │
      └────────┬──────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Query Pending Warehouse Allocations     │
│  Status: PENDING_WAREHOUSE_ALLOCATION    │
└─────────────┬──────────────────────────┘
              │
              ▼
      ┌───────────────────┐
      │ For Each Batch:   │
      │ - Get Zone List   │
      │ - Count Benefici- │
      │   aries per Zone  │
      │ - Get Amounts     │
      └────────┬──────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Call Factory.get_warehouse_allocator()  │
└─────────────┬──────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│  allocator.allocate_warehouse(           │
│    small_geo_list,                       │
│    beneficiary_count_per_geo,            │
│    benefit_per_beneficiary,              │
│    total_amount                          │
│  )                                       │
└─────────────┬──────────────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │ For Each GEO:        │
    │ - Find serving WH    │
    │ - Calculate amount   │
    │ - Check capacity     │
    │ - Allocate           │
    │ - Return allocation  │
    └────────┬─────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  Save Allocations to Database            │
│  Update Batch Status                     │
│  Calculate: Distribution Schedule        │
└─────────────┬──────────────────────────┘
              │
              ▼
      ┌────────────────────┐
      │ Next Phase:        │
      │ Warehouse Notifi-  │
      │ cation             │
      └────────────────────┘
```

#### Detailed Warehouse Selection Flow (For Each Zone)

```
Input:
  - Zone ID: "ZONE-001"
  - Beneficiary Count: 500,000
  - Benefit/Person: 100 USD
  - Required Amount: 50,000,000 USD

┌────────────────────────────────────────────┐
│ Step 1: Find Warehouses Serving This Zone  │
│ Query g2p_admin_area_small_warehouse_rel   │
│ WHERE admin_area_id = "ZONE-001"           │
│ ORDER BY priority ASC                      │
│ Result: [WH-001 (p=1), WH-002 (p=2)]      │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 2: Check Warehouse Capacities         │
│ WH-001: Total 100M, Current 60M, Free: 40M│
│ WH-002: Total 80M, Current 20M, Free: 60M │
│ WH-003: Total 60M, Current 10M, Free: 50M │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 3: Find Available Capacity             │
│ Total Available: 40M + 60M + 50M = 150M    │
│ Required: 50M                              │
│ Status: SUFFICIENT                         │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 4: Allocate Across Warehouses         │
│ (Using allocation strategy)                │
│                                            │
│ Strategy 1: Simple (primary first)         │
│   WH-001: 40M (hits capacity)             │
│   WH-002: 10M (remainder)                 │
│                                            │
│ Strategy 2: Balanced (proportional)        │
│   WH-001: 40M ÷ 150M × 50M = 13.33M      │
│   WH-002: 60M ÷ 150M × 50M = 20M         │
│   WH-003: 50M ÷ 150M × 50M = 16.67M      │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 5: Get Warehouse Details              │
│ For each allocated warehouse:              │
│ - Warehouse name, code, location           │
│ - Contact info (phone, email)              │
│ - Operating hours                          │
│ - Security requirements                    │
│ - Special handling instructions            │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Step 6: Return Allocations                 │
│ [                                          │
│   {                                        │
│     batch_control_geo_id: "B001-G001",    │
│     warehouse_id: "WH-001",                │
│     allocated_amount: 40000000,            │
│     allocation_sequence: 1,                │
│     warehouse_capacity: 100000000,         │
│     ...                                    │
│   },                                       │
│   {                                        │
│     batch_control_geo_id: "B001-G001",    │
│     warehouse_id: "WH-002",                │
│     allocated_amount: 10000000,            │
│     allocation_sequence: 2,                │
│     warehouse_capacity: 80000000,          │
│     ...                                    │
│   }                                        │
│ ]                                          │
└────────────────────────────────────────────┘
```

***

### Reference Implementation

#### WarehouseAllocatorRefImpl

```python
import logging
from typing import Dict, List
from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface import WarehouseAllocator
from ..models import (
    G2PWarehouse,
    G2PAdministrativeAreaSmallWarehouseRel,
)

_logger = logging.getLogger("warehouse_allocator_ref_impl")
_engine = get_engine()

class WarehouseAllocatorRefImpl(WarehouseAllocator):
    """
    Reference implementation of Warehouse Allocator.
    Uses simple sequential allocation (primary warehouse first,
    then secondary, etc. as needed).
    """
    
    def __init__(self):
        self.session_maker = sessionmaker(
            bind=_engine.get("db_engine"),
            expire_on_commit=False
        )
    
    def allocate_warehouse(
        self,
        small_geo_list: List[Dict],
        beneficiary_count_per_geo: Dict,
        benefit_amount_per_beneficiary: float,
        total_benefit_amount: float,
    ) -> List[Dict]:
        """
        Allocate warehouses using simple strategy:
        - Use primary warehouse first until capacity exhausted
        - Fall back to secondary, tertiary, etc.
        """
        
        _logger.info(
            f"Allocating warehouses for {len(small_geo_list)} zones, "
            f"total amount: {total_benefit_amount}"
        )
        
        results = []
        
        with self.session_maker() as session:
            try:
                # For each geographic zone
                for geo in small_geo_list:
                    zone_id = geo['administrative_zone_id_small']
                    beneficiary_count = beneficiary_count_per_geo.get(zone_id, 0)
                    required_amount = (
                        beneficiary_count * benefit_amount_per_beneficiary
                    )
                    
                    _logger.debug(
                        f"Allocating for zone {zone_id}: "
                        f"{beneficiary_count} beneficiaries, "
                        f"{required_amount} amount"
                    )
                    
                    # Get warehouses serving this zone
                    warehouses = self._get_warehouses_for_zone(
                        session,
                        zone_id
                    )
                    
                    if not warehouses:
                        _logger.warning(
                            f"No warehouses available for zone {zone_id}"
                        )
                        raise NoWarehouseAvailableError(
                            f"No warehouses for zone {zone_id}"
                        )
                    
                    # Allocate across warehouses
                    zone_allocations = self._allocate_to_warehouses(
                        session,
                        geo,
                        warehouses,
                        beneficiary_count,
                        required_amount,
                        benefit_amount_per_beneficiary
                    )
                    
                    results.extend(zone_allocations)
                
                _logger.info(
                    f"Successfully allocated {len(results)} warehouse records"
                )
                return results
                
            except Exception as e:
                _logger.error(f"Warehouse allocation failed: {str(e)}")
                raise
    
    def _get_warehouses_for_zone(
        self,
        session,
        zone_id: str
    ) -> List[Dict]:
        """
        Get warehouses serving a geographic zone,
        ordered by priority.
        """
        
        warehouse_rels = session.query(
            G2PAdministrativeAreaSmallWarehouseRel
        ).filter(
            G2PAdministrativeAreaSmallWarehouseRel.g2p_administrative_area_small_id
            == zone_id
        ).order_by(
            G2PAdministrativeAreaSmallWarehouseRel.priority.asc()
        ).all()
        
        warehouses = []
        for rel in warehouse_rels:
            warehouse = session.query(G2PWarehouse).filter(
                G2PWarehouse.id == rel.g2p_warehouse_id
            ).first()
            
            if warehouse and warehouse.operational_status == 'ACTIVE':
                warehouses.append({
                    'id': warehouse.id,
                    'name': warehouse.name,
                    'code': warehouse.code,
                    'location': warehouse.location,
                    'total_capacity': warehouse.total_capacity,
                    'current_balance': warehouse.current_balance,
                    'available_capacity': (
                        warehouse.total_capacity - warehouse.current_balance
                    ),
                    'contact_phone': warehouse.contact_phone,
                    'contact_email': warehouse.contact_email,
                    'operating_hours': warehouse.operating_hours,
                    'priority': rel.priority,
                    'distance_km': rel.distance_km,
                })
        
        return warehouses
    
    def _allocate_to_warehouses(
        self,
        session,
        geo: Dict,
        warehouses: List[Dict],
        beneficiary_count: int,
        required_amount: float,
        benefit_amount_per_beneficiary: float
    ) -> List[Dict]:
        """
        Allocate required amount across available warehouses.
        
        Strategy: Use primary warehouse first, fall back to secondary
        as needed.
        """
        
        allocations = []
        remaining_amount = required_amount
        remaining_beneficiaries = beneficiary_count
        allocation_sequence = 1
        
        # Check total available capacity
        total_capacity = sum(w['available_capacity'] for w in warehouses)
        
        if total_capacity < required_amount:
            _logger.warning(
                f"Insufficient warehouse capacity: "
                f"required {required_amount}, available {total_capacity}"
            )
            raise InsufficientCapacityError(
                f"Insufficient capacity for zone "
                f"{geo['administrative_zone_id_small']}"
            )
        
        # Allocate to each warehouse
        for warehouse in warehouses:
            if remaining_amount <= 0:
                break
            
            # Allocate to this warehouse
            allocate_amount = min(
                remaining_amount,
                warehouse['available_capacity']
            )
            
            # Calculate beneficiaries for this warehouse
            allocate_beneficiaries = int(
                allocate_amount / benefit_amount_per_beneficiary
            )
            
            _logger.debug(
                f"Allocating {allocate_amount} to "
                f"{warehouse['name']} "
                f"({allocate_beneficiaries} beneficiaries)"
            )
            
            allocation = {
                'batch_control_geo_id': geo['batch_control_geo_id'],
                'administrative_zone_id_small': (
                    geo['administrative_zone_id_small']
                ),
                'warehouse_id': warehouse['id'],
                'warehouse_name': warehouse['name'],
                'warehouse_code': warehouse['code'],
                'warehouse_location': warehouse['location'],
                'allocated_beneficiary_count': allocate_beneficiaries,
                'allocated_amount': allocate_amount,
                'currency': 'USD',
                'warehouse_capacity': warehouse['total_capacity'],
                'allocation_sequence': allocation_sequence,
                'additional_info': {
                    'contact_phone': warehouse['contact_phone'],
                    'contact_email': warehouse['contact_email'],
                    'operating_hours': warehouse['operating_hours'],
                    'distance_km': warehouse['distance_km'],
                },
            }
            
            allocations.append(allocation)
            
            remaining_amount -= allocate_amount
            remaining_beneficiaries -= allocate_beneficiaries
            allocation_sequence += 1
        
        return allocations
    
    def validate_warehouse_capacity(
        self,
        warehouse_id: str,
        required_amount: float,
    ) -> bool:
        """Check if warehouse has sufficient capacity"""
        
        with self.session_maker() as session:
            warehouse = session.query(G2PWarehouse).filter(
                G2PWarehouse.id == warehouse_id
            ).first()
            
            if not warehouse:
                return False
            
            available = (
                warehouse.total_capacity - warehouse.current_balance
            )
            return available >= required_amount
    
    def get_warehouse_utilization(
        self,
        warehouse_id: str,
    ) -> Dict:
        """Get warehouse capacity and utilization stats"""
        
        with self.session_maker() as session:
            warehouse = session.query(G2PWarehouse).filter(
                G2PWarehouse.id == warehouse_id
            ).first()
            
            if not warehouse:
                raise ValueError(f"Warehouse {warehouse_id} not found")
            
            available = (
                warehouse.total_capacity - warehouse.current_balance
            )
            utilization = (
                (warehouse.current_balance / warehouse.total_capacity * 100)
                if warehouse.total_capacity > 0
                else 0
            )
            
            return {
                'warehouse_id': warehouse.id,
                'warehouse_name': warehouse.name,
                'total_capacity': warehouse.total_capacity,
                'allocated_amount': warehouse.current_balance,
                'available_capacity': available,
                'utilization_percentage': utilization,
            }
```

#### Key Features of Reference Implementation

1. **Sequential Allocation**
   * Allocates to primary warehouse first
   * Falls back to secondary, tertiary, etc.
   * Simple and predictable
2. **Capacity Validation**
   * Checks total available capacity before allocation
   * Rejects if insufficient
3. **Multi-Warehouse Support**
   * Allocates single zone to multiple warehouses if needed
   * Tracks allocation sequence
   * Maintains geographic relationship
4. **Beneficiary Tracking**
   * Calculates beneficiaries per warehouse
   * Tracks remaining beneficiaries and amount
5. **Comprehensive Logging**
   * Debug logs for each warehouse allocation
   * Warnings for capacity issues
   * Error logs with context

***

### Configuration

#### Environment Variables

```bash
# Warehouse Allocator Implementation
WAREHOUSE_ALLOCATOR_IMPL=reference  # Options: reference, balanced, priority_based

# Database
WAREHOUSE_DATABASE_URL=postgresql://user:pass@host:5432/warehouse_db

# Allocation Strategy
WAREHOUSE_ALLOCATOR_STRATEGY=sequential  # or balanced, proportional
WAREHOUSE_ALLOCATOR_SAFETY_STOCK_PERCENTAGE=10  # Extra buffer

# Warehouse Parameters
WAREHOUSE_MIN_VIABLE_CAPACITY=100000  # Minimum warehouse size
WAREHOUSE_ALLOCATOR_ENABLE_MULTI_WAREHOUSE=true  # Multi-warehouse per zone

# Logging
WAREHOUSE_ALLOCATOR_LOG_LEVEL=INFO
```

#### Configuration Class

```python
from pydantic import BaseSettings

class WarehouseAllocatorSettings(BaseSettings):
    implementation: str = "reference"
    database_url: str
    strategy: str = "sequential"
    safety_stock_percentage: int = 10
    min_viable_capacity: float = 100000.0
    enable_multi_warehouse: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "WAREHOUSE_ALLOCATOR_"
```

***

### Error Handling

#### Error Scenarios

```
1. No Warehouses Available
   ├─ Cause: No warehouses configured for geographic zone
   ├─ Error: NoWarehouseAvailableError
   └─ Action: Block batch, escalate to admin

2. Insufficient Capacity
   ├─ Cause: Total warehouse capacity < required amount
   ├─ Error: InsufficientCapacityError
   └─ Action: Reduce allocation or add warehouses

3. Warehouse Unavailable
   ├─ Cause: Warehouse maintenance, closed
   ├─ Error: WarehouseUnavailableError
   └─ Action: Use alternate warehouse

4. Database Error
   ├─ Cause: Database connection failure
   ├─ Error: DatabaseError
   └─ Action: Retry with backoff

5. Invalid Input
   ├─ Cause: Invalid zone ID, negative beneficiary count
   ├─ Error: ValidationError
   └─ Action: Log and skip
```

***

### Integration with Celery Workers

#### Celery Task (Main Bridge)

```python
@shared_task(name="warehouse_allocation_worker")
def warehouse_allocation_worker(batch_id: str):
    """
    Celery task to allocate warehouses for a batch.
    
    Called after agency allocation is complete.
    """
    
    session = SessionLocal()
    
    try:
        # Get batch
        batch = session.query(DisbursementBatchControl).filter(
            DisbursementBatchControl.id == batch_id
        ).first()
        
        # Get beneficiary distribution per zone
        beneficiary_per_geo = {}
        beneficiaries = session.query(BatchBeneficiary).filter(
            BatchBeneficiary.batch_id == batch_id
        ).all()
        
        for beneficiary in beneficiaries:
            zone = beneficiary.administrative_zone_id_small
            beneficiary_per_geo[zone] = (
                beneficiary_per_geo.get(zone, 0) + 1
            )
        
        # Build geo list (unique zones)
        small_geo_list = []
        for zone_id, count in beneficiary_per_geo.items():
            # Get zone details
            zone_record = session.query(
                AdministrativeZoneSmall
            ).filter(
                AdministrativeZoneSmall.id == zone_id
            ).first()
            
            if zone_record:
                small_geo_list.append({
                    'batch_control_geo_id': f"{batch_id}-{zone_id}",
                    'administrative_zone_id_small': zone_id,
                    'administrative_zone_mnemonic_small': (
                        zone_record.mnemonic
                    ),
                })
        
        # Get allocator
        allocator = WarehouseAllocatorFactory.get_warehouse_allocator()
        
        # Allocate
        allocations = allocator.allocate_warehouse(
            small_geo_list=small_geo_list,
            beneficiary_count_per_geo=beneficiary_per_geo,
            benefit_amount_per_beneficiary=(
                batch.benefit_amount_per_beneficiary
            ),
            total_benefit_amount=batch.total_benefit_amount,
        )
        
        # Save allocations
        for allocation in allocations:
            record = WarehouseAllocationRecord(
                batch_id=batch_id,
                warehouse_id=allocation['warehouse_id'],
                administrative_zone_id_small=(
                    allocation['administrative_zone_id_small']
                ),
                allocated_amount=allocation['allocated_amount'],
                allocated_beneficiary_count=(
                    allocation['allocated_beneficiary_count']
                ),
                allocation_status='ALLOCATED',
            )
            session.add(record)
        
        session.commit()
        
        # Update batch status
        batch.warehouse_allocation_status = "COMPLETED"
        session.commit()
        
        return {"status": "success", "allocations": len(allocations)}
        
    except Exception as e:
        session.rollback()
        _logger.error(f"Warehouse allocation failed: {e}")
        
        batch.warehouse_allocation_status = "FAILED"
        batch.warehouse_allocation_error = str(e)
        session.commit()
        
        return {"status": "failed", "reason": str(e)}
    
    finally:
        session.close()
```

***

### Usage Examples

#### Example 1: Basic Warehouse Allocation

```python
from openg2p_g2p_bridge_warehouse_allocator.factory import (
    WarehouseAllocatorFactory
)

allocator = WarehouseAllocatorFactory.get_warehouse_allocator()

# Input data
small_geos = [
    {
        'batch_control_geo_id': 'B001-Z001',
        'administrative_zone_id_small': 'ZONE-001',
        'administrative_zone_mnemonic_small': 'DIST-A',
    }
]

beneficiary_per_geo = {
    'ZONE-001': 500000,
}

# Allocate
allocations = allocator.allocate_warehouse(
    small_geo_list=small_geos,
    beneficiary_count_per_geo=beneficiary_per_geo,
    benefit_amount_per_beneficiary=100.0,
    total_benefit_amount=50000000.0,
)

# Output
for alloc in allocations:
    print(f"Warehouse: {alloc['warehouse_name']}")
    print(f"Allocation: {alloc['allocated_amount']} USD")
    print(f"Beneficiaries: {alloc['allocated_beneficiary_count']}")
    print("---")
```

#### Example 2: Check Warehouse Capacity

```python
allocator = WarehouseAllocatorFactory.get_warehouse_allocator()

# Check capacity
has_capacity = allocator.validate_warehouse_capacity(
    warehouse_id='WH-001',
    required_amount=50000000.0,
)

if has_capacity:
    print("Warehouse has sufficient capacity")
else:
    print("Warehouse capacity insufficient")

# Get utilization
util = allocator.get_warehouse_utilization('WH-001')
print(f"Utilization: {util['utilization_percentage']}%")
```

#### Example 3: Custom Load-Balanced Allocator

```python
from openg2p_g2p_bridge_warehouse_allocator.interface import (
    WarehouseAllocator
)

class LoadBalancedAllocator(WarehouseAllocator):
    """Allocate proportional to warehouse capacity"""
    
    def allocate_warehouse(
        self, small_geo_list, beneficiary_count_per_geo,
        benefit_amount_per_beneficiary, total_benefit_amount
    ):
        allocations = []
        
        for geo in small_geo_list:
            zone_id = geo['administrative_zone_id_small']
            required = (
                beneficiary_count_per_geo[zone_id] *
                benefit_amount_per_beneficiary
            )
            
            warehouses = self._get_warehouses(zone_id)
            
            # Calculate total capacity
            total_capacity = sum(
                w['available_capacity'] for w in warehouses
            )
            
            # Allocate proportionally
            for warehouse in warehouses:
                proportion = (
                    warehouse['available_capacity'] / total_capacity
                )
                allocate_amount = required * proportion
                
                allocation = {
                    'batch_control_geo_id': geo['batch_control_geo_id'],
                    'administrative_zone_id_small': zone_id,
                    'warehouse_id': warehouse['id'],
                    'allocated_amount': allocate_amount,
                    # ... other fields
                }
                allocations.append(allocation)
        
        return allocations
```

***

### Summary

**Warehouse Allocation** determines how physical cash/benefits are distributed across the warehouse network. The extension provides:

* **Flexible allocation strategies** through pluggable implementations
* **Capacity-aware allocation** preventing stockouts
* **Multi-warehouse support** for load distribution
* **Clear interface** defining inputs and outputs
* **Reference implementation** using sequential allocation
* **Seamless integration** with Celery tasks

Key points:

* Balances geographic coverage with capacity constraints
* Supports multiple warehouses per geographic zone
* Tracks beneficiaries and amounts per warehouse
* Integrates with warehouse inventory systems
* Enables custom allocation strategies

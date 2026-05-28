# Geo resolver

## Geo Resolution - Design and Flow Document

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

**Geo Resolution** maps beneficiary location information (addresses, coordinates, village names, etc.) to standardized administrative geographic zones used by the disbursement system. This determines which geographic area (district, block, zone) a beneficiary belongs to, which in turn affects which agency and warehouse handles their payment.

**Module:** `openg2p-g2p-bridge-geo-resolver`

***

### Purpose and Use Case

#### Why Geo Resolution?

Beneficiary records contain location information in various formats:

* **Address-based:** Village, post office, district
* **Coordinate-based:** GPS coordinates (latitude/longitude)
* **Administrative:** Traditional geographic identifiers
* **Name-based:** Place names, landmarks

The system needs standardized administrative zones for:

* Consistent decision-making (agency allocation)
* Geographic grouping (batch processing)
* Reporting and analytics
* Boundary consistency

#### Real-World Example

```
Beneficiary Records:
├─ Bene-001
│  ├─ Name: Ramesh Kumar
│  ├─ Location: Village Chapar, Post Belgaum, Belgaum District
│  ├─ State: Karnataka
│  └─ GPS: 15.8497° N, 75.6699° E
│
├─ Bene-002
│  ├─ Name: Rajesh Singh
│  ├─ Location: Belgaum City, Belgaum District
│  └─ GPS: 15.8588° N, 75.6781° E
│
└─ Bene-003
   ├─ Name: Priya Patel
   ├─ Location: "Belgaum area" (vague)
   └─ GPS: None

Geo Resolution Task:
├─ Bene-001 → Matches village → Zone-001 (Belgaum District)
├─ Bene-002 → Matches city coordinates → Zone-001 (Belgaum District)
└─ Bene-003 → Fuzzy match → Zone-001 (Belgaum District - high confidence)

Output:
├─ Bene-001 → administrative_zone_id_large: STATE-KA, administrative_zone_id_small: DIST-001
├─ Bene-002 → administrative_zone_id_large: STATE-KA, administrative_zone_id_small: DIST-001
└─ Bene-003 → administrative_zone_id_large: STATE-KA, administrative_zone_id_small: DIST-001
```

#### Key Questions It Answers

1. **Which geographic zone does this beneficiary belong to?**
   * Matches address against known locations
   * Uses coordinates if available
   * Falls back to fuzzy matching
2. **What is the geographic hierarchy?**
   * Large zone (state/province)
   * Small zone (district/block)
3. **How confident is the resolution?**
   * Exact match
   * High confidence (95%+)
   * Medium confidence (75-95%)
   * Low confidence (<75%)
4. **What if beneficiary location is ambiguous?**
   * Flag for manual review
   * Use default/parent zone
   * Reject and request clarification

***

### Interface Definition

#### GeoResolver Interface

```python
from typing import Dict, List
from openg2p_fastapi_common.service import BaseService

class GeoResolver(BaseService):
    """
    Interface for resolving beneficiary geographic locations
    to standard administrative zones.
    
    The resolver receives a list of beneficiaries with location
    information and returns their mapped administrative zones.
    """
    
    def resolve_geo(
        self,
        batch_beneficiary_list: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """
        Resolve geographic zones for beneficiaries.
        
        Args:
            batch_beneficiary_list: List of beneficiary records with structure:
                [
                    {
                        'disbursement_id': str,  # Batch/envelope reference
                        'beneficiary_id': str,  # Unique beneficiary ID
                        'name': str,  # Beneficiary name
                        'address': str,  # Complete address
                        'village': str,  # Village/town name
                        'post_office': str,  # Post office
                        'taluka': str,  # Block/Taluka
                        'district': str,  # District name
                        'state': str,  # State/Province
                        'latitude': float,  # GPS latitude (optional)
                        'longitude': float,  # GPS longitude (optional)
                        'pin_code': str,  # Postal code (optional)
                    }
                ]
        
        Returns:
            List of resolved records with structure:
            [
                {
                    'disbursement_id': str,
                    'beneficiary_id': str,
                    'administrative_zone_id_large': str,  # State/Province ID
                    'administrative_zone_mnemonic_large': str,  # State code
                    'administrative_zone_id_small': str,  # District/Block ID
                    'administrative_zone_mnemonic_small': str,  # District code
                    'resolution_confidence': float,  # 0-100 percentage
                    'resolution_method': str,  # HOW resolution was done
                    'matched_location': str,  # What location was matched
                }
            ]
        
        Raises:
            NoLocationMatchError: If location cannot be resolved
            InvalidLocationError: If location data is invalid
            AmbiguousLocationError: If multiple matches found
        """
        raise NotImplementedError()
    
    def validate_location(
        self,
        address: str,
        district: str,
        state: str,
    ) -> bool:
        """
        Validate if location data is sufficient for resolution.
        
        Returns:
            True if sufficient, False otherwise
        """
        raise NotImplementedError()
    
    def get_resolution_confidence(
        self,
        beneficiary_id: str,
    ) -> Dict:
        """
        Get confidence details for a beneficiary's geo resolution.
        
        Returns:
            {
                'beneficiary_id': str,
                'confidence_level': str,  # HIGH, MEDIUM, LOW
                'confidence_score': float,  # 0-100
                'resolution_method': str,
                'alternative_zones': List[Dict],  # Other possible matches
            }
        """
        raise NotImplementedError()
```

***

### Data Models

#### Input Models

```python
class BeneficiaryLocation(BaseModel):
    """Beneficiary location information"""
    disbursement_id: str
    beneficiary_id: str
    name: Optional[str] = None
    
    # Address components
    address: Optional[str] = None
    village: Optional[str] = None
    post_office: Optional[str] = None
    taluka: Optional[str] = None  # Block/Sub-district
    district: Optional[str] = None
    state: Optional[str] = None
    
    # Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Other identifiers
    pin_code: Optional[str] = None
    aadhaar_address: Optional[str] = None  # Aadhaar-registered address
```

#### Output Models

```python
class GeoResolution(BaseModel):
    """Resolved geographic location"""
    disbursement_id: str
    beneficiary_id: str
    
    # Resolved zones
    administrative_zone_id_large: str  # State/Province ID
    administrative_zone_mnemonic_large: str  # State code
    administrative_zone_id_small: str  # District/Block ID
    administrative_zone_mnemonic_small: str  # District code
    
    # Resolution details
    resolution_confidence: float  # 0-100
    resolution_method: str  # EXACT, FUZZY, COORDINATES, etc.
    matched_location: str  # What actually matched
    
    class Config:
        schema_extra = {
            "example": {
                "disbursement_id": "BATCH-001",
                "beneficiary_id": "BENE-001",
                "administrative_zone_id_large": "STATE-KA",
                "administrative_zone_mnemonic_large": "KA",
                "administrative_zone_id_small": "DIST-001",
                "administrative_zone_mnemonic_small": "BELGAUM",
                "resolution_confidence": 95.5,
                "resolution_method": "ADDRESS_MATCH",
                "matched_location": "Belgaum District",
            }
        }

class ResolutionConfidence(BaseModel):
    """Confidence details for geo resolution"""
    beneficiary_id: str
    confidence_level: str  # HIGH, MEDIUM, LOW
    confidence_score: float
    resolution_method: str
    alternative_zones: Optional[List[Dict]] = None
```

#### Database Models (Reference Implementation)

```python
class GeographicZone(Base):
    """Geographic administrative zones"""
    __tablename__ = "geographic_zone"
    
    id = Column(String, primary_key=True)
    zone_type = Column(String)  # LARGE (state), SMALL (district)
    name = Column(String, nullable=False)
    mnemonic = Column(String)  # Code (KA, DL, etc.)
    
    parent_id = Column(String)  # Parent zone (state for district)
    
    geographic_boundaries = Column(JSON)  # Boundary data for geo-fencing
    centroid_latitude = Column(Float)  # Center point
    centroid_longitude = Column(Float)

class LocationMaster(Base):
    """Location master registry"""
    __tablename__ = "location_master"
    
    id = Column(String, primary_key=True)
    village_name = Column(String)
    block_name = Column(String)
    district_name = Column(String)
    state_name = Column(String)
    
    geographic_zone_id_small = Column(
        String,
        ForeignKey('geographic_zone.id')
    )
    geographic_zone_id_large = Column(
        String,
        ForeignKey('geographic_zone.id')
    )
    
    pin_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # For farmer registry example
    farmer_registry_reference = Column(String)

class GeoBeneficiaryRegistry(Base):
    """Farmer/Beneficiary location registry (example)"""
    __tablename__ = "geo_beneficiary_registry"
    
    beneficiary_id = Column(String, primary_key=True)
    beneficiary_name = Column(String)
    
    village_name = Column(String)
    block_name = Column(String)
    district_name = Column(String)
    state_name = Column(String)
    
    geographic_zone_id_small = Column(String)
    geographic_zone_id_large = Column(String)
    
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Registration details
    registration_date = Column(DateTime)
    registry_source = Column(String)  # Where beneficiary was registered
```

***

### Architecture and Design

#### Component Diagram

```
┌──────────────────────────────────────────────────────┐
│  Celery Worker: geo_resolution_beat_producer         │
│  (in openg2p-g2p-bridge-celery-workers)             │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ 1. Gets pending batch beneficiaries
                  │ 2. Extracts location info
                  │ 3. Calls Factory
                  ▼
┌──────────────────────────────────────────────────────┐
│  GeoResolverFactory                                  │
│  ├─ Reads environment config                         │
│  └─ Returns implementation instance                  │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ Returns implementation
                  ▼
┌──────────────────────────────────────────────────────┐
│  GeoResolverInterface                                │
│  (Abstract)                                          │
└─────────────────▲────────────────────────────────────┘
                  │
        ┌─────────┴────────────┬──────────────┐
        │                      │              │
        ▼                      ▼              ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────┐
│ RefImpl         │ │ FuzzyMatch     │ │ Custom       │
│ (Reference)    │ │ (Coordinates)  │ │              │
│                │ │                │ │              │
│ Exact/Fuzzy    │ │ GPS-based      │ │ Specialized  │
│ Text Match     │ │ Resolution     │ │ Logic        │
└────────┬───────┘ └────────┬───────┘ └──────┬───────┘
         │                  │                │
         │ Accesses         │ Accesses       │ Accesses
         ▼                  ▼                ▼
    ┌──────────────────────────────────────────┐
    │  PostgreSQL Database                     │
    │  ├─ geographic_zone                      │
    │  ├─ location_master                      │
    │  └─ geo_beneficiary_registry             │
    └──────────────────────────────────────────┘
```

#### Resolution Methods

```
1. EXACT_MATCH
   - Beneficiary ID found in beneficiary registry
   - Confidence: 100%
   - Time: O(1) - Direct lookup

2. ADDRESS_MATCH
   - Address matched against location master
   - Uses street/village + district
   - Confidence: 80-95%
   - Time: O(n) - String matching

3. FUZZY_MATCH
   - Fuzzy string matching (Levenshtein, Jaro-Winkler)
   - Handles typos and variations
   - Confidence: 70-85%
   - Time: O(n*m) - Fuzzy algorithm

4. COORDINATES_MATCH
   - GPS coordinates checked against geographic boundaries
   - Point-in-polygon test
   - Confidence: 85-98%
   - Time: O(log n) - Spatial index

5. PIN_CODE_MATCH
   - Postal code lookup
   - Limited by region size
   - Confidence: 75-90%
   - Time: O(1) - Direct lookup

6. HIERARCHICAL_MATCH
   - Match district → find state
   - Match state → find default zone
   - Confidence: 50-70%
   - Time: O(log n) - Tree traversal
```

***

### Process Flow

#### High-Level Flow

```
┌─────────────────────────────────────┐
│  New Disbursement Batch Created     │
│  - Beneficiaries: [B1, B2, B3...]   │
│  - Location Info: Address, GPS, etc │
└────────────────┬────────────────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │ Beat Producer Task   │
      │ (Every 30 minutes)   │
      └────────┬─────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query Pending Geo Resolutions      │
│  Status: PENDING_GEO_RESOLUTION     │
└────────────────┬────────────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │ For Each Batch:         │
    │ - Get beneficiaries     │
    │ - Extract location data │
    │ - Call Factory          │
    └────────┬────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  geo_resolver.resolve_geo(...)      │
│  Input: List of beneficiary locs    │
└────────────────┬────────────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │ For Each Beneficiary:    │
    │ 1. Try resolution methods│
    │ 2. Determine confidence  │
    │ 3. Select best match     │
    │ 4. Return zone mapping   │
    └────────┬─────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Save Resolutions to Database       │
│  Flag low-confidence for review     │
│  Update Batch Status                │
└────────────────┬────────────────────┘
                 │
                 ▼
    ┌──────────────────────────┐
    │ Next Phase:              │
    │ Agency/Warehouse         │
    │ Allocation               │
    └──────────────────────────┘
```

#### Detailed Resolution Flow (Per Beneficiary)

```
Input:
  - Beneficiary ID: "BENE-001"
  - Name: "Ramesh Kumar"
  - Address: "Village Chapar, Belgaum"
  - District: "Belgaum"
  - State: "Karnataka"
  - GPS: 15.8497, 75.6699

┌────────────────────────────────────────────┐
│ Step 1: Try Direct Lookup                  │
│ Query geo_beneficiary_registry              │
│ WHERE beneficiary_id = "BENE-001"          │
│ Result: Found in Belgaum District         │
└────────────────┬───────────────────────────┘
                 │
                 ├─ IF FOUND:
                 │  Confidence: 100%
                 │  Method: EXACT_MATCH
                 │  Return (State-KA, Dist-001)
                 │
                 └─ IF NOT FOUND:
                    Continue to Step 2

┌────────────────────────────────────────────┐
│ Step 2: Try Address Matching               │
│ Query location_master                      │
│ WHERE village LIKE "Chapar"                │
│   AND district LIKE "Belgaum"              │
│   AND state LIKE "Karnataka"               │
│ Result: Exact match found                 │
└────────────────┬───────────────────────────┘
                 │
                 ├─ IF EXACT:
                 │  Confidence: 95%
                 │  Method: ADDRESS_MATCH
                 │  Return mapped zones
                 │
                 └─ IF PARTIAL/FUZZY:
                    Continue to Step 3

┌────────────────────────────────────────────┐
│ Step 3: Try Coordinates Matching           │
│ IF GPS provided:                           │
│   - Check point-in-polygon for zones       │
│   - Find matching geographic boundary      │
│ Result: Coordinates in Belgaum District    │
└────────────────┬───────────────────────────┘
                 │
                 ├─ IF MATCH:
                 │  Confidence: 90%
                 │  Method: COORDINATES_MATCH
                 │  Return mapped zones
                 │
                 └─ IF NO MATCH:
                    Continue to Step 4

┌────────────────────────────────────────────┐
│ Step 4: Fuzzy Text Matching                │
│ For each location in master:               │
│   - Calculate similarity score             │
│   - Levenshtein distance < threshold       │
│ Result: "Belgaum" matches 95% similarity   │
└────────────────┬───────────────────────────┘
                 │
                 ├─ IF MATCH (>70%):
                 │  Confidence: score
                 │  Method: FUZZY_MATCH
                 │  Return mapped zones
                 │
                 └─ IF NO MATCH:
                    Continue to Step 5

┌────────────────────────────────────────────┐
│ Step 5: Hierarchical Matching              │
│ If district known:                         │
│   - Find any zone matching district        │
│ Result: Belgaum District zone found        │
└────────────────┬───────────────────────────┘
                 │
                 ├─ IF FOUND:
                 │  Confidence: 70%
                 │  Method: HIERARCHICAL_MATCH
                 │  Return zone
                 │
                 └─ IF NOT FOUND:
                    Raise Error

┌────────────────────────────────────────────┐
│ Step 6: Return Resolution                  │
│ {                                          │
│   beneficiary_id: "BENE-001",              │
│   administrative_zone_id_large: "STATE-KA",│
│   administrative_zone_id_small: "DIST-001",│
│   resolution_confidence: 95.0,             │
│   resolution_method: "ADDRESS_MATCH",      │
│   matched_location: "Belgaum District",    │
│ }                                          │
└────────────────────────────────────────────┘
```

***

### Reference Implementation

#### FarmerResolverImpl (Geo Resolution Reference)

```python
import logging
from typing import Dict, List
from difflib import SequenceMatcher
from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface import GeoResolver
from ..models import (
    GeographicZone,
    LocationMaster,
    GeoBeneficiaryRegistry,
)

_logger = logging.getLogger("farmer_resolver_impl")
_engine = get_engine()

class FarmerResolverImpl(GeoResolver):
    """
    Reference implementation of Geo Resolver.
    Uses farmer/beneficiary registry with fallback to
    address matching and fuzzy search.
    """
    
    EXACT_MATCH_CONFIDENCE = 100.0
    ADDRESS_MATCH_CONFIDENCE = 95.0
    FUZZY_MATCH_CONFIDENCE = 80.0
    COORDINATES_MATCH_CONFIDENCE = 90.0
    HIERARCHICAL_MATCH_CONFIDENCE = 70.0
    
    FUZZY_MATCH_THRESHOLD = 0.70
    
    def __init__(self):
        self.session_maker = sessionmaker(
            bind=_engine.get("db_engine"),
            expire_on_commit=False
        )
    
    def resolve_geo(
        self,
        batch_beneficiary_list: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """
        Resolve geographic zones for list of beneficiaries.
        
        Strategy:
        1. Try exact registry lookup
        2. Try address matching
        3. Try coordinate matching
        4. Try fuzzy matching
        5. Try hierarchical matching
        """
        
        _logger.info(
            f"Resolving geo for {len(batch_beneficiary_list)} beneficiaries"
        )
        
        results = []
        
        with self.session_maker() as session:
            for bene in batch_beneficiary_list:
                try:
                    resolution = self._resolve_single(session, bene)
                    if resolution:
                        results.append(resolution)
                    else:
                        _logger.warning(
                            f"Could not resolve geo for "
                            f"{bene.get('beneficiary_id')}"
                        )
                except Exception as e:
                    _logger.error(
                        f"Geo resolution error for "
                        f"{bene.get('beneficiary_id')}: {e}"
                    )
        
        return results
    
    def _resolve_single(
        self,
        session,
        bene: Dict
    ) -> Dict or None:
        """Resolve geographic zone for single beneficiary"""
        
        bene_id = bene.get('beneficiary_id')
        
        _logger.debug(f"Resolving geo for beneficiary {bene_id}")
        
        # Method 1: Exact Registry Lookup
        resolution = self._try_exact_match(session, bene)
        if resolution:
            _logger.debug(f"Exact match found for {bene_id}")
            return resolution
        
        # Method 2: Address Matching
        resolution = self._try_address_match(session, bene)
        if resolution:
            _logger.debug(f"Address match found for {bene_id}")
            return resolution
        
        # Method 3: Coordinates Matching
        if bene.get('latitude') and bene.get('longitude'):
            resolution = self._try_coordinates_match(session, bene)
            if resolution:
                _logger.debug(f"Coordinates match found for {bene_id}")
                return resolution
        
        # Method 4: Fuzzy Matching
        resolution = self._try_fuzzy_match(session, bene)
        if resolution:
            _logger.debug(f"Fuzzy match found for {bene_id}")
            return resolution
        
        # Method 5: Hierarchical Matching (fallback)
        resolution = self._try_hierarchical_match(session, bene)
        if resolution:
            _logger.debug(f"Hierarchical match found for {bene_id}")
            return resolution
        
        _logger.warning(f"No resolution found for {bene_id}")
        return None
    
    def _try_exact_match(self, session, bene: Dict) -> Dict or None:
        """Try exact registry lookup"""
        
        bene_id = bene.get('beneficiary_id')
        
        record = session.query(GeoBeneficiaryRegistry).filter(
            GeoBeneficiaryRegistry.beneficiary_id == bene_id
        ).first()
        
        if record:
            return {
                'disbursement_id': bene.get('disbursement_id'),
                'beneficiary_id': bene_id,
                'administrative_zone_id_large': record.geographic_zone_id_large,
                'administrative_zone_mnemonic_large': (
                    self._get_zone_mnemonic(session, record.geographic_zone_id_large)
                ),
                'administrative_zone_id_small': record.geographic_zone_id_small,
                'administrative_zone_mnemonic_small': (
                    self._get_zone_mnemonic(session, record.geographic_zone_id_small)
                ),
                'resolution_confidence': self.EXACT_MATCH_CONFIDENCE,
                'resolution_method': 'EXACT_MATCH',
                'matched_location': f"{record.village_name}, {record.district_name}",
            }
        
        return None
    
    def _try_address_match(self, session, bene: Dict) -> Dict or None:
        """Try address-based matching"""
        
        village = bene.get('village', '').strip()
        district = bene.get('district', '').strip()
        state = bene.get('state', '').strip()
        
        if not village or not district:
            return None
        
        # Query location master
        record = session.query(LocationMaster).filter(
            LocationMaster.village_name.ilike(f"%{village}%"),
            LocationMaster.district_name.ilike(f"%{district}%"),
        )
        
        if state:
            record = record.filter(
                LocationMaster.state_name.ilike(f"%{state}%")
            )
        
        match = record.first()
        
        if match:
            return {
                'disbursement_id': bene.get('disbursement_id'),
                'beneficiary_id': bene.get('beneficiary_id'),
                'administrative_zone_id_large': match.geographic_zone_id_large,
                'administrative_zone_mnemonic_large': (
                    self._get_zone_mnemonic(session, match.geographic_zone_id_large)
                ),
                'administrative_zone_id_small': match.geographic_zone_id_small,
                'administrative_zone_mnemonic_small': (
                    self._get_zone_mnemonic(session, match.geographic_zone_id_small)
                ),
                'resolution_confidence': self.ADDRESS_MATCH_CONFIDENCE,
                'resolution_method': 'ADDRESS_MATCH',
                'matched_location': f"{match.village_name}, {match.district_name}",
            }
        
        return None
    
    def _try_coordinates_match(self, session, bene: Dict) -> Dict or None:
        """Try GPS coordinate-based matching"""
        
        latitude = float(bene.get('latitude', 0))
        longitude = float(bene.get('longitude', 0))
        
        if latitude == 0 or longitude == 0:
            return None
        
        # Find geographic zone by point-in-polygon
        # (Simplified: just find nearest zone)
        zone = session.query(GeographicZone).filter(
            GeographicZone.zone_type == 'SMALL'
        ).order_by(
            # Distance formula (simplified)
            ((GeographicZone.centroid_latitude - latitude) ** 2 +
             (GeographicZone.centroid_longitude - longitude) ** 2).asc()
        ).first()
        
        if zone:
            # Get parent zone (large)
            parent_zone = session.query(GeographicZone).filter(
                GeographicZone.id == zone.parent_id
            ).first()
            
            return {
                'disbursement_id': bene.get('disbursement_id'),
                'beneficiary_id': bene.get('beneficiary_id'),
                'administrative_zone_id_large': parent_zone.id if parent_zone else None,
                'administrative_zone_mnemonic_large': parent_zone.mnemonic if parent_zone else None,
                'administrative_zone_id_small': zone.id,
                'administrative_zone_mnemonic_small': zone.mnemonic,
                'resolution_confidence': self.COORDINATES_MATCH_CONFIDENCE,
                'resolution_method': 'COORDINATES_MATCH',
                'matched_location': f"{zone.name}",
            }
        
        return None
    
    def _try_fuzzy_match(self, session, bene: Dict) -> Dict or None:
        """Try fuzzy string matching"""
        
        address = bene.get('address', '').strip()
        district = bene.get('district', '').strip()
        
        if not address and not district:
            return None
        
        # Get all location records
        all_locations = session.query(LocationMaster).all()
        
        best_match = None
        best_score = 0
        
        for location in all_locations:
            # Compare district names
            if district:
                score = SequenceMatcher(
                    None,
                    district.lower(),
                    location.district_name.lower()
                ).ratio()
                
                if score > best_score and score >= self.FUZZY_MATCH_THRESHOLD:
                    best_score = score
                    best_match = location
            
            # Compare full address if provided
            if address and not best_match:
                score = SequenceMatcher(
                    None,
                    address.lower(),
                    f"{location.village_name} {location.district_name}".lower()
                ).ratio()
                
                if score > best_score and score >= self.FUZZY_MATCH_THRESHOLD:
                    best_score = score
                    best_match = location
        
        if best_match:
            parent_zone = session.query(GeographicZone).filter(
                GeographicZone.id == best_match.geographic_zone_id_large
            ).first()
            
            return {
                'disbursement_id': bene.get('disbursement_id'),
                'beneficiary_id': bene.get('beneficiary_id'),
                'administrative_zone_id_large': best_match.geographic_zone_id_large,
                'administrative_zone_mnemonic_large': parent_zone.mnemonic if parent_zone else None,
                'administrative_zone_id_small': best_match.geographic_zone_id_small,
                'administrative_zone_mnemonic_small': (
                    self._get_zone_mnemonic(session, best_match.geographic_zone_id_small)
                ),
                'resolution_confidence': int(best_score * 100),
                'resolution_method': 'FUZZY_MATCH',
                'matched_location': f"{best_match.village_name}, {best_match.district_name}",
            }
        
        return None
    
    def _try_hierarchical_match(self, session, bene: Dict) -> Dict or None:
        """Fallback: hierarchical matching"""
        
        district = bene.get('district', '').strip()
        state = bene.get('state', '').strip()
        
        if not district:
            return None
        
        # Find zone by district
        zone = session.query(GeographicZone).filter(
            GeographicZone.zone_type == 'SMALL',
            GeographicZone.name.ilike(f"%{district}%")
        ).first()
        
        if zone:
            parent_zone = session.query(GeographicZone).filter(
                GeographicZone.id == zone.parent_id
            ).first()
            
            return {
                'disbursement_id': bene.get('disbursement_id'),
                'beneficiary_id': bene.get('beneficiary_id'),
                'administrative_zone_id_large': parent_zone.id if parent_zone else None,
                'administrative_zone_mnemonic_large': parent_zone.mnemonic if parent_zone else None,
                'administrative_zone_id_small': zone.id,
                'administrative_zone_mnemonic_small': zone.mnemonic,
                'resolution_confidence': self.HIERARCHICAL_MATCH_CONFIDENCE,
                'resolution_method': 'HIERARCHICAL_MATCH',
                'matched_location': zone.name,
            }
        
        return None
    
    def _get_zone_mnemonic(self, session, zone_id: str) -> str:
        """Get zone mnemonic/code"""
        
        if not zone_id:
            return None
        
        zone = session.query(GeographicZone).filter(
            GeographicZone.id == zone_id
        ).first()
        
        return zone.mnemonic if zone else None
    
    def validate_location(
        self,
        address: str,
        district: str,
        state: str,
    ) -> bool:
        """Validate if location is sufficient"""
        
        # At minimum need district
        return bool(district and district.strip())
    
    def get_resolution_confidence(
        self,
        beneficiary_id: str,
    ) -> Dict:
        """Get confidence details"""
        
        with self.session_maker() as session:
            registry_record = session.query(
                GeoBeneficiaryRegistry
            ).filter(
                GeoBeneficiaryRegistry.beneficiary_id == beneficiary_id
            ).first()
            
            if not registry_record:
                return {
                    'beneficiary_id': beneficiary_id,
                    'confidence_level': 'NOT_FOUND',
                    'confidence_score': 0,
                }
            
            return {
                'beneficiary_id': beneficiary_id,
                'confidence_level': 'HIGH',
                'confidence_score': 100,
                'resolution_method': 'EXACT_MATCH',
                'matched_zone': registry_record.geographic_zone_id_small,
            }
```

#### Key Features of Reference Implementation

1. **Multi-Method Resolution**
   * Exact registry lookup (highest confidence)
   * Address matching
   * Coordinate-based matching
   * Fuzzy string matching
   * Hierarchical fallback
2. **Confidence Scoring**
   * Different scores for different methods
   * 100% for exact matches
   * 70-95% for other methods
3. **Graceful Degradation**
   * Tries multiple methods
   * Falls back as needed
   * Returns best match found
4. **Beneficiary Registry**
   * Fast lookup if beneficiary in system
   * Geographic zone pre-mapped
   * Supports farmer/beneficiary registry
5. **Flexible Matching**
   * Case-insensitive
   * Partial matching
   * Fuzzy matching for typos

***

### Configuration

#### Environment Variables

```bash
# Geo Resolver Implementation
GEO_RESOLVER_IMPL=farmer_registry  # Options: farmer_registry, coordinate_based, custom

# Database
GEO_RESOLVER_DATABASE_URL=postgresql://user:pass@host:5432/geo_db

# Resolution Parameters
GEO_RESOLVER_FUZZY_THRESHOLD=0.70  # Minimum match threshold
GEO_RESOLVER_MIN_CONFIDENCE=60  # Minimum acceptable confidence

# Coordinate Matching
GEO_RESOLVER_MAX_DISTANCE_KM=50  # Max distance for coordinate matching
GEO_RESOLVER_USE_SPATIAL_INDEX=true  # Use PostGIS for geo queries

# Logging
GEO_RESOLVER_LOG_LEVEL=INFO
```

***

### Integration with Celery Workers

#### Celery Task (Main Bridge)

```python
@shared_task(name="geo_resolution_worker")
def geo_resolution_worker(batch_id: str):
    """Resolve geographic zones for batch beneficiaries"""
    
    session = SessionLocal()
    
    try:
        # Get all beneficiaries in batch
        beneficiaries = session.query(BatchBeneficiary).filter(
            BatchBeneficiary.batch_id == batch_id
        ).all()
        
        # Build input list
        bene_list = [
            {
                'disbursement_id': batch_id,
                'beneficiary_id': b.id,
                'name': b.name,
                'address': b.address,
                'village': b.village,
                'district': b.district,
                'state': b.state,
                'latitude': b.latitude,
                'longitude': b.longitude,
            }
            for b in beneficiaries
        ]
        
        # Get resolver
        resolver = GeoResolverFactory.get_geo_resolver()
        
        # Resolve
        resolutions = resolver.resolve_geo(bene_list)
        
        # Save resolutions
        for resolution in resolutions:
            # Find beneficiary
            bene = session.query(BatchBeneficiary).filter(
                BatchBeneficiary.id == resolution['beneficiary_id']
            ).first()
            
            if bene:
                bene.administrative_zone_id_large = (
                    resolution['administrative_zone_id_large']
                )
                bene.administrative_zone_id_small = (
                    resolution['administrative_zone_id_small']
                )
                bene.geo_resolution_confidence = (
                    resolution['resolution_confidence']
                )
                bene.geo_resolution_method = (
                    resolution['resolution_method']
                )
        
        session.commit()
        
        batch = session.query(DisbursementBatchControl).filter(
            DisbursementBatchControl.id == batch_id
        ).first()
        
        batch.geo_resolution_status = "COMPLETED"
        session.commit()
        
        return {"status": "success", "resolved": len(resolutions)}
        
    except Exception as e:
        session.rollback()
        _logger.error(f"Geo resolution failed: {e}")
        
        batch.geo_resolution_status = "FAILED"
        session.commit()
        
        return {"status": "failed", "reason": str(e)}
    
    finally:
        session.close()
```

***

### Usage Examples

#### Example 1: Basic Geo Resolution

```python
from openg2p_g2p_bridge_geo_resolver.factory import (
    GeoResolverFactory
)

resolver = GeoResolverFactory.get_geo_resolver()

beneficiaries = [
    {
        'disbursement_id': 'BATCH-001',
        'beneficiary_id': 'BENE-001',
        'village': 'Chapar',
        'district': 'Belgaum',
        'state': 'Karnataka',
        'latitude': 15.8497,
        'longitude': 75.6699,
    }
]

resolutions = resolver.resolve_geo(beneficiaries)

for res in resolutions:
    print(f"Zone: {res['administrative_zone_mnemonic_small']}")
    print(f"Confidence: {res['resolution_confidence']}%")
    print(f"Method: {res['resolution_method']}")
```

***

### Summary

**Geo Resolution** maps beneficiary locations to standard administrative zones using multiple resolution methods. The extension provides flexible, confidence-based geographic mapping essential for agency and warehouse allocation.

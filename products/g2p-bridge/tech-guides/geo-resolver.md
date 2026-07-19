---
description: Design & Implementation
---

# Geo resolver

{% hint style="info" %}
Part of writing a connector — for the end-to-end flow (implement the interface → extend the published Bridge Docker image → configure → deploy) see [How to write your own connector](../design-specifications/connectors-and-extensibility.md).
{% endhint %}

### Module Information

* **Module Name**: `openg2p-g2p-bridge-geo-resolver`
* **Location**: `/openg2p-g2p-bridge-geo-resolver/`
* **Primary Implementation**: `FarmerGeoResolverImpl`

***

### Interface Definition

**File**: `interface/geo_resolver_interface.py`

```python
class GeoResolver(BaseService):
    def resolve_geo(self, batch_beneficiary_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Resolves geographic zones for beneficiaries.
        
        Args:
            batch_beneficiary_list: List of dicts with keys:
                - disbursement_id (str)
                - beneficiary_id (str)
        
        Returns:
            List of dicts with keys:
                - disbursement_id
                - beneficiary_id
                - administrative_zone_id_large
                - administrative_zone_mnemonic_large
                - administrative_zone_id_small
                - administrative_zone_mnemonic_small
        """
        raise NotImplementedError()
```

***

### Reference Implementation: FarmerGeoResolverImpl

**File**: `implementations/farmer_resolver_impl.py`

#### Database Models Used

* `G2PFarmerRegistry` - Farmer/beneficiary registry with geographic location data

#### Algorithm

The implementation uses a **direct lookup and mapping** approach:

```
1. Extract beneficiary IDs from input list
   Result: List of beneficiary IDs to look up

2. Query farmer registry for all matching beneficiary records
   Query: G2PFarmerRegistry where link_registry_id IN beneficiary_ids
   Select: link_registry_id, large_area_id, large_area_code, 
           small_area_id, small_area_code
   Result: List of farmer details

3. Build a map for fast lookup
   Create dict: {beneficiary_id -> farmer_row}

4. For each input beneficiary:
   a. Look up in farmer map
   b. If found:
      - Create result dict with disbursement_id, beneficiary_id, 
        and both large and small area IDs/codes
      - Add to results list
   c. If not found:
      - Skip (don't add to results)

5. Return results list
   Note: Results may be smaller than input list if some beneficiaries not found
```

#### Key Characteristics

1. **Direct Database Lookup**: Uses SQLAlchemy's `select()` and `where()` with `in_()` operator
2. **Mapping-based Processing**: Builds dict for O(1) lookups after initial query
3. **Handles Missing Records**: Silently skips beneficiaries not found in registry
4. **Database Engine**: Uses registry database
   * `db_engine_registry` - Registry database for farmer/beneficiary data
5. **Logging**: Uses logger name "farmer\_geo\_resolver\_impl"

#### Return Data Structure

```python
{
    "disbursement_id": str,  # From input
    "beneficiary_id": str,   # From input
    "administrative_zone_id_large": str,       # From G2PFarmerRegistry.large_area_id
    "administrative_zone_mnemonic_large": str, # From G2PFarmerRegistry.large_area_code
    "administrative_zone_id_small": str,       # From G2PFarmerRegistry.small_area_id
    "administrative_zone_mnemonic_small": str, # From G2PFarmerRegistry.small_area_code
}
```

***

### Factory Pattern

**File**: `factory/geo_resolution_factory.py`

```python
class GeoResolutionFactory(BaseService):
    @staticmethod
    def get_geo_resolver() -> GeoResolver:
        return FarmerGeoResolverImpl.get_component()
```

***

### Database Model Details

**G2PFarmerRegistry** Fields Used:

* `link_registry_id` - Beneficiary/farmer ID (lookup key)
* `large_area_id` - State/Province ID
* `large_area_code` - State/Province code
* `small_area_id` - District/Block ID
* `small_area_code` - District/Block code

***

### Configuration

**File**: `config.py`

Standard OpenG2P configuration pattern. Database connection via Settings.

***

### Key Behaviors

1. **No Exception on Missing Beneficiaries**: If a beneficiary ID is not found in registry, it's silently skipped
2. **Order Not Preserved**: Results may not be in same order as input
3. **No Validation**: Does not validate if geographic zones exist/are valid
4. **Logging**:
   * INFO: When resolution starts, how many beneficiaries input, how many farmer details fetched
   * WARNING: When no farmer details found for provided beneficiary IDs

***

### Error Handling

* **No Exceptions Raised**: Returns empty list if no matches found (doesn't error)
* **Graceful Degradation**: Skips individual missing beneficiaries, returns partial results
* **Database Errors**: Would propagate SQLAlchemy exceptions if database connection fails

***

### Integration Notes

#### Input Format

The input is a simple list of dicts, typically coming from a disbursement batch:

```python
batch_beneficiary_list = [
    {"disbursement_id": "BATCH-001", "beneficiary_id": "BENE-123"},
    {"disbursement_id": "BATCH-001", "beneficiary_id": "BENE-456"},
    # ... more beneficiaries
]
```

#### Output Format

Returns matching records with geographic zone information, typically used for:

* Agency allocation (which agency serves this zone)
* Warehouse allocation (which warehouse serves this zone)
* Reporting and analytics

***

### Performance Considerations

1. **Single Batch Query**: All beneficiary lookups done in one DB query (efficient)
2. **Dict-based Lookup**: O(1) lookup time per beneficiary after initial query
3. **No N+1 Queries**: Uses `in_()` clause instead of looping queries

***

### Implementation Limitations/Notes

1. Silently omits beneficiaries not found in registry - caller must handle partial results
2. No de-duplication - if beneficiary appears twice in input, appears twice in output
3. Direct mapping only - no fuzzy matching or fallback strategies
4. Depends entirely on farmer registry data being present and accurate
5. No caching - queries database every time (even for same beneficiaries)

***

### Typical Celery Integration

```python
# In worker task
resolver = GeoResolverFactory.get_geo_resolver()
resolutions = resolver.resolve_geo(batch_beneficiary_list)

# Handle partial results
if len(resolutions) < len(batch_beneficiary_list):
    # Some beneficiaries not found - log/handle missing ones
    found_ids = {r['beneficiary_id'] for r in resolutions}
    missing = [b for b in batch_beneficiary_list if b['beneficiary_id'] not in found_ids]
    log.warning(f"Missing geo resolution for: {missing}")
```

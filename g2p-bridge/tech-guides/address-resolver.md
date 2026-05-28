# Address resolver

## Financial Address Resolution (SPAR) - Design and Flow Document

### Table of Contents

1. Overview
2. Purpose and Use Case
3. Interface Definition
4. Architecture and Design
5. Process Flow
6. Reference Implementation
7. Configuration
8. Error Handling
9. Integration with Celery Workers
10. Usage Examples

***

### Overview

**Financial Address Resolution (SPAR)** maps beneficiary identifiers across different systems using a centralized registry (like SPAR - Single Pool Account Registry). It enriches beneficiary records with verified bank account information, financial addresses, and identity details from authoritative sources.

**Module:** `openg2p-g2p-bridge-mapper-connectors`

***

### Purpose and Use Case

#### Why SPAR Resolution?

Different systems maintain different beneficiary identifiers:

* **G2P System:** Beneficiary ID (BENE-12345)
* **National ID System:** Aadhaar, National ID
* **Banking System:** Account Number, IFSC code
* **SPAR Registry:** Financial Account ID, Bank Details
* **Phone-based Systems:** Phone number, UPI ID

SPAR acts as authoritative source for:

* **Identity Verification** - Link multiple IDs to single person
* **Financial Information** - Verified bank account details
* **De-duplication** - Identify duplicate beneficiaries
* **Compliance** - KYC/AML verification
* **Payment Details** - Correct routing information

#### Real-World Example

```
Beneficiary Database:
├─ Bene-001
│  ├─ Name: Ramesh Kumar
│  ├─ Aadhaar: 1234-5678-9012
│  └─ Phone: 98765-43210

SPAR Resolution:
├─ Query: Aadhaar=1234-5678-9012
├─ Response:
│  ├─ SPAR ID: SPAR-A12345
│  ├─ Bank Account: 123456789012
│  ├─ IFSC Code: SBIN0001234
│  ├─ Bank Name: State Bank of India
│  ├─ Account Holder: Ramesh Kumar
│  ├─ Account Status: ACTIVE
│  ├─ KYC Status: VERIFIED
│  └─ Last Updated: 2026-05-01

Enriched Beneficiary Record:
└─ Bene-001
   ├─ Name: Ramesh Kumar
   ├─ Aadhaar: 1234-5678-9012
   ├─ Phone: 98765-43210
   ├─ Bank Account: 123456789012
   ├─ IFSC: SBIN0001234
   ├─ Bank Name: SBI
   ├─ KYC Verified: Yes
   └─ SPAR ID: SPAR-A12345
```

#### Key Questions It Answers

1. **Is the beneficiary's identity verified?**
   * KYC status
   * Document validity
   * Risk flags
2. **What is the correct payment account?**
   * Bank account number
   * IFSC code
   * Account holder name
3. **Are there duplicate beneficiaries?**
   * Same Aadhaar multiple IDs
   * Same phone multiple IDs
   * De-duplication recommendations
4. **Is account eligible for disbursement?**
   * Account status (active, dormant, closed)
   * Account type (savings, salary, etc.)
   * Risk indicators

***

### Interface Definition

#### MapperInterface

```python
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from openg2p_fastapi_common.service import BaseService

class IdentifierType(str, Enum):
    """Identifier types supported"""
    AADHAAR = "AADHAAR"  # Indian national ID
    NATIONAL_ID = "NATIONAL_ID"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "DRIVER_LICENSE"

class AccountStatus(str, Enum):
    """Bank account statuses"""
    ACTIVE = "ACTIVE"
    DORMANT = "DORMANT"
    CLOSED = "CLOSED"
    FROZEN = "FROZEN"

class KYCStatus(str, Enum):
    """KYC verification status"""
    VERIFIED = "VERIFIED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class BeneficiaryIdentifier(BaseModel):
    """Identifier for resolving beneficiary"""
    identifier_type: IdentifierType
    identifier_value: str
    identifier_source: Optional[str] = None

class SPARAccountInfo(BaseModel):
    """Account information from SPAR"""
    spar_id: str
    account_number: str
    ifsc_code: str  # IFSC for Indian banks
    bank_name: str
    account_holder_name: str
    account_type: str  # SAVING, CURRENT, SALARY, etc.
    account_status: AccountStatus
    
    # KYC Information
    kyc_status: KYCStatus
    kyc_document_type: Optional[str] = None
    kyc_document_number: Optional[str] = None
    kyc_verified_date: Optional[str] = None
    
    # Risk Information
    risk_indicators: List[str] = []  # PEP, Sanctions, etc.
    is_duplicate: bool = False
    duplicate_accounts: List[str] = []
    
    # Linked Identifiers
    linked_aadhaar: Optional[str] = None
    linked_phone: Optional[str] = None
    linked_email: Optional[str] = None
    
    # Registration
    registration_timestamp: Optional[str] = None
    last_updated: Optional[str] = None

class ResolveRequest(BaseModel):
    """Request to resolve beneficiary details"""
    beneficiary_id: str
    identifiers: List[BeneficiaryIdentifier]
    include_duplicates: bool = False
    include_risk_info: bool = True

class ResolveResponse(BaseModel):
    """Response with resolved details"""
    beneficiary_id: str
    resolution_status: str  # SUCCESS, PARTIAL, FAILED
    
    primary_account: Optional[SPARAccountInfo] = None
    alternative_accounts: List[SPARAccountInfo] = []
    
    errors: List[Dict] = []
    warnings: List[str] = []
    
    resolution_timestamp: Optional[str] = None

class MapperInterface(BaseService):
    """
    Interface for mapping beneficiary identifiers and
    enriching beneficiary records with financial details.
    """
    
    def resolve_identifiers(
        self,
        request: ResolveRequest,
    ) -> ResolveResponse:
        """
        Resolve beneficiary identifiers to get verified details.
        
        Args:
            request: Resolution request with identifiers
        
        Returns:
            ResolveResponse with account details
        
        Raises:
            BeneficiaryNotFoundError: If no match found
            MultipleMatchesError: If multiple matches found
            RegistryAccessError: If registry unavailable
        """
        raise NotImplementedError()
    
    def validate_account(
        self,
        account_number: str,
        ifsc_code: str,
        account_holder_name: str,
    ) -> bool:
        """
        Validate account details against SPAR.
        
        Args:
            account_number: Bank account number
            ifsc_code: IFSC code
            account_holder_name: Expected account holder
        
        Returns:
            True if valid and matching, False otherwise
        """
        raise NotImplementedError()
    
    def check_kyc_status(
        self,
        identifier_type: IdentifierType,
        identifier_value: str,
    ) -> KYCStatus:
        """
        Check KYC/identity verification status.
        
        Returns:
            Current KYC status
        """
        raise NotImplementedError()
    
    def check_duplicates(
        self,
        identifier_type: IdentifierType,
        identifier_value: str,
    ) -> List[Dict]:
        """
        Check for duplicate accounts/registrations.
        
        Returns:
            List of duplicate accounts if found
        """
        raise NotImplementedError()
    
    def enrich_beneficiary(
        self,
        beneficiary_data: Dict,
    ) -> Dict:
        """
        Enrich beneficiary record with SPAR data.
        
        Adds financial information to existing beneficiary data.
        
        Args:
            beneficiary_data: Existing beneficiary record
        
        Returns:
            Enriched beneficiary record with account details
        """
        raise NotImplementedError()
```

***

### Architecture and Design

#### Component Diagram

```
┌────────────────────────────────────────────┐
│  Celery Worker: mapper_resolution_worker   │
│  (in openg2p-g2p-bridge-celery-workers)   │
└──────────────────┬─────────────────────────┘
                   │
                   │ Extracts identifiers
                   │ Calls Factory
                   ▼
┌────────────────────────────────────────────┐
│  MapperFactory                             │
│  ├─ Reads environment config               │
│  └─ Returns implementation                 │
└──────────────────┬─────────────────────────┘
                   │
                   │ Returns implementation
                   ▼
┌────────────────────────────────────────────┐
│  MapperInterface                           │
│  (Abstract)                                │
└──────────────────▲─────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┐
        │                     │              │
        ▼                     ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────┐
│ SPAR Mapper      │ │ Offline Mapper   │ │ Custom   │
│ (Reference)      │ │ (Cache-based)    │ │ Mapper   │
│                  │ │                  │ │          │
│ Real-time SPAR   │ │ Pre-synced cache │ │ Specific │
│ API calls        │ │ queries          │ │ Registry │
└────────┬─────────┘ └────────┬─────────┘ └────┬─────┘
         │                    │                │
         │ Makes API calls    │ Queries cache  │ Accesses
         ▼                    ▼                ▼
    ┌──────────────────────────────────────────┐
    │  External Systems                        │
    │  ├─ SPAR API Server                      │
    │  ├─ National ID Registry                 │
    │  ├─ Bank Account Registry                │
    │  └─ KYC Database                         │
    └──────────────────────────────────────────┘
```

#### Resolution Methods

```
Method 1: AADHAAR RESOLUTION
├─ Input: Aadhaar number
├─ Query: SPAR by Aadhaar
├─ Output: Bank account, IFSC, KYC status
└─ Confidence: Very high (if linked)

Method 2: PHONE RESOLUTION
├─ Input: Phone number
├─ Query: SPAR by phone
├─ Output: Bank account, Aadhaar, KYC status
└─ Confidence: High (if unique)

Method 3: ACCOUNT VALIDATION
├─ Input: Bank account + IFSC
├─ Query: Validate in SPAR
├─ Output: Account holder, status, KYC
└─ Confidence: Very high

Method 4: MULTI-IDENTIFIER FUSION
├─ Inputs: Aadhaar + Phone + Email
├─ Cross-check consistency
├─ Resolve conflicts
└─ Return unified record
```

***

### Process Flow

#### Resolution Flow

```
Input:
  - Beneficiary ID: BENE-001
  - Aadhaar: 1234-5678-9012
  - Phone: 9876543210

┌────────────────────────────────┐
│ Step 1: Validate Inputs        │
│ - Aadhaar format valid?        │
│ - Phone format valid?          │
│ Status: Valid                  │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 2: Query SPAR by Aadhaar  │
│ GET /spar/resolve              │
│ Params: aadhaar=1234-5678-9012 │
│ Response: Found 1 match        │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 3: Validate Cross-Links   │
│ Aadhaar match returned:        │
│   Phone: 9876543210 ✓ MATCH    │
│   Email: available             │
│ Consistency: OK                │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 4: Check Duplicates       │
│ Same Aadhaar with other IDs?   │
│ Result: No duplicates found    │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 5: Verify KYC Status      │
│ KYC Status: VERIFIED           │
│ Document: Aadhaar              │
│ Valid Until: 2026-12-31        │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 6: Extract Account Info   │
│ Account: 123456789012          │
│ IFSC: SBIN0001234              │
│ Bank: State Bank of India      │
│ Status: ACTIVE                 │
│ Risk Flags: None               │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 7: Return Response        │
│ {                              │
│   status: "SUCCESS",           │
│   account: "123456789012",     │
│   ifsc: "SBIN0001234",         │
│   kyc_status: "VERIFIED",      │
│   duplicates: [],              │
│ }                              │
└────────────────────────────────┘
```

***

### Reference Implementation

#### SPARMapper (Reference)

```python
import logging
from typing import Dict, List
import requests
from datetime import datetime

from ..interface import (
    MapperInterface,
    ResolveRequest,
    ResolveResponse,
    SPARAccountInfo,
    IdentifierType,
    KYCStatus,
)
from ..config import Settings

_logger = logging.getLogger("spar_mapper")
_config = Settings.get_config()

class SPARMapper(MapperInterface):
    """
    Reference implementation connecting to SPAR registry.
    """
    
    def __init__(self):
        self.spar_api_url = _config.spar_api_url
        self.spar_api_key = _config.spar_api_key
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.spar_api_key}',
            'Content-Type': 'application/json',
        })
        return session
    
    def resolve_identifiers(
        self,
        request: ResolveRequest,
    ) -> ResolveResponse:
        """Resolve identifiers using SPAR"""
        
        _logger.info(
            f"Resolving identifiers for {request.beneficiary_id}"
        )
        
        response = ResolveResponse(
            beneficiary_id=request.beneficiary_id,
            resolution_status="PENDING",
        )
        
        try:
            # Try each identifier
            results = []
            
            for identifier in request.identifiers:
                result = self._resolve_single_identifier(
                    identifier
                )
                
                if result:
                    results.append(result)
            
            if not results:
                response.resolution_status = "FAILED"
                response.errors.append({
                    'code': 'NO_MATCH',
                    'message': 'No matching account found',
                })
                return response
            
            # Use first result as primary
            response.primary_account = results[0]
            response.alternative_accounts = results[1:]
            
            # Check for duplicates if requested
            if request.include_duplicates:
                duplicates = self._find_duplicates(
                    results[0]
                )
                if duplicates:
                    response.primary_account.duplicate_accounts = (
                        duplicates
                    )
                    response.warnings.append(
                        f"Found {len(duplicates)} duplicate accounts"
                    )
            
            response.resolution_status = "SUCCESS"
            response.resolution_timestamp = (
                datetime.now().isoformat()
            )
            
        except Exception as e:
            _logger.error(f"Resolution error: {e}")
            response.resolution_status = "FAILED"
            response.errors.append({
                'code': 'RESOLUTION_ERROR',
                'message': str(e),
            })
        
        return response
    
    def _resolve_single_identifier(
        self,
        identifier,
    ) -> SPARAccountInfo or None:
        """Resolve single identifier"""
        
        try:
            url = f"{self.spar_api_url}/resolve"
            
            payload = {
                'identifier_type': identifier.identifier_type,
                'identifier_value': identifier.identifier_value,
            }
            
            response = self.session.post(
                url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return SPARAccountInfo(
                    spar_id=data.get('spar_id'),
                    account_number=data.get('account_number'),
                    ifsc_code=data.get('ifsc_code'),
                    bank_name=data.get('bank_name'),
                    account_holder_name=data.get(
                        'account_holder_name'
                    ),
                    account_type=data.get('account_type'),
                    account_status=data.get('account_status'),
                    kyc_status=data.get('kyc_status'),
                    kyc_document_type=data.get(
                        'kyc_document_type'
                    ),
                    kyc_verified_date=data.get(
                        'kyc_verified_date'
                    ),
                    risk_indicators=data.get(
                        'risk_indicators', []
                    ),
                    linked_aadhaar=data.get('linked_aadhaar'),
                    linked_phone=data.get('linked_phone'),
                    linked_email=data.get('linked_email'),
                )
            
            else:
                _logger.warning(
                    f"SPAR lookup failed: {response.status_code}"
                )
                return None
        
        except Exception as e:
            _logger.error(f"Identifier resolution error: {e}")
            return None
    
    def validate_account(
        self,
        account_number: str,
        ifsc_code: str,
        account_holder_name: str,
    ) -> bool:
        """Validate account against SPAR"""
        
        try:
            url = f"{self.spar_api_url}/validate"
            
            response = self.session.post(
                url,
                json={
                    'account_number': account_number,
                    'ifsc_code': ifsc_code,
                    'account_holder_name': account_holder_name,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('valid', False)
            
            return False
        
        except Exception as e:
            _logger.error(f"Account validation error: {e}")
            return False
    
    def check_kyc_status(
        self,
        identifier_type: IdentifierType,
        identifier_value: str,
    ) -> KYCStatus:
        """Check KYC status"""
        
        try:
            url = f"{self.spar_api_url}/kyc/status"
            
            response = self.session.get(
                url,
                params={
                    'identifier_type': identifier_type,
                    'identifier_value': identifier_value,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json().get('status')
                return KYCStatus(status)
            
            return KYCStatus.PENDING
        
        except Exception as e:
            _logger.error(f"KYC status check error: {e}")
            return KYCStatus.PENDING
    
    def check_duplicates(
        self,
        identifier_type: IdentifierType,
        identifier_value: str,
    ) -> List[Dict]:
        """Check for duplicate accounts"""
        
        try:
            url = f"{self.spar_api_url}/duplicates"
            
            response = self.session.get(
                url,
                params={
                    'identifier_type': identifier_type,
                    'identifier_value': identifier_value,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('duplicates', [])
            
            return []
        
        except Exception as e:
            _logger.error(f"Duplicate check error: {e}")
            return []
    
    def enrich_beneficiary(
        self,
        beneficiary_data: Dict,
    ) -> Dict:
        """Enrich beneficiary with SPAR data"""
        
        # Extract identifiers
        identifiers = []
        
        if beneficiary_data.get('aadhaar'):
            identifiers.append({
                'identifier_type': 'AADHAAR',
                'identifier_value': beneficiary_data['aadhaar'],
            })
        
        if beneficiary_data.get('phone'):
            identifiers.append({
                'identifier_type': 'PHONE',
                'identifier_value': beneficiary_data['phone'],
            })
        
        # Resolve
        request = ResolveRequest(
            beneficiary_id=beneficiary_data.get('id'),
            identifiers=identifiers,
        )
        
        response = self.resolve_identifiers(request)
        
        # Enrich
        if response.primary_account:
            beneficiary_data['account_number'] = (
                response.primary_account.account_number
            )
            beneficiary_data['ifsc_code'] = (
                response.primary_account.ifsc_code
            )
            beneficiary_data['bank_name'] = (
                response.primary_account.bank_name
            )
            beneficiary_data['kyc_status'] = (
                response.primary_account.kyc_status
            )
            beneficiary_data['account_status'] = (
                response.primary_account.account_status
            )
            beneficiary_data['spar_id'] = (
                response.primary_account.spar_id
            )
        
        beneficiary_data['spar_resolution_status'] = (
            response.resolution_status
        )
        
        return beneficiary_data
    
    def _find_duplicates(
        self,
        account: SPARAccountInfo,
    ) -> List[str]:
        """Find duplicate accounts"""
        
        duplicates = []
        
        if account.linked_aadhaar:
            dups = self.check_duplicates(
                IdentifierType.AADHAAR,
                account.linked_aadhaar,
            )
            duplicates.extend(
                [d['account_number'] for d in dups]
            )
        
        return duplicates
```

***

### Configuration

```bash
# SPAR Mapper Configuration
MAPPER_IMPL=spar_mapper

# SPAR API
SPAR_API_URL=https://spar.example.gov.in/api/v1
SPAR_API_KEY=xxx-secret-key

# Cache Configuration (for offline mode)
MAPPER_CACHE_ENABLED=true
MAPPER_CACHE_TTL_HOURS=24
MAPPER_CACHE_SIZE=100000

# Resolution Settings
MAPPER_VALIDATE_KYC=true
MAPPER_CHECK_DUPLICATES=true
MAPPER_MAX_RETRIES=3

# Logging
MAPPER_LOG_LEVEL=INFO
```

***

### Integration with Celery Workers

```python
@shared_task(name="mapper_resolution_worker")
def mapper_resolution_worker(batch_id: str):
    """Resolve identifiers and enrich beneficiary data"""
    
    mapper = MapperFactory.get_mapper()
    
    beneficiaries = get_batch_beneficiaries(batch_id)
    
    for bene in beneficiaries:
        try:
            # Enrich with SPAR data
            enriched = mapper.enrich_beneficiary({
                'id': bene.id,
                'aadhaar': bene.aadhaar,
                'phone': bene.phone,
            })
            
            # Save enriched data
            save_enriched_beneficiary(enriched)
            
        except Exception as e:
            _logger.error(f"Resolution failed for {bene.id}: {e}")
            save_error(bene.id, str(e))
    
    return {"status": "complete"}
```

***

### Summary

**Financial Address Resolution (SPAR)** provides identifier mapping and beneficiary enrichment through centralized registries, enabling verified account information, KYC status, and fraud detection in disbursement workflows.

***

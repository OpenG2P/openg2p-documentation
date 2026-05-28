---
description: >-
  This guide provides details on implementing the BankConnectorInterface for
  integration with sponsor banks to support various benefit programs in the G2P
  Bridge application.
---

# Sponsor Bank connector

## Sponsor Bank Connection - Design and Flow Document

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

**Sponsor Bank Connection** abstracts the interface to the sponsor bank (the government bank account that holds disbursement funds). It handles all banking operations including checking fund availability, blocking funds for disbursement, initiating actual payments, and reconciling transactions.

**Module:** `openg2p-g2p-bridge-bank-connectors`

***

### Purpose and Use Case

#### Why Bank Connection Abstraction?

Different banks have different:

* **APIs** - REST, SOAP, proprietary protocols
* **Message Formats** - JSON, XML, MT940, CSV
* **Authentication** - API keys, OAuth, certificates
* **Workflows** - How to block, check, and disburse funds
* **Reconciliation** - Different statement formats

The abstraction allows:

* **Plug different banks** without changing core logic
* **Mock banks** for testing
* **Support multiple banks** simultaneously
* **Implement bank-specific optimizations**

#### Real-World Example

```
Government Cash Transfer Program:
├─ Sponsor Bank: State Bank of India (SBI)
│  ├─ Account: Central Government Account (001-CASH-001)
│  ├─ API: SBI Bank Connect API (REST)
│  ├─ Authentication: OAuth 2.0 with certificates
│  ├─ Fund Balance: 10 Billion INR
│  └─ Daily Disbursement Limit: 500 Million INR
│
├─ Operations:
│  ├─ Check Fund Availability
│  │  └─ Query SBI API: GET /accounts/001-CASH-001/balance
│  │
│  ├─ Block Funds (Reserve for disbursement)
│  │  └─ Call SBI API: POST /accounts/block
│  │     Response: Block reference #12345
│  │
│  ├─ Disburse to Beneficiaries
│  │  └─ For each beneficiary:
│  │     - If bank account: Internal transfer
│  │     - If phone wallet: IMPS transfer
│  │     - If postal: Cheque draft
│  │
│  └─ Reconcile Transactions
│     └─ Download MT940 statement
│        Parse and match against disbursement records
│        Report discrepancies

Bank Connector maps:
  Generic Interface → Bank-Specific API
  Business operations → Technical implementation
  Error codes → Meaningful messages
```

#### Key Questions It Answers

1. **Are sufficient funds available?**
   * Check account balance
   * Verify transaction limits
   * Validate currency/amount
2. **How to reserve funds for disbursement?**
   * Block/hold mechanism
   * Duration of block
   * Cancellation procedure
3. **How to execute payments?**
   * Direct bank transfer
   * Mobile wallet
   * Postal cheque
   * Payment gateway
4. **How to confirm payment status?**
   * Transaction reference
   * Confirmation method
   * Timeline
5. **How to reconcile with statement?**
   * Statement format
   * Matching logic
   * Discrepancy handling

***

### Interface Definition

#### BankConnectorInterface

```python
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from openg2p_fastapi_common.service import BaseService
from openg2p_g2p_bridge_models.models import (
    FundsAvailableWithBankEnum,
    FundsBlockedWithBankEnum,
)

class CheckFundsResponse(BaseModel):
    """Response from fund availability check"""
    status: FundsAvailableWithBankEnum  # AVAILABLE, PARTIALLY_AVAILABLE, NOT_AVAILABLE
    balance: float  # Available balance
    holds: float  # Amount currently held/blocked
    available_for_disbursement: float  # Balance - holds
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class BlockFundsResponse(BaseModel):
    """Response from fund blocking request"""
    status: FundsBlockedWithBankEnum  # BLOCKED, PARTIALLY_BLOCKED, FAILED
    block_reference_no: str  # Reference to track the block
    blocked_amount: float  # Actual amount blocked
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    expiry_date: Optional[str] = None  # When block expires

class DisbursementPaymentPayload(BaseModel):
    """Single payment instruction"""
    disbursement_id: str  # Unique payment ID
    remitting_account: str  # Government account number
    remitting_account_type: Optional[str] = "SAVING"  # SAVING, CURRENT, etc.
    remitting_account_branch_code: Optional[str] = None
    remitting_account_currency: str  # INR, USD, etc.
    payment_amount: float  # Amount to transfer
    funds_blocked_reference_number: str  # From block operation
    
    # Beneficiary details
    beneficiary_id: str
    beneficiary_name: Optional[str] = None
    
    # Beneficiary bank details
    beneficiary_account: Optional[str] = None  # If bank transfer
    beneficiary_account_currency: Optional[str] = None
    beneficiary_account_type: Optional[str] = None
    beneficiary_bank_code: Optional[str] = None
    beneficiary_branch_code: Optional[str] = None
    
    # Mobile wallet details
    beneficiary_mobile_wallet_provider: Optional[str] = None  # PhonePe, GooglePay, etc.
    beneficiary_phone_no: Optional[str] = None
    
    # Email wallet details
    beneficiary_email: Optional[str] = None
    beneficiary_email_wallet_provider: Optional[str] = None
    
    # Narrative/description
    disbursement_narrative: Optional[str] = None
    benefit_program_mnemonic: Optional[str] = None
    cycle_code_mnemonic: Optional[str] = None
    payment_date: str  # ISO date format

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    PENDING = "PENDING"

class PaymentResponse(BaseModel):
    """Response from payment execution"""
    status: PaymentStatus
    transaction_reference: Optional[str] = None  # Bank's reference
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class BankConnectorInterface(BaseService):
    """
    Interface for banking operations.
    
    Provides abstraction over bank-specific APIs and protocols.
    Different implementations handle different banks/APIs.
    """
    
    def check_funds(
        self,
        account_number: str,
        currency: str,
        amount: float,
    ) -> CheckFundsResponse:
        """
        Check if sufficient funds are available for disbursement.
        
        Args:
            account_number: Government account to check
            currency: Currency code (INR, USD, etc.)
            amount: Amount to check for
        
        Returns:
            CheckFundsResponse with availability status
        
        Raises:
            BankConnectionError: If bank connection fails
            InvalidAccountError: If account not found
        """
        raise NotImplementedError()
    
    def block_funds(
        self,
        account_number: str,
        currency: str,
        amount: float,
        block_duration_days: int = 7,
    ) -> BlockFundsResponse:
        """
        Block/hold funds for disbursement.
        
        This reserves funds so they can't be used elsewhere while
        disbursement is in progress.
        
        Args:
            account_number: Government account
            currency: Currency code
            amount: Amount to block
            block_duration_days: How long to hold the block
        
        Returns:
            BlockFundsResponse with block reference
        
        Raises:
            InsufficientFundsError: If funds not available
            BankConnectionError: If bank operation fails
        """
        raise NotImplementedError()
    
    def initiate_payment(
        self,
        payment_payloads: List[DisbursementPaymentPayload],
    ) -> List[PaymentResponse]:
        """
        Execute actual fund transfers to beneficiaries.
        
        Args:
            payment_payloads: List of payment instructions
        
        Returns:
            List of payment responses (one per payload)
        
        Raises:
            BankConnectionError: If bank operation fails
            PaymentFailedError: If payment cannot be executed
        """
        raise NotImplementedError()
    
    def retrieve_reconciliation_id(
        self,
        bank_reference: str,
        customer_reference: str,
        narratives: str,
    ) -> str:
        """
        Extract reconciliation/transaction ID from bank response.
        
        Banks include various data in responses. This method extracts
        the identifier needed for reconciliation.
        
        Args:
            bank_reference: Bank's transaction reference
            customer_reference: Customer reference from request
            narratives: Message text from transaction
        
        Returns:
            Extracted reconciliation ID
        """
        raise NotImplementedError()
    
    def retrieve_beneficiary_name(
        self,
        narratives: str,
    ) -> str:
        """Extract beneficiary name from bank message"""
        raise NotImplementedError()
    
    def retrieve_reversal_reason(
        self,
        narratives: str,
    ) -> str:
        """Extract reversal/failure reason from bank message"""
        raise NotImplementedError()
    
    def validate_beneficiary_account(
        self,
        account_number: str,
        beneficiary_name: str,
    ) -> bool:
        """
        Validate beneficiary account before payment.
        
        Some banks support account name verification to prevent
        sending money to wrong accounts.
        """
        raise NotImplementedError()
    
    def get_transaction_status(
        self,
        transaction_reference: str,
    ) -> Dict:
        """
        Query transaction status from bank.
        
        Returns:
            {
                'status': 'SUCCESS|PENDING|FAILED',
                'amount': float,
                'timestamp': str,
                'beneficiary_account': str,
                'narrative': str,
            }
        """
        raise NotImplementedError()
```

***

### Data Models

#### Input Models

```python
class BankAccount(BaseModel):
    """Government bank account"""
    account_number: str
    account_holder: str
    account_type: str  # SAVING, CURRENT
    currency: str
    bank_code: str

class BeneficiaryPayment(BaseModel):
    """Payment instruction for beneficiary"""
    beneficiary_id: str
    beneficiary_name: str
    
    # Different payment methods (mutually exclusive)
    bank_account: Optional[str] = None  # For bank transfer
    phone_number: Optional[str] = None  # For mobile wallet
    email: Optional[str] = None  # For email wallet
    
    amount: float
    currency: str
```

#### Output Models

```python
class PaymentResult(BaseModel):
    """Result of single payment"""
    disbursement_id: str
    beneficiary_id: str
    status: PaymentStatus
    transaction_reference: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = None

class BankReconciliationRecord(BaseModel):
    """Bank statement record for reconciliation"""
    bank_statement_date: str
    bank_reference_number: str
    transaction_date: str
    
    debit_credit: str  # DEBIT or CREDIT
    amount: float
    currency: str
    
    remitter_account: str
    remitter_name: str
    
    beneficiary_account: str
    beneficiary_name: str
    
    narrative: str
    balance_after: float
```

#### Database Models

```python
class SponsorBankTransaction(Base):
    """Record of bank transaction"""
    __tablename__ = "sponsor_bank_transaction"
    
    id = Column(String, primary_key=True)
    disbursement_id = Column(String, ForeignKey('disbursement_envelope.id'))
    
    bank_reference_number = Column(String, unique=True)
    transaction_timestamp = Column(DateTime)
    
    remitting_account = Column(String)
    remitting_amount = Column(Float)
    currency = Column(String)
    
    beneficiary_account = Column(String)
    beneficiary_id = Column(String)
    
    transaction_status = Column(String)  # SUCCESS, FAILED, PENDING
    status_code = Column(String)  # Error code if failed
    status_message = Column(String)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

class BlockedFundsRecord(Base):
    """Record of blocked/held funds"""
    __tablename__ = "blocked_funds_record"
    
    id = Column(String, primary_key=True)
    batch_id = Column(String)
    
    remitting_account = Column(String)
    blocked_amount = Column(Float)
    currency = Column(String)
    
    block_reference = Column(String, unique=True)
    block_timestamp = Column(DateTime)
    block_expiry = Column(DateTime)
    
    unblock_timestamp = Column(DateTime)  # When block released
    unblock_status = Column(String)  # RELEASED, EXPIRED, CANCELLED
```

***

### Architecture and Design

#### Component Diagram

```
┌────────────────────────────────────────────────┐
│  Celery Worker Tasks (from main bridge)        │
│  ├─ block_funds_with_bank_worker              │
│  ├─ disburse_funds_from_bank_worker           │
│  └─ check_funds_with_bank_worker              │
└──────────────────┬─────────────────────────────┘
                   │
                   │ 1. Calls Factory
                   ▼
┌────────────────────────────────────────────────┐
│  BankConnectorFactory                          │
│  ├─ Reads environment config                   │
│  └─ Returns implementation instance            │
└──────────────────┬─────────────────────────────┘
                   │
                   │ Returns implementation
                   ▼
┌────────────────────────────────────────────────┐
│  BankConnectorInterface                        │
│  (Abstract)                                    │
└──────────────────▲────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┐
        │                     │              │
        ▼                     ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────┐
│ Example Bank     │ │ SBI Bank         │ │ Custom   │
│ Connector        │ │ Connector        │ │ Bank     │
│ (Reference)      │ │ (Real)           │ │ Impl     │
│                  │ │                  │ │          │
│ Mock bank        │ │ SBI API          │ │ Specific │
│                  │ │ Integration      │ │ Bank API │
└────────┬─────────┘ └────────┬─────────┘ └────┬─────┘
         │                    │                │
         │ Makes HTTP calls   │ Makes calls    │ Makes calls
         ▼                    ▼                ▼
    ┌────────────────────────────────────────────┐
    │  External Bank Systems                     │
    │  ├─ Bank REST API                          │
    │  ├─ SFTP for statements                    │
    │  └─ Other protocols                        │
    └────────────────────────────────────────────┘
```

#### Banking Operations Workflow

```
┌──────────────────────────────────┐
│  Disbursement Batch Initiated    │
│  Amount: 100 Million INR         │
│  Beneficiaries: 1 Million        │
└────────────────┬─────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ PHASE 1: Check Funds│
        └────────┬────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│  check_funds_with_bank()         │
│  Query: Balance in account?      │
│  Response: 500 Million available │
│  Status: SUFFICIENT              │
└────────────────┬─────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ PHASE 2: Block Funds│
        └────────┬────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│  block_funds()                   │
│  Hold: 100 Million               │
│  Duration: 7 days                │
│  Reference: BLK-12345            │
│  Status: BLOCKED                 │
└────────────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ PHASE 3: Disburse    │
        │ (Batch of payments)  │
        └────────┬─────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│  initiate_payment()              │
│  For each beneficiary:           │
│  - Transfer amount               │
│  - Collect transaction reference │
│  Status: Per-beneficiary results │
└────────────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ PHASE 4: Reconcile   │
        │ (Daily/Daily)        │
        └────────┬─────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│  Reconciliation Process          │
│  1. Download bank statement      │
│  2. Parse transactions           │
│  3. Match against records        │
│  4. Report discrepancies         │
└──────────────────────────────────┘
```

***

### Process Flow

#### Fund Checking Flow

```
Input:
  - Account: "001-CASH-001"
  - Currency: "INR"
  - Amount Needed: 100,000,000

┌─────────────────────────────────┐
│ Step 1: Connect to Bank          │
│ Load credentials from config     │
│ Establish secure connection      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Step 2: Query Account Balance    │
│ API Call: GET /account/balance   │
│ Headers: Include auth token      │
│ Params: account_id, currency     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Step 3: Parse Response           │
│ {                               │
│   "balance": 500000000,         │
│   "holds": 50000000,            │
│   "available": 450000000        │
│ }                               │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Step 4: Evaluate Availability   │
│ Required: 100,000,000           │
│ Available: 450,000,000          │
│ Status: SUFFICIENT              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Step 5: Return Response          │
│ {                               │
│   "status": "AVAILABLE",        │
│   "balance": 500000000,         │
│   "holds": 50000000,            │
│   "available_for_disbursement": │
│     450000000                   │
│ }                               │
└─────────────────────────────────┘
```

#### Fund Blocking Flow

```
Input:
  - Account: "001-CASH-001"
  - Amount: 100,000,000
  - Duration: 7 days

┌────────────────────────────────┐
│ Step 1: Validate               │
│ - Account exists?              │
│ - Sufficient balance?          │
│ - Valid currency?              │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 2: Generate Block ID      │
│ Reference: BLK-20260528-00001  │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 3: Call Bank API          │
│ POST /account/block            │
│ Body: {                        │
│   "account": "001-CASH-001",  │
│   "amount": 100000000,         │
│   "reference": "BLK-...",     │
│   "expiry_days": 7            │
│ }                              │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 4: Save Block Record      │
│ Store in database:             │
│ - Block reference              │
│ - Amount blocked               │
│ - Expiry date                  │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Step 5: Return Response         │
│ {                              │
│   "status": "BLOCKED",         │
│   "block_reference_no": "..." │
│   "blocked_amount": 100000000  │
│   "expiry_date": "2026-06-04" │
│ }                              │
└────────────────────────────────┘
```

#### Payment Execution Flow

```
Input: List of DisbursementPaymentPayload

For each payment:

┌────────────────────────────────────┐
│ Step 1: Validate Payment           │
│ - Account valid?                   │
│ - Amount positive?                 │
│ - Currency matches?                │
│ - Beneficiary info complete?       │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 2: Determine Payment Method   │
│ IF bank account:                   │
│   - Use NEFT/RTGS/IMPS             │
│ ELSE IF mobile:                    │
│   - Use UPI/wallet API             │
│ ELSE IF email:                     │
│   - Use email payment service      │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 3: Build Payment Instruction  │
│ Set payment details including:     │
│ - Remitting account                │
│ - Beneficiary details              │
│ - Amount and currency              │
│ - Narrative/reference              │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 4: Submit to Bank             │
│ POST /payment/initiate             │
│ Headers: Auth, Signature           │
│ Body: Payment instruction          │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 5: Parse Response             │
│ Status: SUCCESS, ERROR, PENDING    │
│ Transaction Ref: Bank's ref        │
│ Error Code: If failed              │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 6: Save Transaction Record    │
│ Store:                             │
│ - Disbursement ID                  │
│ - Bank reference                   │
│ - Status                           │
│ - Amount and timestamp             │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Step 7: Return Response            │
│ {                                  │
│   "status": "SUCCESS",             │
│   "transaction_reference": "...",  │
│ }                                  │
└────────────────────────────────────┘
```

***

### Reference Implementation

#### ExampleBankConnector (Reference)

```python
import logging
import uuid
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth

from ..bank_interface import (
    BankConnectorInterface,
    CheckFundsResponse,
    BlockFundsResponse,
    PaymentResponse,
    PaymentStatus,
    DisbursementPaymentPayload,
)
from ..config import Settings

_logger = logging.getLogger("example_bank_connector")
_config = Settings.get_config()

class ExampleBankConnector(BankConnectorInterface):
    """
    Reference/Example implementation of Bank Connector.
    
    This is a mock implementation for testing and learning.
    Real banks would have actual API integrations.
    """
    
    def __init__(self):
        self.bank_api_url = _config.bank_api_url
        self.bank_api_key = _config.bank_api_key
        self.bank_account = _config.bank_account
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with auth"""
        session = requests.Session()
        if self.bank_api_key:
            session.headers.update({
                'Authorization': f'Bearer {self.bank_api_key}',
                'Content-Type': 'application/json',
            })
        return session
    
    def check_funds(
        self,
        account_number: str,
        currency: str,
        amount: float,
    ) -> CheckFundsResponse:
        """Check fund availability"""
        
        _logger.info(
            f"Checking funds: account={account_number}, "
            f"amount={amount} {currency}"
        )
        
        try:
            # Call bank API
            url = f"{self.bank_api_url}/accounts/{account_number}/balance"
            
            response = self.session.get(
                url,
                params={'currency': currency},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                balance = float(data.get('balance', 0))
                holds = float(data.get('holds', 0))
                available = balance - holds
                
                # Determine status
                if available >= amount:
                    status = "AVAILABLE"
                elif available > 0:
                    status = "PARTIALLY_AVAILABLE"
                else:
                    status = "NOT_AVAILABLE"
                
                _logger.info(
                    f"Fund check result: balance={balance}, "
                    f"holds={holds}, status={status}"
                )
                
                return CheckFundsResponse(
                    status=status,
                    balance=balance,
                    holds=holds,
                    available_for_disbursement=available,
                )
            
            else:
                _logger.error(
                    f"Bank API error: {response.status_code}, "
                    f"{response.text}"
                )
                return CheckFundsResponse(
                    status="NOT_AVAILABLE",
                    balance=0,
                    holds=0,
                    available_for_disbursement=0,
                    error_code=f"HTTP_{response.status_code}",
                    error_message=response.text[:100],
                )
        
        except Exception as e:
            _logger.error(f"Fund check failed: {e}")
            return CheckFundsResponse(
                status="NOT_AVAILABLE",
                balance=0,
                holds=0,
                available_for_disbursement=0,
                error_code="CONNECTION_ERROR",
                error_message=str(e),
            )
    
    def block_funds(
        self,
        account_number: str,
        currency: str,
        amount: float,
        block_duration_days: int = 7,
    ) -> BlockFundsResponse:
        """Block funds for disbursement"""
        
        _logger.info(
            f"Blocking funds: account={account_number}, "
            f"amount={amount}, duration={block_duration_days}d"
        )
        
        try:
            # Generate block reference
            block_ref = f"BLK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            
            # Call bank API
            url = f"{self.bank_api_url}/accounts/{account_number}/block"
            
            payload = {
                'amount': amount,
                'currency': currency,
                'reference': block_ref,
                'expiry_days': block_duration_days,
                'purpose': 'DISBURSEMENT',
            }
            
            response = self.session.post(
                url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get('status', 'BLOCKED')
                blocked_amount = float(data.get('blocked_amount', amount))
                
                expiry = (
                    datetime.now() + timedelta(days=block_duration_days)
                ).isoformat()
                
                _logger.info(
                    f"Funds blocked: reference={block_ref}, "
                    f"amount={blocked_amount}"
                )
                
                return BlockFundsResponse(
                    status=status,
                    block_reference_no=block_ref,
                    blocked_amount=blocked_amount,
                    expiry_date=expiry,
                )
            
            else:
                _logger.error(
                    f"Block funds error: {response.status_code}"
                )
                return BlockFundsResponse(
                    status="FAILED",
                    block_reference_no=block_ref,
                    blocked_amount=0,
                    error_code=f"HTTP_{response.status_code}",
                    error_message=response.text[:100],
                )
        
        except Exception as e:
            _logger.error(f"Fund blocking failed: {e}")
            return BlockFundsResponse(
                status="FAILED",
                block_reference_no="",
                blocked_amount=0,
                error_code="CONNECTION_ERROR",
                error_message=str(e),
            )
    
    def initiate_payment(
        self,
        payment_payloads: List[DisbursementPaymentPayload],
    ) -> List[PaymentResponse]:
        """Execute payments"""
        
        _logger.info(f"Initiating {len(payment_payloads)} payments")
        
        results = []
        
        for payload in payment_payloads:
            try:
                response = self._execute_single_payment(payload)
                results.append(response)
            except Exception as e:
                _logger.error(
                    f"Payment error for {payload.disbursement_id}: {e}"
                )
                results.append(PaymentResponse(
                    status=PaymentStatus.ERROR,
                    error_code="PROCESSING_ERROR",
                    error_message=str(e),
                ))
        
        return results
    
    def _execute_single_payment(
        self,
        payload: DisbursementPaymentPayload
    ) -> PaymentResponse:
        """Execute single payment"""
        
        # Generate transaction reference
        txn_ref = f"TXN-{uuid.uuid4().hex[:12]}"
        
        try:
            # Determine payment method
            if payload.beneficiary_account:
                endpoint = "payment/bank_transfer"
            elif payload.beneficiary_phone_no:
                endpoint = "payment/mobile_wallet"
            elif payload.beneficiary_email:
                endpoint = "payment/email_wallet"
            else:
                return PaymentResponse(
                    status=PaymentStatus.ERROR,
                    error_code="INVALID_BENEFICIARY",
                    error_message="No valid beneficiary details",
                )
            
            # Build payment instruction
            payment_data = {
                'transaction_id': txn_ref,
                'remitting_account': payload.remitting_account,
                'amount': payload.payment_amount,
                'currency': payload.remitting_account_currency,
                'beneficiary_id': payload.beneficiary_id,
                'beneficiary_name': payload.beneficiary_name,
                'blocked_reference': payload.funds_blocked_reference_number,
                'narrative': payload.disbursement_narrative,
            }
            
            if payload.beneficiary_account:
                payment_data['beneficiary_account'] = payload.beneficiary_account
            elif payload.beneficiary_phone_no:
                payment_data['beneficiary_phone'] = payload.beneficiary_phone_no
            elif payload.beneficiary_email:
                payment_data['beneficiary_email'] = payload.beneficiary_email
            
            # Call bank API
            url = f"{self.bank_api_url}/{endpoint}"
            
            response = self.session.post(
                url,
                json=payment_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                _logger.info(
                    f"Payment successful: {txn_ref}, "
                    f"amount={payload.payment_amount}"
                )
                
                return PaymentResponse(
                    status=PaymentStatus.SUCCESS,
                    transaction_reference=txn_ref,
                )
            
            elif response.status_code == 202:
                # Accepted but still processing
                return PaymentResponse(
                    status=PaymentStatus.PENDING,
                    transaction_reference=txn_ref,
                )
            
            else:
                _logger.error(
                    f"Payment failed: {response.status_code}, "
                    f"{response.text}"
                )
                return PaymentResponse(
                    status=PaymentStatus.ERROR,
                    transaction_reference=txn_ref,
                    error_code=f"HTTP_{response.status_code}",
                    error_message=response.text[:200],
                )
        
        except Exception as e:
            _logger.error(f"Payment execution error: {e}")
            return PaymentResponse(
                status=PaymentStatus.ERROR,
                error_code="EXECUTION_ERROR",
                error_message=str(e),
            )
    
    def retrieve_reconciliation_id(
        self,
        bank_reference: str,
        customer_reference: str,
        narratives: str,
    ) -> str:
        """Extract reconciliation ID"""
        
        # Different banks include this in different formats
        # This is a simple example
        return bank_reference
    
    def retrieve_beneficiary_name(
        self,
        narratives: str,
    ) -> str:
        """Extract beneficiary name from narrative"""
        
        # Parse narrative field
        parts = narratives.split('|')
        if len(parts) > 1:
            return parts[1].strip()
        return ""
    
    def retrieve_reversal_reason(
        self,
        narratives: str,
    ) -> str:
        """Extract reversal reason"""
        
        if 'FAILED' in narratives or 'REVERSED' in narratives:
            return narratives
        return ""
    
    def validate_beneficiary_account(
        self,
        account_number: str,
        beneficiary_name: str,
    ) -> bool:
        """Validate account (if bank supports it)"""
        
        try:
            url = (
                f"{self.bank_api_url}/validate/account"
            )
            
            response = self.session.post(
                url,
                json={
                    'account': account_number,
                    'name': beneficiary_name,
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get('valid', False)
            
            return False
        
        except Exception as e:
            _logger.warning(f"Account validation error: {e}")
            return True  # Continue if validation fails
    
    def get_transaction_status(
        self,
        transaction_reference: str,
    ) -> Dict:
        """Query transaction status"""
        
        try:
            url = (
                f"{self.bank_api_url}/transaction/{transaction_reference}/status"
            )
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            return {
                'status': 'UNKNOWN',
                'error': f"HTTP {response.status_code}",
            }
        
        except Exception as e:
            _logger.error(f"Status query error: {e}")
            return {
                'status': 'UNKNOWN',
                'error': str(e),
            }
```

***

### Configuration

#### Environment Variables

```bash
# Bank Connector Implementation
BANK_CONNECTOR_IMPL=example_bank  # Options: example_bank, sbi, custom

# Bank API Configuration
BANK_API_URL=https://bank.example.com/api/v1
BANK_API_KEY=your-api-key-here
BANK_ACCOUNT=001-CASH-001
BANK_CURRENCY=INR

# Timeout and Retry
BANK_API_TIMEOUT_SECONDS=10
BANK_API_MAX_RETRIES=3
BANK_API_RETRY_DELAY_SECONDS=2

# Logging
BANK_CONNECTOR_LOG_LEVEL=INFO
```

***

### Integration with Celery Workers

#### Celery Tasks

```python
@shared_task(name="block_funds_with_bank_worker")
def block_funds_with_bank_worker(batch_id: str):
    """Block funds for batch disbursement"""
    
    connector = BankConnectorFactory.get_bank_connector()
    
    batch = get_batch(batch_id)
    
    response = connector.block_funds(
        account_number=batch.remitting_account,
        currency=batch.currency,
        amount=batch.total_amount,
        block_duration_days=7,
    )
    
    # Save block reference
    batch.funds_blocked_reference = response.block_reference_no
    batch.funds_blocked_status = response.status
    save_batch(batch)
    
    return {"status": response.status}
```

***

### Summary

**Sponsor Bank Connection** provides the abstraction layer for all banking operations, enabling pluggable bank integrations without changing core disbursement logic.

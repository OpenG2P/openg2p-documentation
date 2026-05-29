---
description: Design & Implementation
---

# Sponsor Bank connector

### Bank Disbursments - Flow

<figure><img src="../../../.gitbook/assets/Flow - Digital Cash Transfers.jpg" alt=""><figcaption></figcaption></figure>

### Module Information

* **Module Name**: `openg2p-g2p-bridge-bank-connectors`
* **Location**: `/openg2p-g2p-bridge-bank-connectors/`
* **Primary Implementation**: `ExampleBankConnector`

***

### Interface Definition

**File**: `bank_interface/bank_connector_interface.py`

#### Data Models

```python
class CheckFundsResponse(BaseModel):
    status: FundsAvailableWithBankEnum  # From openg2p_g2p_bridge_models
    error_code: str

class BlockFundsResponse(BaseModel):
    status: FundsBlockedWithBankEnum  # From openg2p_g2p_bridge_models
    block_reference_no: str
    error_code: str

class DisbursementPaymentPayload(BaseModel):
    disbursement_id: str
    remitting_account: str
    remitting_account_type: Optional[str] = None
    remitting_account_branch_code: Optional[str] = None
    remitting_account_currency: str
    payment_amount: float
    funds_blocked_reference_number: str
    
    beneficiary_id: str
    beneficiary_name: Optional[str] = None
    
    # Bank account payment method
    beneficiary_account: Optional[str] = None
    beneficiary_account_currency: Optional[str] = None
    beneficiary_account_type: Optional[str] = None
    beneficiary_bank_code: Optional[str] = None
    beneficiary_branch_code: Optional[str] = None
    
    # Mobile wallet method
    beneficiary_mobile_wallet_provider: Optional[str] = None
    beneficiary_phone_no: Optional[str] = None
    
    # Email wallet method
    beneficiary_email: Optional[str] = None
    beneficiary_email_wallet_provider: Optional[str] = None
    
    # Metadata
    disbursement_narrative: Optional[str] = None
    benefit_program_mnemonic: Optional[str] = None
    cycle_code_mnemonic: Optional[str] = None
    payment_date: str

class PaymentStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

class PaymentResponse(BaseModel):
    status: PaymentStatus
    error_code: str
```

#### Interface Methods

```python
class BankConnectorInterface(BaseService):
    def check_funds(self, account_number, currency, amount) -> CheckFundsResponse:
        """Check if funds are available"""
        raise NotImplementedError()

    def block_funds(self, account_number, currency, amount) -> BlockFundsResponse:
        """Block/hold funds for disbursement"""
        raise NotImplementedError()

    def initiate_payment(self, payment_payloads: List[DisbursementPaymentPayload]) -> PaymentResponse:
        """Execute actual payment(s)"""
        raise NotImplementedError()

    def retrieve_reconciliation_id(
        self, bank_reference: str, customer_reference: str, narratives: str
    ) -> str:
        """Extract transaction ID from bank response"""
        raise NotImplementedError()

    def retrieve_beneficiary_name(self, narratives: str) -> str:
        """Extract beneficiary name from bank message"""
        raise NotImplementedError()

    def retrieve_reversal_reason(self, narratives: str) -> str:
        """Extract reversal reason from bank message"""
        raise NotImplementedError()
```

***

### Reference Implementation: ExampleBankConnector

**File**: `bank_connectors/example_bank_connector.py`

#### Key Features

1. **HTTP-Based Communication**: Uses `httpx.Client()` for HTTP requests
2. **Configuration-Driven URLs**: Bank URLs from Settings configuration
3. **Logging**: Uses logger from config: `_config.logging_default_logger_name`

#### Implementation Details

**check\_funds()**

```
Input: account_number (str), currency (str), amount (float)

Process:
1. Build request: {"account_number", "account_currency", "total_funds_needed"}
2. POST to _config.funds_available_check_url_example_bank
3. Check response status == "success"
4. Return CheckFundsResponse with appropriate status

Response Status:
- If response status == "success": FundsAvailableWithBankEnum.FUNDS_AVAILABLE
- Otherwise: (continues, exact logic cut off in provided code)
```

**block\_funds()**

`(Implementation details not fully visible in provided code excerpt)`

**initiate\_payment()**

```
Input: List[DisbursementPaymentPayload]

Process:
For each payment payload:
1. Determine payment method based on what's populated:
   - If beneficiary_account: Use bank transfer
   - Else if beneficiary_phone_no: Use mobile wallet  
   - Else if beneficiary_email: Use email wallet
   - Else: Raise error
2. Build payment instruction
3. Make HTTP request
4. Parse response
5. Return PaymentResponse

Note: Returns single PaymentResponse, not list (interface signature may be incorrect)
```

**retrieve\_reconciliation\_id(), retrieve\_beneficiary\_name(), retrieve\_reversal\_reason()**

`(Implementations not provided in code excerpt)`

***

### Factory Pattern

**File**: `bank_connectors/bank_connector_factory.py`

```python
class BankConnectorFactory(BaseService):
    @staticmethod
    def get_bank_connector() -> BankConnectorInterface:
        return ExampleBankConnector.get_component()  # Or other implementation
```

***

### Configuration

**File**: `config.py`

Configuration parameters include:

* `logging_default_logger_name` - Logger name
* `funds_available_check_url_example_bank` - URL for funds check endpoint
* And likely other bank-specific URLs (block\_funds, payment, etc.)

***

### Enums from openg2p\_g2p\_bridge\_models

The interface depends on enums defined in the models package:

* `FundsAvailableWithBankEnum` - Status for fund availability check
* `FundsBlockedWithBankEnum` - Status for fund blocking operation

Actual enum values not visible in provided code.

***

### HTTP Client Configuration

* **Library**: `httpx`
* **Method**: `POST` for requests
* **Error Handling**: `response.raise_for_status()` - raises on 4xx/5xx
* **JSON Body**: Requests sent as JSON

***

### Payment Payload Variants

The implementation supports three payment methods via different fields:

1. **Bank Account Transfer**
   * Uses: beneficiary\_account, beneficiary\_bank\_code, beneficiary\_branch\_code
2. **Mobile Wallet**
   * Uses: beneficiary\_phone\_no, beneficiary\_mobile\_wallet\_provider
3. **Email Wallet**
   * Uses: beneficiary\_email, beneficiary\_email\_wallet\_provider

Implementation logic determines which method based on which fields are populated.

***

### Response Format

#### CheckFundsResponse

```python
{
    "status": FundsAvailableWithBankEnum,
    "error_code": str
}
```

#### BlockFundsResponse

```python
{
    "status": FundsBlockedWithBankEnum,
    "block_reference_no": str,
    "error_code": str
}
```

#### PaymentResponse

```python
{
    "status": PaymentStatus,  # SUCCESS or ERROR
    "error_code": str
}
```

***

### Key Implementation Notes

1. **Single Response for Batch**: `initiate_payment()` receives `List[DisbursementPaymentPayload]` but returns single `PaymentResponse` (possible interface mismatch)
2. **HTTP Exceptions**: HTTP errors result in exceptions being raised (not caught)
3. **Error Code Handling**: All responses include error\_code field (populated on error)
4. **Configuration-Driven**: Bank endpoints loaded from configuration, allowing different banks to be configured without code changes
5. **No Transaction Tracking**: Does not track transaction IDs in response (that's handled by retrieve methods)

***

### Integration Pattern

```python
# Typical Celery worker usage
connector = BankConnectorFactory.get_bank_connector()

# Step 1: Check funds
check_response = connector.check_funds(
    account_number=batch.remitting_account,
    currency=batch.currency,
    amount=batch.total_amount
)
if check_response.status != FundsAvailableWithBankEnum.FUNDS_AVAILABLE:
    # Handle insufficient funds
    return

# Step 2: Block funds
block_response = connector.block_funds(
    account_number=batch.remitting_account,
    currency=batch.currency,
    amount=batch.total_amount
)
if block_response.status != FundsBlockedWithBankEnum.BLOCKED:
    # Handle block failure
    return

# Step 3: Execute payments
payment_payloads = [... build from beneficiaries ...]
payment_response = connector.initiate_payment(payment_payloads)
if payment_response.status != PaymentStatus.SUCCESS:
    # Handle payment failure
    return
```

***

### Error Scenarios

1. **HTTP Connection Error**: Raises httpx exception
2. **4xx/5xx Response**: Raises from `response.raise_for_status()`
3. **Missing Payment Method Fields**: Raises ValueError in payment validation
4. **Bank Response Parsing Error**: May raise JSON parsing error if response malformed

***

### Testing Notes

The "ExampleBankConnector" is meant for:

* Development/testing
* As a template for real bank implementations
* Mock responses without actual bank integration


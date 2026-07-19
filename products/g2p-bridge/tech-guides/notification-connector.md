---
description: Design & Implementation
---

# Notification connector

{% hint style="info" %}
Part of writing a connector — for the end-to-end flow (implement the interface → extend the published Bridge Docker image → configure → deploy) see [How to write your own connector](../design-specifications/connectors-and-extensibility.md).
{% endhint %}

### Module Information

* **Module Name**: `openg2p-g2p-bridge-notification-connectors`
* **Location**: `/openg2p-g2p-bridge-notification-connectors/`
* **Primary Implementation**: `NovuNotifier`

***

### Interface Definition

**File**: `interface/notification_interface.py`

```python
class NotificationInterface(BaseService):
    def send_notification(
        self,
        notification_id: str,
        payload: Any,
        notification_type: NotificationType,
        recipient: Recipient,
    ) -> None:
        """
        Send a notification to a list of recipients.
        """
        pass
```

#### Data Models

```python
class NotificationType(enum.Enum):
    AGENCY_NOTIFICATION = "AGENCY_NOTIFICATION"
    WAREHOUSE_NOTIFICATION = "WAREHOUSE_NOTIFICATION"
    BENEFICIARY_NOTIFICATION = "BENEFICIARY_NOTIFICATION"

class Recipient(BaseModel):
    recipient_id: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None

class NotificationResponseStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class NotificationResponse(BaseModel):
    notification_id: str
    response: Optional[str] = None
    status: NotificationResponseStatus
```

#### Method Parameters

* **notification\_id** (str): Unique identifier for the notification
* **payload** (Any): Custom payload to include in the notification (can be dict or any JSON-serializable object)
* **notification\_type** (NotificationType): Type of notification (AGENCY, WAREHOUSE, or BENEFICIARY)
* **recipient** (Recipient): Recipient details including email, phone, name

#### Return Value

* **NotificationResponse**: Contains notification\_id, response (str from Novu), and status (SUCCESS or FAILURE)

***

### Reference Implementation: NovuNotifier

**File**: `implementations/novu_notifier.py`

#### Integration with Novu Platform

The implementation uses the `novu_py` library to send notifications through the Novu platform.

#### Algorithm

```
1. Determine workflow_id based on notification_type
   - WAREHOUSE_NOTIFICATION -> novu_warehouse_workflow_id from config
   - AGENCY_NOTIFICATION -> novu_agency_workflow_id from config
   - BENEFICIARY_NOTIFICATION -> novu_beneficiary_workflow_id from config
   - Otherwise: Raise ValueError for unsupported type

2. Create Novu client
   - Initialize with novu_url and novu_api_key from config
   - Context manager (with statement) for resource cleanup

3. Send notification via Novu
   - Call novu.trigger() with TriggerEventRequestDto containing:
     * workflow_id: The workflow ID determined in step 1
     * payload: The custom payload passed in
     * to: recipient.recipient_email
     * overrides: Empty Overrides object

4. Check response status
   - If novu_response.result.status.value == "processed": status = SUCCESS
   - Otherwise: status = FAILURE

5. Return NotificationResponse
   - notification_id: From input parameter
   - response: String representation of novu_response.result
   - status: SUCCESS or FAILURE based on step 4
```

#### Key Characteristics

1. **Novu Client Context Manager**: Uses `with Novu(...)` for proper resource cleanup
2. **Workflow-Based**: Maps notification types to configured Novu workflow IDs
3. **Email-Based Delivery**: Currently sends to `recipient.recipient_email`
4. **Response Parsing**: Checks `novu_response.result.status.value` for success/failure determination
5. **Logging**: Uses logger name "novu\_notifier\_impl"
   * INFO: Notification sent, API key and workflow ID used, Novu response
   * No exception raising for Novu failures - returns FAILURE status instead

***

### Factory Pattern

**File**: `factory/notification_factory.py`

```python
class NotificationFactory(BaseService):
    @staticmethod
    def get_notifier() -> NotificationInterface:
        return NovuNotifier.get_component()
```

***

### Configuration

**File**: `config.py`

Configuration uses Pydantic Settings with environment variable prefix `g2p_bridge_notification_connectors_`:

```python
class Settings(BaseSettings):
    novu_url: str = "http://localhost:3000"
    novu_api_key: str = "149f3f3dff5493729136246b9454f315"
    novu_warehouse_workflow_id: str = "warehouse-notification"
    novu_agency_workflow_id: str = "agency-notification"
    novu_beneficiary_workflow_id: str = "beneficiary-notification"
```

#### Configuration Parameters

| Parameter                      | Default Value                      | Purpose                                   |
| ------------------------------ | ---------------------------------- | ----------------------------------------- |
| `novu_url`                     | `http://localhost:3000`            | Novu server URL                           |
| `novu_api_key`                 | `149f3f3dff5493729136246b9454f315` | Novu API authentication key               |
| `novu_warehouse_workflow_id`   | `warehouse-notification`           | Workflow ID for warehouse notifications   |
| `novu_agency_workflow_id`      | `agency-notification`              | Workflow ID for agency notifications      |
| `novu_beneficiary_workflow_id` | `beneficiary-notification`         | Workflow ID for beneficiary notifications |

***

### Data Models Detail

#### Recipient Model

```python
{
    "recipient_id": str,           # Unique recipient identifier
    "recipient_name": Optional[str],  # Recipient's name (optional)
    "recipient_email": Optional[str], # Email address for delivery (optional)
    "recipient_phone": Optional[str]  # Phone number (not currently used) (optional)
}
```

#### NotificationResponse Model

```python
{
    "notification_id": str,  # From input request
    "response": Optional[str],  # String representation of Novu response result
    "status": NotificationResponseStatus  # SUCCESS or FAILURE
}
```

***

### Supported Notification Types

The implementation supports three notification types via enum:

1. **AGENCY\_NOTIFICATION**
   * Uses workflow\_id from `novu_agency_workflow_id` config
   * Use case: Notifications sent to agencies/operational partners
2. **WAREHOUSE\_NOTIFICATION**
   * Uses workflow\_id from `novu_warehouse_workflow_id` config
   * Use case: Notifications sent to warehouse operators
3. **BENEFICIARY\_NOTIFICATION**
   * Uses workflow\_id from `novu_beneficiary_workflow_id` config
   * Use case: Notifications sent to direct beneficiaries

***

### Novu Integration Details

#### TriggerEventRequestDto

The implementation creates a `novu_py.TriggerEventRequestDto` with:

* **workflow\_id**: The Novu workflow to trigger
* **payload**: Custom data for the notification (dict or JSON-serializable)
* **to**: Recipient email address (recipient.recipient\_email)
* **overrides**: Empty Overrides object (no custom overrides currently set)

#### Response Handling

Novu response processing:

* Accesses `novu_response.result.status.value` to check if status is "processed"
* Returns status as SUCCESS if processed, FAILURE otherwise
* Converts entire result object to string for response field

***

### Error Handling

* **ValueError**: Raised if notification\_type is not one of the three supported types
* **Novu Exceptions**: Would propagate from novu\_py library if HTTP/network errors occur
* **Response Status Handling**: Non-"processed" statuses result in FAILURE status, not exceptions

***

### HTTP Client Configuration

* **Library**: `novu_py` (Python SDK for Novu platform)
* **Server**: Configured via `novu_url` setting
* **Authentication**: API key via `novu_api_key` setting
* **Context Manager**: Uses Python context manager for connection lifecycle

***

### Logging

All logging uses logger name: `novu_notifier_impl`

* INFO: Notification sending initiated with recipient email
* INFO: API key and workflow ID being used
* INFO: Novu response received and parsed
* DEBUG: Response details from Novu

***

### Integration Pattern

```python
# Typical Celery worker usage
from ..factory.notification_factory import NotificationFactory

notifier = NotificationFactory.get_notifier()

response = notifier.send_notification(
    notification_id="notif-12345",
    payload={
        "disbursement_id": "DISB-001",
        "amount": 1000,
        "beneficiary_name": "John Doe"
    },
    notification_type=NotificationType.BENEFICIARY_NOTIFICATION,
    recipient=Recipient(
        recipient_id="bene-123",
        recipient_name="John Doe",
        recipient_email="john@example.com"
    )
)

if response.status == NotificationResponseStatus.SUCCESS:
    # Log success, update database
    pass
else:
    # Handle failure, retry, log error
    pass
```

***

### Key Implementation Notes

1. **Email-only Delivery**: Currently only sends to `recipient.recipient_email`. Recipient phone is accepted in model but not used.
2. **Payload Flexibility**: The payload parameter is `Any` type, allowing flexible data structures
3. **No Exception on Failure**: Notification failures return FAILURE status in response rather than raising exceptions
4. **Workflow Mapping**: Notification type maps to pre-configured Novu workflow IDs, allowing different workflows per notification type
5. **Context Manager**: Novu client uses context manager to ensure proper resource cleanup
6. **Async-Compatible**: The synchronous implementation can be called from async contexts in Celery workers

***

### Limitations/Considerations

1. Only sends to email addresses; SMS/push notification support would require workflow configuration in Novu
2. No retry logic in implementation; Celery task retries would handle failed sends
3. Payload is passed as-is to Novu; no validation or transformation of payload structure
4. No tracking of notification delivery status beyond initial trigger response
5. API key is hardcoded in default config; should be overridden via environment variable in production

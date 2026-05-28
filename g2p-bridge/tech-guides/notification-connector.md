# Notification connector

## Notification Connection - Design and Flow Document

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

**Notification Connection** sends status notifications to stakeholders (beneficiaries, agencies, warehouses) through multiple channels (SMS, Email, Push, WhatsApp, etc.) about disbursement status, payments, and important updates.

**Module:** `openg2p-g2p-bridge-notification-connectors`

***

### Purpose and Use Case

#### Why Notification Abstraction?

Different stakeholders need different notification methods:

* **Beneficiaries** → SMS (basic phones), WhatsApp, In-app notifications
* **Agencies** → Email, API callbacks, Portal notifications
* **Warehouses** → Email, SMS, API webhooks
* **Administrators** → Email, Dashboards, Alerts

Different deployments prefer different channels:

* India: SMS + WhatsApp (high penetration)
* Sub-Saharan Africa: SMS + USSD (minimal data)
* Developed countries: Email + SMS (preferred)

#### Real-World Example

```
Disbursement Batch Status: Payment Successful

Notifications Sent:

1. Beneficiary (via SMS)
   "You have received INR 500 under CTP program. 
    Reference: PAY-12345. For issues: 1800-GOVHELP"

2. Agency (via Email)
   Subject: Batch BEN-001 Completed - 50k beneficiaries processed
   Body: Detailed transaction report, reconciliation status, errors

3. Warehouse (via API Webhook)
   POST /callback
   {
     "event": "batch_completed",
     "batch_id": "BEN-001",
     "warehouse_id": "WH-001",
     "beneficiaries_allocated": 25000,
     "amount": 2500000,
   }

4. Administrator (via Email + Dashboard Alert)
   Alert: Batch processing complete with 150 failed payments
   Action required: Review and reprocess
```

#### Key Questions It Answers

1. **How to notify beneficiaries?**
   * Which channel (SMS, WhatsApp, Email)?
   * What message content?
   * In which language?
2. **How to notify agencies?**
   * Detailed reports or summaries?
   * Real-time or batch notifications?
   * Which contact method?
3. **How to handle notification failures?**
   * Retry logic
   * Fallback channels
   * Alert administrators
4. **How to track notifications?**
   * Delivery status
   * Read receipts
   * Audit trail

***

### Interface Definition

#### Notification Types

```python
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from openg2p_fastapi_common.service import BaseService

class NotificationType(str, Enum):
    """Types of notifications"""
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    BATCH_INITIATED = "BATCH_INITIATED"
    BATCH_COMPLETED = "BATCH_COMPLETED"
    BATCH_FAILED = "BATCH_FAILED"
    ALLOCATION_COMPLETED = "ALLOCATION_COMPLETED"
    BATCH_SUMMARY = "BATCH_SUMMARY"

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    PUSH_NOTIFICATION = "PUSH"
    WEBHOOK = "WEBHOOK"
    USSD = "USSD"
    IVR = "IVR"

class NotificationRecipientType(str, Enum):
    """Recipient categories"""
    BENEFICIARY = "BENEFICIARY"
    AGENCY = "AGENCY"
    WAREHOUSE = "WAREHOUSE"
    ADMINISTRATOR = "ADMINISTRATOR"

class NotificationTemplate(BaseModel):
    """Notification template"""
    id: str
    name: str
    recipient_type: NotificationRecipientType
    notification_type: NotificationType
    channel: NotificationChannel
    
    subject: Optional[str] = None  # For email
    body: str  # Main message
    template_variables: List[str] = []  # Variables like {amount}, {reference}
    language: str = "en"
    
    retry_count: int = 3
    retry_delay_minutes: int = 5

class NotificationPayload(BaseModel):
    """Notification to be sent"""
    notification_id: str
    recipient_id: str  # Beneficiary/Agency/Warehouse ID
    recipient_type: NotificationRecipientType
    
    notification_type: NotificationType
    channel: NotificationChannel
    
    recipient_address: str  # Phone number, email, webhook URL
    
    template_variables: Dict[str, str]  # Variables for template
    
    priority: int = 5  # 1-10, higher = more urgent
    scheduled_time: Optional[datetime] = None  # Send at specific time
    
    retry_count: int = 0

class NotificationResponse(BaseModel):
    """Response from notification sending"""
    notification_id: str
    status: str  # SENT, FAILED, QUEUED, DELIVERED
    provider_reference: Optional[str] = None
    provider_status_code: Optional[str] = None
    provider_message: Optional[str] = None
    sent_timestamp: Optional[datetime] = None
    delivered_timestamp: Optional[datetime] = None

class NotificationConnectorInterface(BaseService):
    """
    Interface for sending notifications via various channels.
    
    Implementations handle different notification providers and methods.
    """
    
    def send_notification(
        self,
        notification: NotificationPayload,
    ) -> NotificationResponse:
        """
        Send single notification.
        
        Args:
            notification: Notification payload with all details
        
        Returns:
            NotificationResponse with delivery status
        """
        raise NotImplementedError()
    
    def send_notifications_batch(
        self,
        notifications: List[NotificationPayload],
    ) -> List[NotificationResponse]:
        """
        Send batch of notifications.
        
        Args:
            notifications: List of notification payloads
        
        Returns:
            List of responses (one per notification)
        """
        raise NotImplementedError()
    
    def get_notification_status(
        self,
        notification_id: str,
    ) -> NotificationResponse:
        """
        Query delivery status of a notification.
        
        Returns:
            Current status including delivery info
        """
        raise NotImplementedError()
    
    def validate_recipient_address(
        self,
        channel: NotificationChannel,
        address: str,
    ) -> bool:
        """
        Validate recipient address format.
        
        Args:
            channel: Notification channel (SMS, Email, etc.)
            address: Recipient address to validate
        
        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError()
    
    def get_delivery_report(
        self,
        batch_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict:
        """
        Get delivery report for a batch.
        
        Returns:
            {
                'total_sent': int,
                'successful': int,
                'failed': int,
                'pending': int,
                'by_channel': {...},
                'by_status': {...},
            }
        """
        raise NotImplementedError()
```

***

### Architecture and Design

#### Component Diagram

```
┌─────────────────────────────────────────────┐
│  Celery Workers (Main Bridge)               │
│  ├─ beneficiary_notification_worker         │
│  ├─ agency_notification_worker              │
│  └─ warehouse_notification_worker           │
└────────────────┬────────────────────────────┘
                 │
                 │ Calls Factory
                 ▼
┌─────────────────────────────────────────────┐
│  NotificationFactory                        │
│  ├─ Reads config (channels, providers)      │
│  └─ Returns implementation                  │
└────────────────┬────────────────────────────┘
                 │
                 │ Returns implementation
                 ▼
┌─────────────────────────────────────────────┐
│  NotificationConnectorInterface             │
│  (Abstract)                                 │
└────────────────▲────────────────────────────┘
                 │
        ┌────────┴────────┬──────────────┐
        │                 │              │
        ▼                 ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐
│ Multi-Channel│ │ SMS-Only     │ │ Custom   │
│ (Reference)  │ │ (Basic)      │ │ Impl     │
│              │ │              │ │          │
│ SMS, Email   │ │ SMS only     │ │ Specific │
│ WhatsApp,    │ │ for areas    │ │ channels │
│ Push, etc.   │ │ with limited │ │ only     │
│              │ │ connectivity │ │          │
└────────┬─────┘ └────────┬─────┘ └────┬─────┘
         │                │            │
         │ Calls provider │ Calls API  │ Calls API
         ▼                ▼            ▼
    ┌──────────────────────────────────────┐
    │  External Providers                  │
    │  ├─ SMS Gateway (Twilio, Local)      │
    │  ├─ Email Service (SendGrid, SES)    │
    │  ├─ WhatsApp API                     │
    │  ├─ Push Notification Service        │
    │  └─ Webhook/API callbacks            │
    └──────────────────────────────────────┘
```

#### Notification Flow

```
1. Event Triggered
   ├─ Payment successful
   ├─ Batch completed
   └─ Error occurred

2. Determine Recipients
   ├─ Beneficiary
   ├─ Agency
   ├─ Warehouse
   └─ Administrator

3. Select Channels
   ├─ Beneficiary → SMS + WhatsApp
   ├─ Agency → Email + Dashboard
   ├─ Warehouse → Email + Webhook
   └─ Admin → Email + Alert

4. Get Templates
   ├─ Load template by type
   ├─ Substitute variables
   └─ Format for channel

5. Validate Recipients
   ├─ Phone number format
   ├─ Email validity
   └─ Webhook URL format

6. Send Notifications
   ├─ Queue for sending
   ├─ Call provider APIs
   ├─ Handle failures
   └─ Track delivery

7. Monitor Delivery
   ├─ Query provider status
   ├─ Update local records
   └─ Generate reports
```

***

### Reference Implementation

```python
import logging
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests

from ..interface import (
    NotificationConnectorInterface,
    NotificationPayload,
    NotificationResponse,
    NotificationChannel,
)
from ..config import Settings

_logger = logging.getLogger("multi_channel_notification")
_config = Settings.get_config()

class MultiChannelNotificationConnector(NotificationConnectorInterface):
    """
    Reference implementation supporting multiple channels.
    """
    
    def __init__(self):
        self.sms_gateway = SMSGateway(_config.sms_provider)
        self.email_service = EmailService(_config.email_provider)
        self.webhook_client = WebhookClient()
    
    def send_notification(
        self,
        notification: NotificationPayload,
    ) -> NotificationResponse:
        """Send single notification"""
        
        _logger.info(
            f"Sending notification {notification.notification_id} "
            f"via {notification.channel}"
        )
        
        try:
            if notification.channel == NotificationChannel.SMS:
                return self._send_sms(notification)
            
            elif notification.channel == NotificationChannel.EMAIL:
                return self._send_email(notification)
            
            elif notification.channel == NotificationChannel.WHATSAPP:
                return self._send_whatsapp(notification)
            
            elif notification.channel == NotificationChannel.WEBHOOK:
                return self._send_webhook(notification)
            
            elif notification.channel == NotificationChannel.PUSH_NOTIFICATION:
                return self._send_push(notification)
            
            else:
                raise ValueError(f"Unknown channel: {notification.channel}")
        
        except Exception as e:
            _logger.error(f"Notification send failed: {e}")
            return NotificationResponse(
                notification_id=notification.notification_id,
                status="FAILED",
                provider_message=str(e),
            )
    
    def _send_sms(
        self,
        notification: NotificationPayload
    ) -> NotificationResponse:
        """Send SMS via gateway"""
        
        response = self.sms_gateway.send(
            phone_number=notification.recipient_address,
            message=notification.template_variables.get('body', ''),
            reference_id=notification.notification_id,
        )
        
        return NotificationResponse(
            notification_id=notification.notification_id,
            status=response.get('status'),
            provider_reference=response.get('provider_id'),
            provider_status_code=response.get('code'),
            sent_timestamp=datetime.now(),
        )
    
    def _send_email(
        self,
        notification: NotificationPayload
    ) -> NotificationResponse:
        """Send email via email service"""
        
        response = self.email_service.send(
            to_address=notification.recipient_address,
            subject=notification.template_variables.get('subject', ''),
            body=notification.template_variables.get('body', ''),
            reference_id=notification.notification_id,
        )
        
        return NotificationResponse(
            notification_id=notification.notification_id,
            status=response.get('status'),
            provider_reference=response.get('provider_id'),
            sent_timestamp=datetime.now(),
        )
    
    def _send_whatsapp(
        self,
        notification: NotificationPayload
    ) -> NotificationResponse:
        """Send WhatsApp message"""
        
        # Implementation would use WhatsApp API (e.g., Twilio)
        pass
    
    def _send_webhook(
        self,
        notification: NotificationPayload
    ) -> NotificationResponse:
        """Send webhook callback"""
        
        response = self.webhook_client.post(
            url=notification.recipient_address,
            payload={
                'notification_id': notification.notification_id,
                'type': notification.notification_type,
                'timestamp': datetime.now().isoformat(),
                'data': notification.template_variables,
            },
        )
        
        return NotificationResponse(
            notification_id=notification.notification_id,
            status="SENT" if response.ok else "FAILED",
            provider_status_code=str(response.status_code),
            sent_timestamp=datetime.now(),
        )
    
    def _send_push(
        self,
        notification: NotificationPayload
    ) -> NotificationResponse:
        """Send push notification"""
        
        # Implementation would use push service (e.g., FCM)
        pass
    
    def send_notifications_batch(
        self,
        notifications: List[NotificationPayload],
    ) -> List[NotificationResponse]:
        """Send batch of notifications"""
        
        results = []
        for notification in notifications:
            response = self.send_notification(notification)
            results.append(response)
        
        return results
    
    def get_notification_status(
        self,
        notification_id: str,
    ) -> NotificationResponse:
        """Query notification status"""
        
        # Would query database/provider for status
        pass
    
    def validate_recipient_address(
        self,
        channel: NotificationChannel,
        address: str,
    ) -> bool:
        """Validate recipient address"""
        
        if channel == NotificationChannel.SMS:
            return self._validate_phone(address)
        elif channel == NotificationChannel.EMAIL:
            return self._validate_email(address)
        elif channel == NotificationChannel.WEBHOOK:
            return self._validate_url(address)
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number"""
        # Remove non-digits
        digits = ''.join(c for c in phone if c.isdigit())
        return 10 <= len(digits) <= 15
    
    def _validate_email(self, email: str) -> bool:
        """Validate email"""
        return '@' in email and '.' in email
    
    def _validate_url(self, url: str) -> bool:
        """Validate webhook URL"""
        return url.startswith('http')
    
    def get_delivery_report(
        self,
        batch_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict:
        """Get delivery report"""
        
        # Query database for delivery stats
        # Return aggregated metrics
        pass
```

***

### Configuration

```bash
# Notification Implementation
NOTIFICATION_IMPL=multi_channel

# Enabled Channels
NOTIFICATION_CHANNELS=SMS,EMAIL,WHATSAPP

# SMS Gateway
SMS_PROVIDER=twilio  # or local_gateway
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=+1234567890

# Email Service
EMAIL_PROVIDER=sendgrid  # or ses, smtp
SENDGRID_API_KEY=xxx
EMAIL_FROM_ADDRESS=noreply@govpayments.org

# WhatsApp
WHATSAPP_PROVIDER=twilio  # or meta
WHATSAPP_ACCOUNT_ID=xxx

# Push Notifications
PUSH_PROVIDER=fcm  # Firebase Cloud Messaging
FCM_SERVER_KEY=xxx

# Logging
NOTIFICATION_LOG_LEVEL=INFO
```

***

### Integration with Celery Workers

```python
@shared_task(name="beneficiary_notification_worker")
def beneficiary_notification_worker(batch_id: str):
    """Send beneficiary notifications for batch"""
    
    connector = NotificationFactory.get_notification_connector()
    
    # Get beneficiaries with payments
    beneficiaries = get_batch_beneficiaries(batch_id)
    
    notifications = []
    
    for bene in beneficiaries:
        # Create notification payload
        notification = NotificationPayload(
            notification_id=f"NOTIF-{bene.id}",
            recipient_id=bene.id,
            recipient_type=NotificationRecipientType.BENEFICIARY,
            notification_type=NotificationType.PAYMENT_SUCCESS,
            channel=get_preferred_channel(bene),
            recipient_address=bene.phone or bene.email,
            template_variables={
                'amount': bene.amount,
                'reference': bene.payment_reference,
                'program': batch.program_name,
            }
        )
        notifications.append(notification)
    
    # Send batch
    responses = connector.send_notifications_batch(notifications)
    
    # Save delivery status
    for response in responses:
        save_notification_status(response)
    
    return {"sent": len(responses)}
```

***

### Summary

**Notification Connection** provides flexible, multi-channel notification delivery supporting beneficiaries, agencies, and warehouses through SMS, Email, WhatsApp, Webhooks, and other channels.

---
description: >-
  The system that runs notification workflows, channels, and inbox state.
  Novu is the default notification provider.
---

# Notification provider

The notification provider runs workflows. It chooses the channel, renders the copy, retries delivery, and stores inbox state. Product services and the staff UI do not embed it. The [connector](../connector.md) triggers it. The [client](../client.md) reads the inbox.

| Page | Covers |
| --- | --- |
| [Novu](novu.md) | Default notification provider. Commons install, secrets, workflow seeding, the trigger body, and [email and SMS](novu.md#email-and-sms) |

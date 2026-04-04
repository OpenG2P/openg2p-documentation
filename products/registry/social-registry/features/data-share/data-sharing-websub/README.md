# Data Sharing: WebSub

This feature allows for sharing of Social Registry data with partners via [WebSub](https://www.w3.org/TR/websub/) protocol.

## Features

* Uses [WebSub](https://www.w3.org/TR/websub/) protocol for delivering data.
* Allows sharing Registry data to partners, driven by predefined events in the system. Like:
  * When an Individual record is created/updated/deleted.
  * When a Group record is created/updated/deleted.
* Allows for multiple partners to be created in the system, where each partner can subscribe to one or more events.
* Automatic delivery of data when the event is triggered.
* Allows for configuring the exact JSON that is to be sent to the partner.
  * This works in the form of a JQ filter that can be applied to the original Social Registry record where only selected field data is sent to the consumer. This allows control of what data is sent to which partners.
* Allows for adding additional fields which contain cryptographically signed data.
  * Example for printing card partners, who want to include a signed JWT in the QR Code of the printed card; a new JWT field, called "qrcode", can be configured as an additional field with only specific data required on the QR Code. This JWT is signed using the private key(s) of Social Registry (generally stored in Keymanager) and can be verified using the published public key.
* Currently implemented as an Odoo Module.

## Design

{% embed url="https://miro.com/app/board/uXjVLG9O2t0=/" %}

## Guides

* [Install WebSub](../../../../../../deployment/deployment-guide/install-websub.md)
* [Configure WebSub Partner on Social Registry](user-guides/configure-websub-partner-on-social-registry.md).

## Sample WebSub Subscriber Code

* A reference implementation of a WebSub Subscriber written in FastAPI is available here.
  * [https://github.com/openg2p/openg2p-websub-print-listener](https://github.com/openg2p/openg2p-websub-print-listener)
  * This subscriber can be used to listen to WebSub events and render ID cards as PDF (based on template) and store them in S3/MinIO.

## Configuration & Source Code

* Odoo Module: [g2p\_registry\_datashare\_websub](../../../developer-zone/odoo-modules/g2p-registry-datashare-websub.md).

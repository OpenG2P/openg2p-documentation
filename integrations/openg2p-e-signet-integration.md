# eSignet Integration

## Introduction

OpenG2P can use [eSignet](https://docs.esignet.io/) for authentication. eSignet provides an [OIDC](https://openid.net/connect/) interface for authentication while connecting to the MOSIP's IDA services on the backend.

<figure><img src="https://1786418539-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FylzvZHp30DQ3rNCClELV%2Fuploads%2FGn34BnmmusJbJFjSYOAk%2FIdP%20Diagrams-Page-3.png?alt=media&#x26;token=21de4b84-f1d2-4254-a30d-9ca8a40534c8" alt=""><figcaption></figcaption></figure>

Here, OpenG2P is a Relying Party and the Authentication System is MOSIP. Learn [more](https://docs.esignet.io/integration-guides/authentication-system-integration).

## Configure OpenG2P for eSignet

Refer to the guide [Integrate MOSIP eSignet](broken-reference).

## eSignet Login

[eSignet](https://docs.esignet.io) is a [OpenID Connect](https://openid.net/connect/) implementation which aims to offer a simple yet powerful mechanism for end users to identify themselves to avail of online services and also share their profile information.

OpenG2P integrates with MOSIP IdP over eSignet for the Self Service portal registration and login. This enables any MOSIP Id holders can easily use the service of OpenG2P through the secure bio-metric and other means of authentication.

For further details refer to openg2p-auth.


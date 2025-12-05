---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Consent Management

Build a small - Consent Management Microservice - purpose built for OpenG2P

1. Generates a consent request - UI screen\
   Who is the subject - Farmer\
   What is the shared object – farmer\_register, crop\_register\
   Who is the audience - Open-CRVS, Partner\_B, Partner\_C\
   Duration of consent
2. Obtains Authentication (Consent) from Oauth Provider - Biometric, OTP etc.
3. Receives ID Token from Oauth Provider
4. Validate the signature of ID Token
5. Validate the ID token claims
6. I generate and store the ID Token Hash (not the ID Token itself)
7. I generate an Auth Context - the auth context contains the ID Token Hash
8. I generate a consent artefact - all the claims of the consent - the consent artefact contains the Auth Context
9. I generate a consent receipt - Consent Artefact signed by my Consent Management Service









\
<br>

<br>

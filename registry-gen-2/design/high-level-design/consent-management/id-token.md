---
description: ID Token - as received from ID Provider
---

# ID Token

`{`

`"@context": "https://example.org/contexts/id_token.jsonld"`

`"@type": "IDToken",`

`"iss": "https://idp.example.org",`

`"sub": "FARMER_1234",`

`"aud": "my.registry.org",`

`"amr": ["otp"],`

&#x20;`"iat": 1714555200,`

`"exp": 1714558800,`

`"auth_time": 1714555190,`

`"kid": "key-2025-01",`

`"signature": "BASE64URL(JWS_signature)"`&#x20;

`}`

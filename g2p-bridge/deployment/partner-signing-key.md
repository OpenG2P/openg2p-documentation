---
description: Steps to supply the Bridge's own outbound signing key (.p12) at install
---

# Partner Signing Key (.p12)

This is the operational how-to for the Bridge's **own outbound signing key** — the
PKCS#12 (`.p12`) it uses to sign its resolve requests to SPAR.

* For **how partner signatures work** (detached JWS, verified against keys served by
  the Partner Manager service), see the design page
  [Partner APIs → Authentication](../../products/g2p-bridge/design-specifications/partner-apis.md#authentication)
  and [PyJWTCryptoHelper](../../platform/platform-services/privacy-and-security/pyjwtcryptohelper.md).
* To **trust partners that call the Bridge**, or to **register the Bridge with SPAR**,
  see [Onboarding Partners](onboarding-partners.md).

{% hint style="danger" %}
The chart ships a **demo** key (`files/test-partner.p12`) that is **public and for
testing only**. Any real deployment MUST switch to your own key (`inline` or
`existing` mode) and set `global.testPartnerEnabled: false`.
{% endhint %}

## Where the key comes from — `g2pBridgeSigningKey.mode`

In Rancher these fields are under the **Partner Signatures** group (shown only when
**Crypto Backend = local**). The **Signing Key Source** dropdown is
`global.g2pBridgeSigningKey.mode`:

| Mode | Use for | What you provide | What the chart does |
| --- | --- | --- | --- |
| `demo` (default) | Trials / smoke tests | nothing | Mounts the bundled **public** demo `.p12`. **Not for production.** |
| `inline` | Production | The `.p12` **base64-encoded** + its password, pasted in the Rancher form | Builds the signing Secret from those values |
| `existing` | Production | The **name of a Secret** you created yourself (holding the `.p12` + password) | Mounts your Secret; creates no key material |

Related toggles in the same group:

* **Verify Partner Signatures** — `global.g2pBridgeSignatureValidationEnabled` (inbound; on by default).
* **Sign Requests to SPAR** — `global.g2pBridgeSparSignRequestsEnabled` (outbound; on by default).
* **Signing Key ID (kid)** — `global.g2pBridgeSigningKeyKid` (optional; leave empty to
  default to the certificate's SHA-256 thumbprint).

## Step 1 — Generate your own keypair

Use the helper script (RSA-2048 / RS256 — the only algorithm the Bridge and SPAR accept):

```bash
# deployment/scripts/generate-signing-keypair.sh <name> <p12-password> [common-name] [days]
./generate-signing-keypair.sh g2p-bridge 'CHANGEME-strong-password' g2p-bridge 3650
```

or with plain `openssl`:

```bash
openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 3650 -subj "/CN=g2p-bridge" \
  -keyout g2p-bridge.key.pem -out g2p-bridge.crt
openssl pkcs12 -export -inkey g2p-bridge.key.pem -in g2p-bridge.crt \
  -out g2p-bridge.p12 -passout pass:'CHANGEME-strong-password' -name g2p-bridge
```

This produces:

* **`g2p-bridge.p12`** — the private keystore (password-protected). **This is the
  secret** the Bridge signs with. Never commit it.
* **`g2p-bridge.crt`** — the public certificate (PEM). **Not secret** — this is what
  the SPAR operator onboards so SPAR can verify the Bridge (see
  [Onboarding Partners → Register the Bridge with SPAR](onboarding-partners.md#register-the-bridge-with-spar)).

## Step 2 — Feed the `.p12` to the chart

### Option A — `inline` (paste into the Rancher form)

Base64-encode the keystore and paste it into **Signing .p12 (base64)**, and its
password into **Signing .p12 Password**:

```bash
base64 -w0 g2p-bridge.p12    # macOS: base64 g2p-bridge.p12 | tr -d '\n'
```

Equivalent `values.yaml`:

```yaml
global:
  g2pBridgeSigningKey:
    mode: inline
    p12Base64: "<paste base64 of g2p-bridge.p12>"
    password: "CHANGEME-strong-password"
```

### Option B — `existing` (reference a Secret you created)

Create the Secret yourself (e.g. Rancher → Storage → Secrets, or `kubectl`), holding
the `.p12` under key `signing-key.p12` and the password under key `password`:

```bash
kubectl create secret generic my-bridge-signing-key -n <namespace> \
  --from-file=signing-key.p12=g2p-bridge.p12 \
  --from-literal=password='CHANGEME-strong-password'
```

Then point the chart at it (keys are configurable if your Secret uses different ones):

```yaml
global:
  g2pBridgeSigningKey:
    mode: existing
    secretName: my-bridge-signing-key
    secretKey: signing-key.p12       # key holding the .p12
    passwordSecretKey: password      # key holding the password
```

## Step 3 — Register the Bridge's public cert with SPAR

Signing is only half the handshake: SPAR must trust the Bridge's **public
certificate** (as `PARTNER_G2P_BRIDGE`) or it rejects the signed resolve calls. See
[Onboarding Partners → Register the Bridge with SPAR](onboarding-partners.md#register-the-bridge-with-spar).

## Switching from demo to a real key later

You can start on `demo` and move to a real key on any later `helm upgrade`: set
`g2pBridgeSigningKey.mode` to `inline`/`existing` (and provide the material), set
`global.testPartnerEnabled: false`, and re-run the upgrade. The worker picks up the
new key on restart; remember to also re-register the new public cert with SPAR
([Step 3](#step-3-register-the-bridges-public-cert-with-spar)).

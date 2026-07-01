---
description: How the G2P Bridge signs its requests, and how to supply your own key
---

# Partner Signing Key (.p12)

From `0.0.0-develop` onward the Bridge signs and verifies partner requests **in
process** (no MOSIP Keymanager) using the local crypto backend
(`global.g2pBridgeCryptoBackend: local`). There are two directions:

* **Outbound** — the Bridge **signs** its resolve requests to SPAR with its **own
  private key**, held in a **PKCS#12 (`.p12`) keystore**. SPAR verifies that
  signature against the Bridge's **public certificate** (onboarded in SPAR as
  `PARTNER_G2P_BRIDGE`).
* **Inbound** — the Bridge **verifies** partner signatures on the Partner API using
  each partner's **public certificate**, seeded into the `partner_keys` table (see
  [Onboarding partners](#onboarding-partners-inbound) below).

This page is about the **outbound signing key** — the `.p12` you install with the
chart — and the three ways to supply it.

{% hint style="danger" %}
The chart ships a **demo** key (`files/test-partner.p12`) that is **public and for
testing only**. Any real deployment MUST switch to your own key (`inline` or
`existing` mode) and set `global.testPartnerEnabled: false`.
{% endhint %}

## Choosing where the key comes from — `g2pBridgeSigningKey.mode`

In Rancher these fields are under the **Partner Signatures** group (shown only when
**Crypto Backend = local**). The **Signing Key Source** dropdown is
`global.g2pBridgeSigningKey.mode`:

| Mode | Use for | What you provide | What the chart does |
| --- | --- | --- | --- |
| `demo` (default) | Trials / smoke tests | nothing | Mounts the bundled **public** demo `.p12`. **Not for production.** |
| `inline` | Production | The `.p12` **base64-encoded** + its password, pasted in the Rancher form | Builds the signing Secret from those values |
| `existing` | Production | The **name of a Secret** you created yourself (holding the `.p12` + password) | Mounts your Secret; creates no key material |

Related toggles in the same group:

* **Verify Partner Signatures** — `global.g2pBridgeSignatureValidationEnabled` (inbound).
* **Sign Requests to SPAR** — `global.g2pBridgeSparSignRequestsEnabled` (outbound).
* **Signing Key ID (kid)** — `global.g2pBridgeSigningKeyKid` (optional; leave empty to
  default to the certificate's SHA-256 thumbprint).

## Step 1 — Generate your own keypair

Use the helper script (RSA-2048 / RS256 — the only algorithm the Bridge and SPAR
accept):

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
  you hand to SPAR so it can verify the Bridge (see [Step 3](#step-3-let-spar-trust-the-bridge)).

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

## Step 3 — Let SPAR trust the Bridge

Signing is only half the handshake: SPAR must have the Bridge's **public
certificate** onboarded as `PARTNER_G2P_BRIDGE`, or it will reject the signed resolve
calls. Add `g2p-bridge.crt` to SPAR's partner-cert seed (SPAR chart
`global.sparPartnerCerts`) — see the SPAR **Privacy & Security** / Helm docs. (The
bundled trial does this automatically with the demo cert.)

## Onboarding partners (inbound)

To make the Bridge **verify** a partner calling its Partner API, seed that partner's
public certificate into `partner_keys` via `global.g2pBridgePartnerCerts` (reference
id = `PARTNER_<MNEMONIC>`):

```yaml
global:
  g2pBridgePartnerCerts:
    - referenceId: PARTNER_MY_PSP
      publicKey: |
        -----BEGIN CERTIFICATE-----
        ...
        -----END CERTIFICATE-----
```

## Switching from demo to a real key later

You can start on `demo` and move to a real key on any later `helm upgrade`: set
`g2pBridgeSigningKey.mode` to `inline`/`existing` (and provide the material), set
`global.testPartnerEnabled: false`, and re-run the upgrade. The worker picks up the
new key on restart; remember to also onboard the new public cert in SPAR
([Step 3](#step-3-let-spar-trust-the-bridge)).

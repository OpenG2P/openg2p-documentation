---
description: >-
  Replacing and rotating the signing keys of Agri Stack: the Composite's, the
  Exchange Consent Manager's and a partner's, and what to do when a key is
  compromised.
---

# Keys

Three kinds of signing key, each changed where it lives:

| Key | Signs | Who trusts it, and how they get it |
| --- | --- | --- |
| The Composite's | Its calls to the registries, its answers to partners | Every Partner Management reads it from the Composite's JWKS URL when needed ([how](../architecture/exchange.md#how-departments-trust-it)) |
| The Exchange Consent Manager's | The consent tokens for the registries | Each department's Consent Manager reads it from the Exchange CM's JWKS URL |
| A partner's | Its requests and the consents it signs | The Exchange's Partner Management holds it, from the partner's onboarding |

Nobody enters the Composite's or the Exchange CM's key anywhere: changing it where it lives is enough.

## The Composite's key

The install generates it (Secret `agri-composite-signing`, kept on upgrades and uninstall) unless a Secret with your own key existed first.

### Rotate the generated key

1. Delete the Secret: `kubectl -n <Exchange namespace> delete secret agri-composite-signing`.
2. Upgrade the Composite release in Rancher with the same values: the chart generates a new key and `kid`.
3. Restart the Composite: `kubectl -n <Exchange namespace> rollout restart deploy/agri-composite-api`.
4. **Check:** `curl -s https://agri-composite.<Exchange domain>/.well-known/jwks.json` shows the new `kid`.

The Partner Managements pick the new key up within their cache time (5 minutes); until then a registry may refuse the Composite's calls. Rotate at a quiet time.

### Use your own key

For a key generated where your organisation keeps its keys (an EC P-256, RSA or Ed25519 key in a password-protected `.p12`):

```bash
kubectl -n <Exchange namespace> delete secret agri-composite-signing --ignore-not-found
kubectl -n <Exchange namespace> create secret generic agri-composite-signing \
  --from-file=composite.p12=./composite.p12 --from-literal=password='<p12 password>' \
  --from-literal=kid=<kid> --from-literal=algorithm=auto
kubectl -n <Exchange namespace> rollout restart deploy/agri-composite-api
```

The chart leaves a Secret it did not create alone, and a `.p12` is used before a generated key. To rotate it, repeat with the new `.p12` and a new `kid`. Before a first install, create the Secret first and the chart never generates one. Settings: [Composite chart settings: signing key](../composite/chart-settings.md#signing-key).

### An older install

An install from before the generated key holds the Composite's key in each Partner Management itself (onboarded by the former setup script). There, rotating also needs, in **every** Partner Management, a key-update request on `PARTNER_AGRI_COMPOSITE` adding the new public key and `kid` (from the JWKS URL above), approved; then revoke the old `kid` after 5 minutes.

## The Exchange Consent Manager's key

1. Create a Secret with the new `.p12` ([Production: the CM signing key](../deployment/production.md#exchange-consent-manager-signing-key)).
2. In Commons Services of the Exchange: **Signing Key Secret** the new Secret, a new **Signing Key ID**; upgrade.

The departments read the new key from the Exchange CM's JWKS URL. Consent tokens signed with the old key lapse within their lifetime (5 minutes).

## A partner's key

The partner sends its new public key and `kid`. In the Exchange's Partner Management, on the partner: **Rotate / add keys** with the new key (a key-update request), approve. Old and new keys both work until the old `kid` is revoked: revoke it (**Rotate / add keys**, tick the old key) once the partner has switched. Partner's side: [Partner Integration Guide](../partner-integration-guide.md#step-2-get-onboarded-in-partner-management).

## A compromised key

| Key | At once |
| --- | --- |
| The Composite's | Rotate it as above. An older install: also revoke the old `kid` in every Partner Management |
| The Exchange CM's | Rotate it as above; tokens signed with it lapse within 5 minutes |
| A partner's | Revoke its `kid` in the Exchange's Partner Management (or **Disable** the partner: [Managing Partners](managing-partners.md#disable-a-partner)), then add its new key |

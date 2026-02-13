# Consent-Aware data sharing

The Base Registry supports a consent governance model for data sharing, implemented through a dedicated **Consent Management microservice** rather than embedded in the registry core. When personal data is requested by an external partner, the registry does not evaluate consent locally; instead, it delegates all consent verification to the Consent Management service. Consent decisions are tied to the data subject identity, the requesting partner system, the specific data categories being shared, and an expiry period.

The registry invokes the Consent Management service in two ways:

1. **Consent records stored in the Consent Management service**\
   When the individual has previously granted consent for the same partner and data category, the registry passes the request context (subject identifier, partner identifier, data categories, and purpose) to the Consent Management service. The service validates the existing consent artefact and returns an authorization decision to the registry.
2. **Consent payload received as part of interoperable request standards**\
   Some interoperability protocols allow the consent artefact to be included directly by the requesting partner (e.g., DCI/UNDP-style payloads). In this case, the registry forwards the received consent payload to the Consent Management service. The service validates the consent, generates a canonical consent artefact and a signed consent certificate, stores them, and returns an authorization decision.

The Consent Management service issues both the **consent artefact** (the structured representation of consent intent) and the **consent certificate** (a cryptographically signed, timestamped proof of consent suitable for audit or dispute resolution). This model ensures that outbound data flows are consent-aware without the registry having to interpret consent semantics or manage signature validation.

No outbound data is shared from the registry until a **positive authorization decision** is returned by the Consent Management service. This externalized consent enforcement model simplifies the registry architecture while ensuring compliance with privacy-by-design and interoperable data exchange standards.

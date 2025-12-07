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

# Consent-Aware data sharing

The Base Registry supports a consent governance model that ensures that personal data is shared only when a valid consent artefact is in force. Consent decisions are tied to the subject identity, the requesting partner system, the data categories being shared, and an expiry period. The consent artefact can be generated using standardized consent models, and consent enforcement is integrated into data publishing flows so that no outbound data is sent without validating against stored consent records.

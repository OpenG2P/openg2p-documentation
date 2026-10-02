---
description: >-
  Guides for partners, operators and developers of Open Agri Stack: calling the
  composite, configuring it, adding a registry, testing end to end, deploying,
  and running locally.
---

# Guides

| Guide | For | Covers |
| --- | --- | --- |
| [Partner guide](partner-guide.md) | Banks, MFIs, agritechs | Joining Open Agri Stack and using it end to end: onboarding, keys, consent with a grant per registry, signing, calling a use case, reading and verifying the response |
| [Composite configuration](composite-configuration.md) | Operators, use-case authors | The composite's API, which registry APIs it calls and where that is configured, the use-case file format, failure handling, output format, settings and Helm values |
| [Adding a data source](adding-a-data-source.md) | Operators, registry teams | Adding a registry (e.g. a Livestock Registry) as a source of a use case, step by step |
| [End-to-end test from a laptop](end-to-end-test.md) | Developers, operators | Setting up a test partner and calling `loan-profile` against a cluster namespace with one script |
| [Deploying on a cluster](deployment.md) | Operators | The order and settings for commons (MDS, PM, CM), the registries and the composite; uninstalling |
| [Running the composite locally](running-the-composite-locally.md) | Developers | Running the composite and its tests on a laptop |

---
description: Release Notes. WORK IN PROGRESS
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# 1.0.0

### Release version: 1.0.0

### Release date: 30th April 2024

## Summary

SPAR Release 1.0.0 represents a fully functional **ID-Account Mapper** (one of the components of the DPI building blocks) as articulated by the [CDPI literature.](https://docs.cdpi.dev/initiatives/dpi-as-a-packaged-solution-daas/cohort-1-daas-offerings/id-account-mapper) In addition to the ID Account Mapper, the SPAR Release 1.0.0 also includes a Self Service module, using which, beneficiaries can login themselves into the SPAR Self Service system and maintain (link, unlink & modify)  a mapping between their IDs and their Financial Address (Bank Accounts, Mobile Wallets).

## Features of this release

The SPAR subsystem has 3 components, viz. openg2p-spar-mapper-api, openg2p-spar-self-service-api & openg2p-spar-self-service-ui. The features provided by these components are listed below

#### openg2p-spar-mapper-api

1. link, unlink, update and resolve REST APIs as specified by the G2PConnect specifications

#### openg2p-spar-self-service-api

1. Static persistence for Banks & Wallet Service Providers to facilitate self service maintenance of Account (Financial Address) in the Mapper
2. link, unlink, update and resolve REST APIs from a self service perspective - Consumed by the UI layer
3. link, unlink, update and resolve - Integration with mapper-api using G2PConnect APIs - Consuming the Mapper APIs
4. Integration with OIDC-OAuth2.0 based Login Providers with a Functional (or Foundational National ID)

#### openg2p-spar-self-service-ui

1. A simple user-friendly UI to facilitate beneficiaries query the ID-Account-Mapper using their ID and displaying Financial Address (Account information) against the ID
2. UI layer to facilitate construction of Financial Address (based on the construction strategy) using the Bank Codes, Branch Codes, Wallet Service Provider Codes etc.
3. Login using OIDC/OAuth2.0 based Login Providers like E-Signet, Keycloak etc. &#x20;

## Release contents

### Packaged Dockers

<table><thead><tr><th width="274">Image</th><th>Version &#x26; Link</th></tr></thead><tbody><tr><td>openg2p-spar-mapper-api</td><td>v1.0.0 Image</td></tr><tr><td>openg2p-spar-self-service-api</td><td>v1.0.0 Image</td></tr><tr><td>openg2p-spar-self-service-ui</td><td>v1.0.0 Image</td></tr></tbody></table>

### Helm Charts&#x20;

1. [Source Code](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/charts)
2. Published Charts
   1. openg2p-spar-mapper-api
   2. openg2p-spar-self-service-api
   3. openg2p-spar-self-service-ui

### Deployment

* [Deployment scripts](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/deployment)

## Source code

<table><thead><tr><th width="297.3333333333333">Github repository</th><th width="153" align="center">Version/Tag</th></tr></thead><tbody><tr><td>openg2p-spar-mapper-api</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-self-service-api</td><td align="center">v1.1.0</td></tr><tr><td>openg2p-spar-self-service-ui</td><td align="center">v1.1.0</td></tr><tr><td>openg2p-spar-mapper-test</td><td align="center">v1.1.0</td></tr><tr><td>openg2p-spar-self-service-test</td><td align="center">v1.1.0</td></tr><tr><td>openg2p-spar-deployment</td><td align="center">v1.1.0</td></tr></tbody></table>

## Build and deploy

* To build and run this release as a developer refer to the guide [here](broken-reference).
* To deploy this release on Kubernetes refer to the guide [here](broken-reference).

## Test report

* Testing methodology: Manual
* Test results

{% embed url="https://docs.google.com/spreadsheets/d/1IfBrCoYBotCzyd-yQz-kCGlZrXll4qncZMIdH9XqS1A/edit#gid=0" %}
Test Case Tracker
{% endembed %}

## Limitations and known issues

1. Release 1.0.0 has been tested with Limited scale. Extensive load testing and performance benchmarks are planned for Release 1.0.1. Jira backlogs for the same can be found here.
2. REST API security for Mapper APIs (openg2p-spar-mapper-api) - As&#x20;

For a detailed list of issues and feature development, refer here.

To file issues, contribute and discuss, refer to the [Contributing](../../community/contributing-to-openg2p.md) guide.&#x20;
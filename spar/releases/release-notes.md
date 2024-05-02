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
3. Login using OIDC-OAuth2.0 based Login Providers like E-Signet, Keycloak etc. &#x20;

## Release contents

### Packaged Dockers

<table><thead><tr><th width="276">Image</th><th>Docker Hub Link</th></tr></thead><tbody><tr><td>openg2p-spar-mapper-api</td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-api/tags">openg2p-spar-mapper-api:1.0.0</a></td></tr><tr><td>openg2p-spar-self-service-api</td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-self-service-api/tags">openg2p-spar-self-service-api:1.0.0</a></td></tr><tr><td>openg2p-spar-self-service-ui</td><td><a href="https://hub.docker.com/r/openg2p/openg2p-spar-self-service-ui">openg2p-spar-self-service-ui:1.0.0</a></td></tr></tbody></table>

### Helm Charts&#x20;

1. [Source Code](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/charts)
2. Published Charts
   1. openg2p-spar-mapper-api
   2. openg2p-spar-self-service-api
   3. openg2p-spar-self-service-ui

### Deployment

* [Deployment scripts](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/deployment)

### Source code

<table><thead><tr><th width="297.3333333333333">Github repository</th><th width="153" align="center">Version/Tag</th></tr></thead><tbody><tr><td>openg2p-spar-mapper-api</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-self-service-api</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-self-service-ui</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-mapper-test</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-self-service-test</td><td align="center">v1.0.0</td></tr><tr><td>openg2p-spar-deployment</td><td align="center">v1.0.0</td></tr></tbody></table>

### Build and deployment guides

* To build and run this release as a developer refer to the guide [here](broken-reference).
* To deploy this release on Kubernetes refer to the guide [here](broken-reference).

### API Documentation

APIs are available in Stoplight at the following links

[openg2p-spar-self-service-api](https://openg2p.stoplight.io/docs/openg2p-spar-self-service-api/b0fb6beb9cd7e-spar-self-service-api)

[openg2p-spar-mapper-api](https://openg2p.stoplight.io/docs/openg2p-spar-mapper-api/b0fb6beb9cd7e-open-g2-p-spar-account-mapper)

### Unit Testing Coverage Reports

[openg2p-spar-mapper-api](https://app.codecov.io/github/OpenG2P/openg2p-spar-mapper-api)

[openg2p-spar-self-service](https://app.codecov.io/github/OpenG2P/openg2p-spar-self-service)

[openg2p-g2pconnect-common](https://app.codecov.io/github/OpenG2P/openg2p-g2pconnect-common)

### Test report

The Release 1.0.0 Test Report can be found here

{% embed url="https://docs.google.com/spreadsheets/d/1tX9Vzp2N2XQEmpLjkzShAykEh9ZDA5zUc6SNbZxV1s8/edit?usp=drive_link" %}

## Limitations and known issues

1. Release 1.0.0 has been tested with Limited scale. Load testing and performance benchmarks are planned for Release 1.0.1.&#x20;
2. REST API security for Mapper APIs (openg2p-spar-mapper-api) - While the self-service-apis are secured using Auth tokens (from OIDC-OAuth2.0 Login Providers), the mapper-apis will need a JWS Token based authorization for partner systems. This has been described [here](https://docs.openg2p.org/spar/privacy-and-security).
3. You can find the full list of Jira issues/backlogs [here](https://openg2p.atlassian.net/jira/software/projects/SSSIM/boards/6/backlog).

&#x20;

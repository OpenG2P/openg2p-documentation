---
description: SPAR Release Notes for 1.1.0 - WIP
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

# 1.1.0 - WIP

### Release version: 1.1.0

### Release date: 1st July 2024

## Summary

SPAR Release 1.1.0 consists of the following items

1. Performance testing and benchmarking for the mapper service
2. JWT security layer for partner systems that invoke the mapper APIs - using MOSIP Key Manager

## Features of this release

#### openg2p-spar-mapper-api

1. **Performance benchmarking and measurement -** As part of this release, we conducted a detailed performance benchmarking and measurement exercise for the openg2p-spar-mapper-api microservice. The detailed approach, the list of experiments, and the results have been documented in the [Performance Benchmarking Report.](https://docs.openg2p.org/spar/development/testing/performance-testing)
2. **API security enhancement -** The APIs provided by the mapper service are designed to be used by one or more of the participants' partner systems in the openg2p benefit transfer chain. In this release, we have added a JWT security layer to these APIs to enhance security. The detailed approach for implementing this feature can be found in the [Security Layer Documentation](https://docs.openg2p.org/spar/features/privacy-and-security).

## Release contents

<table><thead><tr><th width="276">Release item</th><th>Links </th></tr></thead><tbody><tr><td><strong>SPAR source code</strong> </td><td><ul><li><a href="https://github.com/OpenG2P/openg2p-spar-mapper-api/releases/tag/v1.0.0">openg2p-spar-mapper-api:v1.0.0</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-self-service/releases/tag/v1.0.0">openg2p-spar-self-service:v1.0.0</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-self-service-ui/releases/tag/v1.0.0">openg2p-spar-self-service-ui:v1.0.0</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-deployment/releases/tag/v1.0.0">openg2p-spar-deployment:v1.0.0</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-mapper-test/releases/tag/v1.0.0">openg2p-spar-mapper-test:v1.0.0</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-self-service-test/releases/tag/v1.0.0">openg2p-spar-self-service-test:v1.0.0</a></li></ul></td></tr><tr><td><strong>Packaged dockers</strong></td><td><ul><li><a href="https://hub.docker.com/r/openg2p/openg2p-spar-mapper-api/tags">openg2p-spar-mapper-api:1.0.0</a></li><li><a href="https://hub.docker.com/r/openg2p/openg2p-spar-self-service-api/tags">openg2p-spar-self-service-api:1.0.0</a></li><li><a href="https://hub.docker.com/r/openg2p/openg2p-spar-self-service-ui">openg2p-spar-self-service-ui:1.0.0</a></li></ul></td></tr><tr><td><strong>Deployment</strong></td><td><ul><li><a href="https://github.com/OpenG2P/openg2p-spar-deployment/tree/v1.0.0/charts">Helm Charts</a></li><li><a href="https://github.com/OpenG2P/openg2p-spar-deployment/tree/v1.0.0/deployment">Deployment Scripts</a></li><li><a href="../deployment.md">Deployment documentation</a></li></ul></td></tr><tr><td><strong>Testing</strong></td><td><ul><li><p>Test coverage reports</p><ul><li><a href="https://app.codecov.io/github/OpenG2P/openg2p-spar-mapper-api">openg2p-spar-mapper-api</a></li><li><a href="https://app.codecov.io/github/OpenG2P/openg2p-spar-self-service">openg2p-spar-self-service</a></li><li><a href="https://app.codecov.io/github/OpenG2P/openg2p-g2pconnect-common">openg2p-g2pconnect-common</a></li></ul></li><li><a href="https://drive.google.com/drive/folders/1fofKFfn7yMeDvsIVq-0btJOYaq4vC7VA">Test plans</a></li><li><a href="https://docs.google.com/spreadsheets/d/1tX9Vzp2N2XQEmpLjkzShAykEh9ZDA5zUc6SNbZxV1s8/edit#gid=0">Test reports</a></li></ul></td></tr><tr><td><strong>Documentation</strong></td><td><ul><li><a href="https://docs.openg2p.org/spar">SPAR Documentation</a></li><li><p>API reference</p><ul><li><a href="https://openg2p.stoplight.io/docs/openg2p-spar-mapper-api/b0fb6beb9cd7e-open-g2-p-spar-account-mapper">SPAR Mapper API</a></li><li><a href="https://openg2p.stoplight.io/docs/openg2p-spar-self-service-api/b0fb6beb9cd7e-spar-self-service-api">SPAR Self Service API</a></li></ul></li></ul></td></tr></tbody></table>

## Deploy

To deploy this release on Kubernetes refer to the [deployment guide](../deployment.md).

## Limitations and known issues

1. Release 1.0.0 has been tested with limited scale. Load testing and performance benchmarks are planned for Release 1.1.0
2. REST API security for Mapper APIs (openg2p-spar-mapper-api) - While the self-service-apis are secured using Auth tokens (from OIDC-OAuth2.0 Login Providers), the mapper-apis will need a JWS Token based authorization for partner systems. This has been described [here](https://docs.openg2p.org/spar/privacy-and-security).
3. You can find the full list of Jira issues/backlogs [here](https://openg2p.atlassian.net/jira/software/projects/SSSIM/boards/6/backlog).

&#x20;

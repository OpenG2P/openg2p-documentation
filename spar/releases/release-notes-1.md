---
description: SPAR Release Notes for 1.1.0 - WIP
---

# 1.1.0

### Release version: 1.1.0

### Release date: TBA

## Summary

SPAR Release 1.1.0 consists of the following items

1. Performance testing and benchmarking for the mapper service
2. JWT security layer for partner systems that invoke the mapper APIs - using MOSIP Key Manager

## Features of this release

#### openg2p-spar-mapper-api

1. **Performance benchmarking and measurement -** As part of this release, we conducted a detailed performance benchmarking and measurement exercise for the openg2p-spar-mapper-api microservice. The detailed approach, the list of experiments, and the results have been documented in the [Performance Benchmarking Report.](https://docs.openg2p.org/spar/development/testing/performance-testing)
2. **API security enhancement -** The APIs provided by the mapper service are designed to be used by one or more of the participants' partner systems in the openg2p benefit transfer chain. In this release, we have added a JWT security layer to these APIs to enhance security. The detailed approach for implementing this feature can be found in the [Security Layer Documentation](https://docs.openg2p.org/spar/features/privacy-and-security).

## Release contents

<table><thead><tr><th width="276">Release item</th><th>Links </th></tr></thead><tbody><tr><td><strong>SPAR source code</strong> </td><td><ul><li></li></ul></td></tr><tr><td><strong>Packaged dockers</strong></td><td><ul><li></li></ul></td></tr><tr><td><strong>Deployment</strong></td><td><ul><li></li></ul></td></tr><tr><td><strong>Testing</strong></td><td><ul><li></li></ul></td></tr><tr><td><strong>Documentation</strong></td><td><ul><li></li></ul></td></tr></tbody></table>

## Deploy

To deploy this release on Kubernetes refer to the [deployment guide](../deployment/).

## Limitations and known issues

1. WIP

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
  tags:
    visible: true
---

# Registry Release Notes - v4.0.0

**Release Date:** 17-Apr-2026\
**Branch:** 4.0.0\
**Previous Version:**

***

## Executive Summary

OpenG2P Registry v4.x.x implements **domain agnosticism** as the core architectural principle. This version includes a **Farmer Registry Manifestation** implementation in the extensions repository, built using the extensible registry framework without modifying core platform code.

This release also includes enhancements to the core registry platform: performance optimizations, expanded authentication capabilities, enhanced data validation, and refined user management workflows.

## Key Highlights

### **Domain Agnosticism & Extensibility**

* **Farmer Registry Manifestation:** Farmer Registry implementation in the extensions repository demonstrating domain-specific customization without core platform modifications
* **Extensible Framework:** Core registry platform supports multiple domain manifestations without code duplication
* **Extension Architecture:** Organizations can implement domain-specific registries using the extension framework and core platform

### **Other Key features**

* **Functional ID generation -** The registry uses a decoupled microservice - OpenG2P ID Generator to generate unique functional ID. Whether a Register will have a functional ID or not, is configurable in the Register Metadata.
* **Multi-Provider Authentication:** The registry uses a decoupled microservice - OpenG2P IAM to interfaces with OIDC / OAuth ID Providers (for authentication & authorization). The base release includes integration with Keycloak
* **Change Requests** - All write operations into the Registers (from various channels) go through a centralized Change Request infrastructure. Change Requests need to be verified and approved before they overwrite the register
* **Version History** - All changes to a register are logged into a Version Snapshot. A detailed version history, with links to corresponding originating change requests is available for every register record.
* **Performance Optimizations:** Optimized database queries and async processing with Redis caching
* **Error Handling & Validation:** Enhanced error handling and input validation across all endpoints
* **Asynchronous Task Processing:** Celery Workers and Beat for background job processing
* **Audit & Verification Logging:** Comprehensive verification logging with audit trails and user action attribution

***

## Components of the release

### **Registry Package**

<table><thead><tr><th width="195.139404296875">Package</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Deployment Package<br>v4.x.x</td><td>openg2p-registry-deployment</td><td>The Helm deployment package (v1.0.2) bundles the registry platform runtimes into a single deployable unit. Individual runtime versions are specified in the chart values and listed below.<br><br>Each runtime component uses a distinct version tag, but the Helm package version (v1.0.2) represents the complete, tested bundle of all components.</td></tr></tbody></table>

### Registry Runtimes

These runtiimes will be deployed by the v1.0.2 Package

<table><thead><tr><th width="194.39324951171875">Component</th><th width="276">Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Registry APIs</td><td>openg2p-registry-apis</td><td>Deployed as 3 API runtimes -<br><br>1. staff-portal-api - Providing REST APIs to Registry Staff UI<br><br>2.partner-api -- Providing REST APIs to the partner ecosystem and other DPGs</td></tr><tr><td>Celery Runtimes</td><td>openg2p-registry-celery</td><td>Handles all asynchronous processing in the Registry platform.<br><br>1. Celery Beat Producer &#x26;<br>2. Celery Workers<br><br>The Beat Producer - reads the queues (tables) and emits the tasks to the Workers. The workers do the actual processing.<br><br>By design, there should be only 1 POD for the Beat Producer to ensure that the same task is not picked up by more than 1 Beat Producer.<br><br>The worker pods can be scaled suitably to handle the scale and load requirements.</td></tr></tbody></table>

### Registry Library components

These library components are packaged within the runtimes

<table><thead><tr><th width="196.78900146484375">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Registry Core</td><td>openg2p-registry-core</td><td>Core Library for the Registry Platform</td></tr><tr><td>Domain Extensions</td><td>openg2p-registry-extensions</td><td>The domain extensions that need to be applied over the core registry platform. This release contains - farmer registry extensions</td></tr></tbody></table>

### Registry Messaging Templates

<table><thead><tr><th width="199.696533203125">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Standards</td><td>openg2p-registry-standards</td><td>This repository contains the messaging template files used by the registry to provide support to messaging standards.<br><br>This release contains the Farmer Registry DCI standards<br><br><mark style="color:$primary;">These template files need to be uploaded into the registry platform as part of the configuration.</mark></td></tr></tbody></table>

### Docker - packaging scripts and manifests

<table><thead><tr><th width="199.696533203125">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Docker</td><td>openg2p-registry-docker</td><td>Provides docker creation scripts for all the registry runtimes.<br><br>The docker repository has only the develop branch.<br><br>The exact versions and manifestations are specified in a manifest file.<br><br>e.g. farmer-v1.0.2.txt inside staff-portal-api<br><br>this specifies that the registry-staff-portal-api docker has been built using the<br><br>farmer extension - some tag<br>registry-staff-portal-api - some tag<br></td></tr></tbody></table>

***

## Other Services used by Registry 4.0.0

| Service              | Helm Version                                                                       | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| IAM-Service          | [1.0.0](https://github.com/OpenG2P/openg2p-iam-service-deployment/tree/1.0.0)      | <ol><li>IAM-Service serves as the gateway for ID and Access Token Validation</li><li>IAM-Service interfaces with ID-Providers like Keycloak for the token issuance</li><li>IAM-Service also provides a library for othe OpenG2P APIs like Registry, SPAR etc. for validating the tokens</li><li>Refer to IAM Service Documentation <a href="https://docs.openg2p.org/platform/platform-services/identity-and-access-management">here</a><br></li></ol> |
| ID-Generator-Service | 1.0.0                                                                              | <ol><li>Registry service uses ID Generator service for issuance of Functional IDs</li><li>Refer to ID Generator Documentation <a href="https://docs.openg2p.org/tools/id-generator">here</a></li></ol>                                                                                                                                                                                                                                                 |
| Master Data Service  | [1.0.0](https://github.com/OpenG2P/openg2p-gen2-master-data-deployment/tree/1.0.0) | <ol><li>Registry uses Master Data Service API for Partner and Geo Lookup Data </li></ol>                                                                                                                                                                                                                                                                                                                                                               |

## Features for upcoming Releases

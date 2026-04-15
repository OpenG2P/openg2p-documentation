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

# Registry Release Notes - v1.0.2

**Release Date:** \[DATE TO BE FILLED]\
**Branch:** 1.0\
**Previous Version:**&#x20;

***

## Executive Summary

OpenG2P Registry v1.0.2 implements **domain agnosticism** as the core architectural principle. This version includes a **Farmer Registry Manifestation** implementation in the extensions repository, built using the extensible registry framework without modifying core platform code.

This release also includes enhancements to the core registry platform: performance optimizations, expanded authentication capabilities, enhanced data validation, and refined user management workflows.

## Key Highlights

### **Domain Agnosticism & Extensibility**

* **Farmer Registry Manifestation:** Farmer Registry implementation in the extensions repository demonstrating domain-specific customization without core platform modifications
* **Extensible Framework:** Core registry platform supports multiple domain manifestations without code duplication
* **Extension Architecture:** Organizations can implement domain-specific registries using the extension framework and core platform

### **Other Key features**

* **Functional ID generation -** The registry uses a decoupled microservice - OpenG2P ID Generator to generate unique functional ID. Whether a Register will have a functional ID or not, is configurable in the Register Metadata.
* **Multi-Provider Authentication:** The registry uses a decoupled microservice - OpenG2P IAM   to interfaces with OIDC / OAuth ID Providers (for authentication & authorization). The base release includes integration with Keycloak
* **Change Requests** - All write operations into the Registers (from various channels) go through a centralized Change Request infrastructure. Change Requests need to be verified and approved before they overwrite the register
* **Version History** - All changes to a register are logged into a Version Snapshot. A detailed version history, with links to corresponding originating change requests is available for every register record.
* **Performance Optimizations:** Optimized database queries and async processing with Redis caching
* **Error Handling & Validation:** Enhanced error handling and input validation across all endpoints
* **Asynchronous Task Processing:** Celery Workers and Beat for background job processing
* **Audit & Verification Logging:** Comprehensive verification logging with audit trails and user action attribution

***

## Components of the release

### **Registry Package**

<table><thead><tr><th width="195.139404296875">Package</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Deployment Package<br>v1.0.2</td><td></td><td>The Helm deployment package (v1.0.2) bundles the registry platform runtimes into a single deployable unit. Individual runtime versions are specified in the chart values and listed below. <br><br>Each runtime component uses a distinct version tag, but the Helm package version (v1.0.2) represents the complete, tested bundle of all components.</td></tr></tbody></table>

### Registry Runtimes

These runtiimes will be deployed by the v1.0.2 Package

<table><thead><tr><th width="194.39324951171875">Component</th><th width="276">Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Registry APIs</td><td></td><td>Deployed as 3 API runtimes - <br><br>1. staff-portal-api - Providing REST APIs to Registry Staff UI<br><br>2.partner-api -- Providing REST APIs to the partner ecosystem and other DPGs</td></tr><tr><td>Celery Runtimes</td><td></td><td>Handles all asynchronous processing in the Registry platform.<br><br>1. Celery Beat Producer &#x26;<br>2. Celery Workers<br><br>The Beat Producer - reads the queues (tables) and emits the tasks to the Workers. The workers do the actual processing.<br><br>By design, there should be only 1 POD for the Beat Producer to ensure that the same task is not picked up by more than 1 Beat Producer.<br><br>The worker pods can be scaled suitably to handle the scale and load requirements.</td></tr></tbody></table>

### Registry Library components&#x20;

These library components are packaged within the runtimes

<table><thead><tr><th width="196.78900146484375">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Registry Core</td><td></td><td>Core Library for the Registry Platform</td></tr><tr><td>Domain Extensions</td><td></td><td>The domain extensions that need to be applied over the core registry platform. This release contains - farmer registry extensions</td></tr></tbody></table>

### Registry Messaging Templates

<table><thead><tr><th width="199.696533203125">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Standards</td><td></td><td>This repository contains the messaging template files used by the registry to provide support to messaging standards.<br><br>This release contains the Farmer Registry DCI standards<br><br><mark style="color:$primary;">These template files need to be uploaded into the registry platform as part of the configuration.</mark></td></tr></tbody></table>

### Other Registry Components

<table><thead><tr><th width="199.696533203125">Component</th><th>Repository</th><th>Remarks</th></tr></thead><tbody><tr><td>Docker</td><td></td><td>Provides docker creation scripts for all the registry runtimes.<br><br>The docker repository has only the develop branch.<br><br>The exact versions and manifestations are specified in a manifest file.<br><br>e.g. farmer-v1.0.2.txt inside staff-portal-api<br><br>this specifies that the registry-staff-portal-api docker has been built using the <br><br>farmer extension - some tag<br>registry-staff-portal-api - some tag<br></td></tr></tbody></table>

IAM

ID Generator

Master Data

* **Registry Core Library**\
  [openg2p-registry-gen2-core](https://github.com/openg2p/openg2p-registry-gen2-core/releases/tag/v1.0.2)
* **Registry Extensions**\
  [openg2p-registry-gen2-extensions](https://github.com/openg2p/openg2p-registry-gen2-extensions/releases/tag/v1.0.2)
* **IAM Core Library**\
  [openg2p-iam-core](https://github.com/openg2p/openg2p-iam-core/releases/tag/v1.0.2)

#### Services & APIs

* **Registry Staff Portal API**\
  [openg2p-registry-gen2-apis](https://github.com/openg2p/openg2p-registry-gen2-apis/releases/tag/v1.0.2)
* **Registry Celery Services** (Workers & Beat)\
  [openg2p-registry-gen2-celery](https://github.com/openg2p/openg2p-registry-gen2-celery/releases/tag/v1.0.2)
* **IAM Staff Portal API**\
  [openg2p-iam-service](https://github.com/openg2p/openg2p-iam-service/releases/tag/v1.0.2)

***

### Architecture & Components

#### Library Components

| Component                       | Version | Purpose                                                                                |
| ------------------------------- | ------- | -------------------------------------------------------------------------------------- |
| **openg2p-registry-core**       | v1.0.2  | Domain-agnostic core registry with data models, ORM, and business logic                |
| **openg2p-registry-extensions** | v1.0.2  | Extension framework + Farmer Registry manifestation demonstrating domain customization |
| **openg2p-iam-core**            | v1.0.2  | Identity and access management core library                                            |

#### Runtime Requirements

| Component      | Version | Notes                        |
| -------------- | ------- | ---------------------------- |
| **Python**     | 3.11+   | Core runtime                 |
| **PostgreSQL** | 15+     | Primary data store           |
| **Redis**      | 7.0+    | Caching and Celery broker    |
| **MinIO**      | Latest  | S3-compatible object storage |

#### Docker Images

The following Docker images are available for v1.0.2:

```
# Registry APIs
openg2p/registry-staff-portal-api:v1.0.2
openg2p/registry-staff-portal-api:1.0.2-latest

# Celery Services
openg2p/registry-celery-workers:v1.0.2
openg2p/registry-celery-beat:v1.0.2

# IAM Services
openg2p/iam-staff-portal-api:v1.0.2

# Supporting Services
openg2p/postgres:v1.0.2-15
redis:7-alpine
minio/minio:latest
minio/mc:latest
```

#### Helm Charts

Helm charts for Kubernetes deployment are available:

* **Registry Helm Chart**\
  Repository: `openg2p-helm-charts`\
  Chart: `openg2p-registry`\
  Version: `1.0.2`
* **IAM Helm Chart**\
  Repository: `openg2p-helm-charts`\
  Chart: `openg2p-iam`\
  Version: `1.0.2`

**Installation:**

bash

```bash
helm repo add openg2p https://helm.openg2p.org
helm repo update
helm install registry openg2p/openg2p-registry --version 1.0.2
helm install iam openg2p/openg2p-iam --version 1.0.2
```

***

### Farmer Registry Manifestation - Domain Agnosticity Implementation

v1.0.2 includes the **Farmer Registry Manifestation**, an implementation built on the OpenG2P Registry core platform using the extension framework. This demonstrates the platform's domain-agnostic architecture without core platform modifications.

#### Farmer Registry Components

* **Domain-Specific Data Models:** Farmer profiles, agricultural land details, crop information, and livelihood data
* **Workflows:** Registration, verification, and eligibility assessment processes for agricultural programs
* **Custom Implementation:** Controllers, services, and data models implemented in extensions without modifying core registry code

#### Repository Location

* **Implementation:** [openg2p-registry-gen2-extensions](https://github.com/openg2p/openg2p-registry-gen2-extensions/tree/1.0/farmer_registry)
* **Documentation:** Farmer Registry Guide

#### Architecture Pattern

The Farmer Registry demonstrates the following extension patterns:

* Custom data models extending core registry entities
* Domain-specific business logic in extension services
* Reuse of authentication, authorization, and audit infrastructure from core platform
* Separate deployment of domain manifestations using shared platform infrastructure

***

### Feature Highlights

#### 1. Enhanced Authentication & Authorization

* Multi-provider authentication support with Keycloak
* OAuth2/OIDC token-based API authentication
* Role-based access control (RBAC) with granular permissions
* User ID injection in middleware for audit trails

#### 2. Asynchronous Task Processing

* Celery Workers for background job processing
* Celery Beat for scheduled tasks and batch operations
* Redis-based task queuing and result caching
* Improved performance for long-running operations

#### 3. Data Validation & Integrity

* Input validation across all endpoints
* Error handling and error messaging
* Transaction support for atomic database operations
* Schema validation with Pydantic

#### 4. Audit & Verification Logging

* Verification logging with audit trails
* Support for multiple verifications per intake form
* Change request tracking with audit metadata
* User action attribution through middleware injection

#### 5. Performance Optimizations

* Async/await patterns in FastAPI
* Connection pooling with asyncpg
* Redis caching for frequently accessed data
* Optimized database queries and indexes

***

### What's Changed

#### New Features

* **Farmer Registry Manifestation:** Farmer Registry implementation using extension framework
* **Extensible Registry Framework:** Architecture for domain-specific implementations without core modifications
* **Multi-Domain Support:** Infrastructure supporting multiple registry manifestations
* **Authentication middleware with user\_id injection:** User action attribution across API requests
* **Enhanced verification logging system:** Support for multiple verifications per intake form with audit data
* **Celery task processing:** Asynchronous task queue with Workers and Beat schedulers for batch operations

#### Improvements

* Performance optimizations in database query execution and indexing
* Enhanced error messaging and input validation
* Code organization and modular structure
* Updated documentation and code examples

#### Bug Fixes

* \[List critical bug fixes]
* Fixed hardcoded values in verification service
* Improved connection handling for database operations
* Enhanced error handling in async operations

#### Breaking Changes

* None for this patch release

***

###

---
description: The SPAR subsystem consists of the following repos
---

# Repositories

[**openg2p-spar-mapper-api**](repositories.md#openg2p-spar-mapper-api)

This repo provides the source code the ID-Account Mapper. It's an independent micro service developed using the FastAPI framework.

This service implements the [G2PConnect APIs for Account Mapper.](https://g2p-connect.github.io/specs/release/html/mapper\_core\_api\_v1.0.0.html)

[**openg2p-spar-self-service**](repositories.md#openg2p-spar-self-service)

This repo consists of 3 packages

**openg2p-spar-self-service-api**

This package provides the source code for the self service section of SPAR. It's an independent micro service developed using the FastAPI framework.

Beneficiaries will log in into SPAR using this self-service and update their financial address into the Mapper.&#x20;

This service stores all the Financial Institutions (Commercial Banks and Mobile Service Providers) and their branch information to facilitate a beneficiary to search and define his financial address.

**openg2p-spar-mapper-interface-lib**

This is a library that defines the interfaces to enable the openg2p-spar-self-service-api connect to the openg2p-spar-mapper-api.

**openg2p-spar-mapper-connector-lib**

This is a library that implements the interfaces specified by openg2p-spar-mapper-interface-lib. The self-service-api does not hard wire this mapper-connector-lib. The self-service-api invokes the mapper-api only using the interfaces.

The wiring of the mapper-connector-lib is handled by the Application Initializer (main.py) of the self-service-api.

[**openg2p-spar-self-service-ui**](https://github.com/OpenG2P/openg2p-spar-self-service-ui)

This repository contains the sources for the UI application for the self-service. This UI layer is developed using the React framework. The UI application invokes Rest APIs provided by the self-service-api services.

[**openg2p-spar-mapper-test**](https://github.com/OpenG2P/openg2p-spar-mapper-test)

This repository contains test plans and the scripts related to testing. The repo has two folders

**functional-test**

**load-test**

[**openg2p-spar-self-service-test**](https://github.com/OpenG2P/openg2p-spar-self-service-test)

This repository contains test plans and the scripts related to testing. The repo has two folders

**functional-test**

**load-test**




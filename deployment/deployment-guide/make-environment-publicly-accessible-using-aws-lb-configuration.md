---
description: (WIP)
---

# Make Environment Publicly Accessible using AWS LB Configuration

## Introduction

This document provides step-by-step instructions to make environment publicly accessible without wire guard configuration. Generally, all environments are privately accessible using wire guard configuration.

**Note:** The naming conventions may vary depending on the environment, and this documentation will be applicable when using an AWS load balancer.

## **Create a new Target Groups and LB on AWS**

The steps below outline the process for creating new Target Groups and Load Balancers (LB) on AWS.

* Creating Target Group for **external-http**
* Creating Target Group for **external-httpsredirect**
* Creating a Target Group for **PostgreSQL**
* Creating external network **Load Balancer**

### Creating Target Group for **external-http**

1. Choose a target type - `IP addresses`
2. Target Group name - `openg2p-<envname>-external-http`
3. Protocol : Port  -  `TCP : 30080`
4. VPC  - `general-vpc`
5. Health check protocol : Path : Port (**Traffic Port**)- `HTTP : /healthz/ready : 30521`
6. Next, navigate to "Register Targets", verify the network settings, add the internal IP addresses of the cluster instances, and create the target group.\


### Creating Target Group for **external-httpsredirect**

1. Choose a target type - `IP addresses`
2. Target Group name - `openg2p-<envname>-ext-httpsredirect`
3. Protocol : Port  -  `TCP : 30081`
4. VPC  - `general-vpc`
5. Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`
6. Next, navigate to "Register Targets", verify the network settings, add the internal IP addresses of the cluster instances, and create the target group.

### Creating Target Group for PostgreSQL

For PostgreSQL, there is no need to create a Target Group (TG). Instead, create a record with the name internal.sandbox-name and map the Internal NLB DNS name of the environment to it.\


### Creating external N**etwork Load Balancer**

1. Create NLB with name - `openg2p-<envname>-external`
2. Select VPC -`general-vpc`  do map for `ap-south-1a, 1b, 1c`
3. Select Security Group - `default-nginx-node`&#x20;
4. Listeners and routing **Protocol : Port : Default action**&#x20;
   * `TLS : 443 :  openg2p-<envname>-external-http`
   * `TCP : 80 : openg2p-<envname>-ext-httpsredirect`
5. Select an `ACM certificate` corresponding to the environment's domain name and create an NLB.
6. Make sure the Load balancer created and active.
7.  Map the Load Balancer DNS name to your environment domain name on Route 53.


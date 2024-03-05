# Make Environment Publicly Accessible using AWS LB Configuration

## Introduction

This document provides step-by-step instructions to make environment publicly accessible without wire guard configuration. Generally, all environments are privately accessible using wire guard configuration.

## **Create a new Target Groups and LB on AWS**

The below steps are the process to create a new Target Groups and LB on AWS

* Creating Target Group for **openg2p-external-http**
* Creating Target Group for **openg2p-external-httpsredirect**
* Creating a record
* Creating External **Network Load Balancer**

### Creating Target Group for **openg2p-external-http**

1. Choose a target type - `IP addresses`
2. Target Group name - `openg2p-<envname>-external-http`
3. Protocol : Port  -  `TCP : 30080`
4. VPC  - `general-vpc`
5. Health check protocol : Path : Port (**Traffic Port**)- `HTTP : /healthz/ready : 30521`
6. Tap next and in **Register targets**  verify `Network`, and add environment node `Internal IP's`  and create target group.\


### Creating Target Group for **openg2p-external-httpsredirect**

1. Choose a target type - `IP addresses`
2. Target Group name - `openg2p-<envname>-ext-httpsredirect`
3. Protocol : Port  -  `TCP : 30081`
4. VPC  - `general-vpc`
5. Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`
6. Tap next and in **Register targets**  verify `Network`, and add environment node `Internal IP's`  and create target group.

### Creating a Target Group for PostgreSQL

For PostgreSQL no need to create TG. Create a record with name `internal.sandbox-name` and map `Internal NLB`  of environment to it.\


### Creating External **Network Load Balancer**

1. Create NLB with name - `openg2p-<envname>-external`
2. Select VPC -`general-vpc`  do map for `ap-south-1a, 1b, 1c`
3. Select Security Group - `default-nginx-node`&#x20;
4. Listeners and routing **Protocol : Port : Default action**&#x20;
   * `TLS : 443 :  openg2p-<envname>-external-http`
   * `TCP : 80 : openg2p-<envname>-ext-httpsredirect`
5. Select `ACM certificate` as per  environment domain name and create NLB.
6. Map LB according to the Environment on Route53.

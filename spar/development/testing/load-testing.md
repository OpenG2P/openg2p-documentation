---
description: Work in progress
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

# Load Testing

## Setup

K8S Cluster

POD Configurations

DB Specific configurations

Test Server

Test Tool

## Approach

The methodology is detailed for every API

## Resolve API

10 Million ID-FA Records were created, starting from id value as 1 to id value as 10,000,000. The script to create these records can be found here.

### Test Script description

The test script allows you to adjust the number of records that are submitted in each Resolve Request. All the IDs that are sent in the Resolve request are randomly generated integers (values between 1 and 10,000,000).&#x20;

This script is then submitted using Locust API requests, where we can specify the number of concurrent users (concurrent API invocations).

The Test script can be found here.

### **Readings before test**

The following readings were recorded prior to starting the test.

<table><thead><tr><th width="220">POD</th><th width="217">CPU Utilization</th><th>Memory Utilization</th></tr></thead><tbody><tr><td>Mapper POD</td><td>0.0225 cpu</td><td>477 MB</td></tr><tr><td>Postgres POD</td><td>0.0080 cpu</td><td>20 MB</td></tr></tbody></table>

### **Test scenarios**

#### <mark style="color:green;">**8 concurrent users, 1000 requests per API, 1 second ramp up time per user**</mark>

The following readings were taken 30 minutes after starting the test. The readings were taken while the test was still running.

<table><thead><tr><th width="220">POD</th><th width="217">CPU Utilization</th><th>Memory Utilization</th></tr></thead><tbody><tr><td>Mapper POD</td><td>2 cpu</td><td>546 MB</td></tr><tr><td>Postgres POD</td><td>0.25 cpu</td><td>1.7 GB</td></tr></tbody></table>

The Locust dashboard at the 30 minute showed the following readings

<figure><img src="../../../.gitbook/assets/DuringTest-8x1000-Locust-Dashboard.png" alt=""><figcaption><p>Locust Dashboard - 30 minutes - 8 concurrent users - 1000 records per API</p></figcaption></figure>

<figure><img src="../../../.gitbook/assets/DuringTest-8x1000-Locust-Charts.png" alt=""><figcaption><p>Locust Charts - 30 minutes - 8 concurrent users - 1000 records per API</p></figcaption></figure>

The CPU for the Mapper POD showed a 100% throttle at this stage

<figure><img src="../../../.gitbook/assets/DuringTest-8x1000-CPU-Throttle-MapperPOD.png" alt=""><figcaption><p>CPU throttle - 30 minutes - 8 concurrent users - 1000 records per API</p></figcaption></figure>

#### <mark style="color:green;">**4 concurrent users, 1000 requests per API, 1 second ramp up time per user**</mark>

The following readings were taken 30 minutes after starting the test. The readings were taken while the test was still running.

<table><thead><tr><th width="220">POD</th><th width="217">CPU Utilization</th><th>Memory Utilization</th></tr></thead><tbody><tr><td>Mapper POD</td><td>2 cpu</td><td>546 MB</td></tr><tr><td>Postgres POD</td><td>0.225 cpu</td><td>1.7 GB</td></tr></tbody></table>

The Locust dashboard at the 30 minute showed the following readings

<figure><img src="../../../.gitbook/assets/DuringTest-4x1000-Locust-Stats-2.png" alt=""><figcaption><p>Locust Dashboard - 30 minutes - 4 concurrent users - 1000 records per API</p></figcaption></figure>

<figure><img src="../../../.gitbook/assets/DuringTest-4x1000-Locust-Charts.png" alt=""><figcaption><p>Locust Charts - 30 minutes - 4 concurrent users - 1000 records per API</p></figcaption></figure>

The CPU for the Mapper POD showed a 100% throttle at this stage

<figure><img src="../../../.gitbook/assets/DuringTest-4x1000-CPU-Throttle-MapperPOD.png" alt=""><figcaption><p>CPU throttle - 30 minutes - 4 concurrent users - 1000 records per API</p></figcaption></figure>

#### <mark style="color:green;">**4 concurrent users, 2000 requests per API, 1 second ramp up time per user**</mark>

The following readings were taken 30 minutes after starting the test. The readings were taken while the test was still running.

<table><thead><tr><th width="220">POD</th><th width="217">CPU Utilization</th><th>Memory Utilization</th></tr></thead><tbody><tr><td>Mapper POD</td><td>2 cpu</td><td>590 MB</td></tr><tr><td>Postgres POD</td><td>0.235 cpu</td><td>1.7 GB</td></tr></tbody></table>

The Locust dashboard at the 30 minute showed the following readings

<figure><img src="../../../.gitbook/assets/DuringTest-4x2000-Locust-Stats-2.png" alt=""><figcaption><p>Locust Dashboard - 30 minutes - 4 concurrent users - 2000 records per API</p></figcaption></figure>

<figure><img src="../../../.gitbook/assets/DuringTest-4x2000-Locust-Charts.png" alt=""><figcaption><p>Locust Charts - 30 minutes - 4 concurrent users - 2000 records per API</p></figcaption></figure>

The CPU for the Mapper POD showed a 100% throttle at this stage

<figure><img src="../../../.gitbook/assets/DuringTest-4x2000-CPU-Throttle-MapperPOD.png" alt=""><figcaption><p>CPU throttle - 30 minutes - 4 concurrent users - 2000 records per API</p></figcaption></figure>

The table below summarizes these measurements

{% embed url="https://docs.google.com/spreadsheets/d/1OBBCjhRD7ClKqm5UPTC_5LQFzAbGIN0O3W-TMIjmZIg/edit?usp=drive_link" %}



1000 records per request

<table><thead><tr><th>Users</th><th width="77">CPU</th><th width="77">Mem</th><th width="76">RPS</th><th width="103">Avg Resp </th><th width="107">95% Resp</th><th>99% Resp</th></tr></thead><tbody><tr><td>1</td><td>0.856</td><td>550</td><td>4.5</td><td>211</td><td>280</td><td>330</td></tr><tr><td>2</td><td>1.63</td><td>588</td><td>8.8</td><td>229</td><td>310</td><td>360</td></tr><tr><td>3</td><td>1.98</td><td>588</td><td>9.8</td><td>303</td><td>400</td><td>450</td></tr><tr><td>4</td><td>2</td><td>589</td><td>10</td><td>412</td><td>570</td><td>630</td></tr><tr><td>8</td><td>2</td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>

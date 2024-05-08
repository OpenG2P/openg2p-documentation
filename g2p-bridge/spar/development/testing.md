---
layout:
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
---

# Testing

## Unit Testing

We use the pytest framework for Unit Testing. All Unit Tests can be found in the tests folder in the sources github repository.

## Functional Testing

Artefacts relating to Functional Testing can be found here [Test Plans](https://drive.google.com/drive/folders/1SzlkpSnl2E1y9hLOpH\_CeZkVvE9F8qt1). The plan is a Google Spreadsheet that details the test cases. The actual test execution scripts are Postman Scripts and can be found in the Github Repository - [openg2p-spar-mapper-test](https://github.com/OpenG2P/openg2p-spar-mapper-test.git).

You have to import the Postman JSON files into Postman and execute the test cases listed in the Test Plans.

## Load Testing

**Design of Experiment**

K8S - only 1 POD can be launched - Let’s say Mapper

1 Mapper POD - with fixed resources (Cores, Memory)

1 DB POD - with fixed resources (Cores, Memory, Storage)

Connectivity between Mapper POD and DB POD

Storage - RAID/SAN Storage ?? - how - NFS Mounts??

Underlying Hardware - Xeon, Processor family - ???\


Load Test Mapper - Link API - Let's start with one API\


1 API - 1000 Records

Concurrent - 100 API invocations - result in 100,000 FA Records - Check Resource Utilization for App POD, DB POD, Measure Storage

Concurrent - 200 API invocations

Concurrent - 300 API invocations

\-- go on till we consistently get failures

\-- then reduce - till you reach threshold - of SUCCESS/FAILURE\


1 API - 5000 Records

Concurrent - 100 API invocations - result in 500,000 FA Records - Check Resource Utilization for App POD, DB POD, Measure Storage

Concurrent - 200 API invocations

Concurrent - 300 API invocations

..

Go upto point of Failure - when one or more API invocations start failing

Reduce — the concurrency — till a point - threshold - where - we can consistently demonstrate - failure above, success below

This is one POD

Now - configure kctl - such that it can launch 2 Application PODs

Repeat the experiment — I should be theoretically - go to double the threshold value - determine this -- But DB has only 1 POD - and that can be a limiting factor

3 PODs - Determine this threshold value of SUCCESS/FAILURE

All this - with Single PG Node - With Load balancing - like HAProxy -&#x20;

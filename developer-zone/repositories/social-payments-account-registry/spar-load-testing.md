---
description: WORK IN PROGRESS
---

# SPAR Load Testing

## Organisation of files for load testing

[**spar-load-test (repository)**](#user-content-fn-1)[^1]

1. spar-self-service.jmx - 1 jmx file with all endpoints in sel-service microservice
2. spar-mapper.jmx - 1 jmx file with all endpoints in mapper microservice&#x20;
3. script-to-generate-csv-for-id-fa-mapping-table.py
4. script-to-generate-request-body-for-mapper-apis.py

### **Approach**

One Node - 8 VCPU with 32 GB RAM -&#x20;

k8s - cluster setup in this node

in the k8s - we have one POD for SPAR-Self-Sevice and one POD for SPAR-mapper

POD Configuration - Standard POD Configuration - Resources to be allocated (to be discussed)&#x20;

No automatic spawning of new PODS

This one node - will be progressively subjected to loads (number of JMX Threads - i.e. number of concurrent API invocations)

Performance Monitoring of Node Metrics (CPU, Disk IO, Network Load, RAM)





[^1]: 

---
description: >-
  Runtime roles of the Connector image, how they scale, what the connector
  depends on, and how each role is monitored.
---

# Deployment

The connector ships as a single image and runs in one of several roles, chosen at start.

| Role          | Runs                                                   |
| ------------- | ------------------------------------------------------ |
| API           | The Service API and the endpoints the Admin UI uses.   |
| Fetch worker  | Reads from sources.                                    |
| Push worker   | Sends signed batches to the registry.                  |
| Job scheduler | Starts both workers at their intervals.                |

## Scaling

A production deployment runs the API, the two workers, and the scheduler as separate workloads. Both worker roles scale horizontally by running more instances, and they scale independently, since the pressure on one has nothing to do with the pressure on the other. Small environments can combine the workers and the scheduler in a single workload, at the cost of having to restart them together.

## Dependencies

The connector depends on:

* a relational database for its own data
* a broker for the task queue
* network access to the registry Partner API

## Health checks

The API role exposes liveness and readiness endpoints for health checks. The worker and scheduler roles serve no HTTP traffic and are monitored through process health, logs, and queue depth.

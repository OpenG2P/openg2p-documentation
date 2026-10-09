---
description: >-
  Commons deployment of the MOSIP WebSub hub and consolidator, including Kafka
  and hub authentication.
---

# WebSub Deployment

OpenG2P Commons Services deploys the MOSIP hub and consolidator.

| Component | Default image |
| --- | --- |
| Hub | `mosipid/websub-service:1.3.2` |
| Consolidator | `mosipid/consolidator-websub-service:1.3.2` |

The chart can install a Kafka broker. Commons points the hub at the broker
that is already installed:

```yaml
websub:
  enabled: true
  securityOn: false
  kafka:
    enabled: false
  kafkaInstallationName: commons-kafka
```

With the standard release names:

| Service | URL |
| --- | --- |
| Hub, same namespace | `http://commons-services-websub` |
| Kafka | `commons-kafka:9092` |

Registry chart value `global.websubBaseUrl` should be the hub root, without
`/hub`. The default in Commons is `http://commons-services-websub`.

## Hub authentication

`securityOn` enables the MOSIP auth-manager cookie check on register, publish,
and subscribe. The Registry publishers do not obtain that cookie, so the
Commons integration sets:

```yaml
securityOn: false
```

That switch does not disable callback challenges or `X-Hub-Signature`.
Subscribers still send `hub.secret`. Turn `securityOn` on only when MOSIP
auth-manager is deployed and every publisher and subscriber sends
`Cookie: Authorization=<token>`.

## Registry processes

`WebsubHelper` lives in `openg2p-registry-core` and reads
`websub_base_url`. The core setting name is `REGISTRY_CORE_WEBSUB_BASE_URL`.
The Partner API and Celery charts also expose:

| Process | Chart environment variable |
| --- | --- |
| Partner API | `REGISTRY_PARTNER_API_WEBSUB_BASE_URL` |
| Celery worker | `REGISTRY_CELERY_WORKERS_WEBSUB_BASE_URL` |

{% hint style="warning" %}
After an upgrade, confirm the effective `websub_base_url` inside both running
processes. The default value set in core is the incluster access route
`http://commons-services-websub`.
{% endhint %}

Which Registry call uses the hub is specified with the feature: topic
registration in the
[Outgestion Pipeline](../../../products/registry/registry/design/outgestion-pipeline.md),
and asynchronous search publish in
[DCI partner search](../../../products/registry/registry/design/partner-register-search/dci-search.md).

## Operations

| Component | Health |
| --- | --- |
| Hub | `/hub/actuator/health` |
| Consolidator | `/consolidator/actuator/health` |

| Symptom | Check |
| --- | --- |
| `hub.mode=denied` with HTTP 200 | `securityOn`, auth-manager, and whether the caller sent the MOSIP cookie. |
| Subscribe is rejected | Non-empty `hub.secret`, a callback the hub can reach, and a body that echoes `hub.challenge`. |
| Publishes succeed but no callback runs | Subscription topic name, challenge response, and hub delivery logs. |

Kafka topic names are listed in
[Subscription and delivery](subscription.md).

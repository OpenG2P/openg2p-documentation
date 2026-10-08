---
description: >-
  Shared WebSub hub used by OpenG2P products to register topics and deliver
  events to subscriber callbacks.
---

# WebSub

OpenG2P uses a [WebSub](https://www.w3.org/TR/websub/) hub as a shared delivery
service. Publishers register a topic and post content to the hub. The hub
verifies subscriber callbacks and delivers that content to them.

The hub is not part of the Registry application. Registry, and any other
product that needs push delivery, calls the hub over HTTP. Commons Services
deploys the MOSIP hub and consolidator.

## What the hub does

* Accepts topic registration from a publisher.
* Accepts subscriptions from callbacks and checks that the callback is
  controlled by the subscriber.
* Stores topic and subscriber changes as Kafka events.
* Delivers a publish to every verified subscriber of that topic.
* Signs each delivery with the subscriber's `hub.secret` when one was supplied.

The hub is stateless. The consolidator folds the Kafka events into the state
that every hub instance reads. Both components are required.

## Who publishes

| Publisher | What it sends |
| --- | --- |
| Registry outgestion | Approved register changes, after template transformation. |
| Registry Partner API | Asynchronous DCI `on-search` results for one partner. |

Those products choose the topic name and the payload. Subscription, the
callback challenge, and `X-Hub-Signature` are hub behaviour and are the same
for every publisher.

## Pages

{% content-ref url="subscription.md" %}
[Subscription and delivery](subscription.md)
{% endcontent-ref %}

{% content-ref url="deployment.md" %}
[Deployment](deployment.md)
{% endcontent-ref %}

Registry uses of the hub:

{% content-ref url="../../../products/registry/registry/design/outgestion-pipeline.md" %}
[Outgestion Pipeline](../../../products/registry/registry/design/outgestion-pipeline.md)
{% endcontent-ref %}

{% content-ref url="../../../products/registry/registry/design/partner-register-search/dci-search.md" %}
[DCI partner search](../../../products/registry/registry/design/partner-register-search/dci-search.md)
{% endcontent-ref %}

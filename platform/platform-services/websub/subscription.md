---
description: >-
  How a publisher registers a WebSub topic, how a subscriber proves its
  callback, and how delivery is signed.
---

# Subscription and Delivery

All hub calls are form posts to `{hubBaseUrl}/hub/`. Do not confuse the hub
base URL with this path. Registry's `WebsubHelper` appends `/hub/` itself.

## Register a topic

A publisher registers a topic before subscribers can attach to it:

```text
hub.mode=register
hub.topic=programme-a-search
```

HTTP errors are failures. A body of `hub.mode=denied` is also a failure, even
when the HTTP status is 200. The MOSIP hub uses that body for authorization
and validation failures. See
[Deployment](deployment.md) for `securityOn`.

Registry registers topics from the Celery topic-registration worker. The
worker is described with outgoing topics in the
[Outgestion Pipeline](../../../products/registry/registry/design/outgestion-pipeline.md).

## Subscribe a callback

The subscriber chooses the callback URL and the shared secret:

```bash
curl -sS -X POST 'https://websub.example.org/hub/' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'hub.mode=subscribe' \
  --data-urlencode 'hub.topic=programme-a-search' \
  --data-urlencode 'hub.callback=https://programme.example/registry/on-search' \
  --data-urlencode 'hub.secret=replace-with-a-strong-shared-secret'
```

The hub answers `hub.mode=accepted`, then verifies that the subscriber controls
the callback:

```text
GET /registry/on-search
  ?hub.mode=subscribe
  &hub.topic=programme-a-search
  &hub.challenge=<random-value>
  &hub.lease_seconds=864000
```

The callback returns HTTP 200 with the exact `hub.challenge` as the plain-text
body. The challenge proves control of the URL. It is not a signing key and it
is not reused.

`hub.secret` must be non-empty for this hub. The callback must be reachable
from the hub.

## Publish and verify delivery

A publisher posts:

```text
hub.mode=publish
hub.topic=programme-a-search
hub.content=<payload>
```

The hub POSTs that payload to each verified callback. When the subscription
included `hub.secret`, the delivery has:

```text
X-Hub-Signature: sha256=<64 hexadecimal characters>
```

The value is HMAC-SHA256 of the raw body bytes, using the subscriber's
`hub.secret` as the key. The digest is always 64 hex characters. Payload size
does not change the digest length.

Verify it before parsing JSON:

1. Read and keep the raw POST bytes.
2. Compute HMAC-SHA256 with the subscription secret.
3. Compare the digest with `X-Hub-Signature` using a constant-time comparison.
4. Decode the payload only after the digest matches.

Do not parse and re-serialize the body before the HMAC check. Content type can
differ by hub version, so use the raw bytes and the headers observed from the
deployed hub.

| Mechanism | What it proves |
| --- | --- |
| `hub.challenge` | The subscriber controls the callback URL at subscribe time. |
| `hub.secret` and `X-Hub-Signature` | This delivery came from the hub to that subscription. |
| Publisher payload signature | The payload itself was produced by the publisher. For DCI search, that is the detached JWS on the `on-search` envelope. |

The publisher signature is not a hub feature. DCI signing is specified in
[DCI partner search](../../../products/registry/registry/design/partner-register-search/dci-search.md).

## Kafka metadata topics

The hub and consolidator use:

* `registered-websub-topics`
* `consolidated-websub-topics`
* `registered-websub-subscribers`
* `consolidated-websub-subscribers`

An application topic such as `programme-a-search` is a value inside those
messages. It is not its own Kafka topic.

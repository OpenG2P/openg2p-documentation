---
description: >-
  Helm values and Docker build args that turn the notification connector
  on for Registry and AWE.
---

# Deployment

Registry staff API, the Registry Celery worker, and AWE each get the same connector environment. The connector reads `NOTIFICATION_*` directly. There is no service-specific prefix.

The staff UI gets a different set. It talks to the public Novu hosts. It does not send. See [Inbox](inbox.md).

## Shared values

Registry chart: [values.yaml](https://github.com/OpenG2P/registry-platform/blob/develop/helm/openg2p-registry/values.yaml) and [questions.yaml](https://github.com/OpenG2P/registry-platform/blob/develop/helm/openg2p-registry/questions.yaml).

AWE chart: [values.yaml](https://github.com/OpenG2P/awe/blob/develop/helm/openg2p-awe/values.yaml) and [questions.yaml](https://github.com/OpenG2P/awe/blob/develop/helm/openg2p-awe/questions.yaml).

| Helm value | Env on the API or worker | Default |
| --- | --- | --- |
| `global.notificationEnabled` | `NOTIFICATION_ENABLED` | `true` |
| `global.notificationProvider` | `NOTIFICATION_PROVIDER` | `novu` |
| `global.notificationProviderUrl` | `NOTIFICATION_PROVIDER_URL` | `http://commons-novu-api:3000` |
| `global.notificationWorkflows` | `NOTIFICATION_WORKFLOWS` | The event map for that product. See below |
| `global.staffPortalBaseUrl` | `NOTIFICATION_STAFF_PORTAL_BASE_URL` | empty |
| `global.notificationApiKeySecret` | Secret name for `NOTIFICATION_PROVIDER_API_KEY` | `commons-novu` |
| `global.notificationApiKeySecretKey` | Secret key | `api-key` |

The API key reference is optional. A pod can start when the Novu secret is not there yet. Sends then fail until the key exists, and that failure is logged.

`NOTIFICATION_STAFF_PORTAL_BASE_URL` is the public staff UI origin, for example `https://staff.example.org`, with no path and no trailing slash required (the app strips one trailing slash). Locale `/en` is fixed in the Novu workflow. Use the registry staff UI host, not the AWE admin host. Export and AWE links are empty of a host until this value is set.

`notificationEnabled: false` skips every send, even when a workflow is listed. Removing one key from `notificationWorkflows` skips only that event.

Registry puts the same `NOTIFICATION_*` block on the staff API and on the Celery worker. Export and ingest sends run on the worker. AWE puts the block on the AWE API.

### Registry workflow map

```json
{
  "change_request.created": "change-request-created",
  "change_request.approved": "change-request-approved",
  "change_request.rejected": "change-request-rejected",
  "intake_form.submission_created": "intake-form-submission-created",
  "intake_form.submission_approved": "intake-form-submission-approved",
  "intake_form.submission_rejected": "intake-form-submission-rejected",
  "register_export.completed": "register-export-completed",
  "register_export.failed": "register-export-failed"
}
```

### AWE workflow map

```json
{
  "approval.stage_started": "approval-stage-started",
  "approval.task_reassigned": "approval-task-reassigned",
  "approval.stage_escalated": "approval-stage-escalated",
  "approval.task_expired": "approval-task-expired",
  "approval.request_approved": "approval-request-approved",
  "approval.request_rejected": "approval-request-rejected",
  "approval.request_cancelled": "approval-request-cancelled",
  "approval.stage_quorum_skipped": "approval-stage-quorum-skipped"
}
```

The AWE Helm question describes `novu` as the provider value. The connector still loads whatever name is registered. See [Switch provider](connector.md#switch-provider). Changing provider means a new Python provider and a new `notificationProvider` value. The event map can stay.

## Staff UI values

These are on the registry staff UI deployment. They are not connector settings.

| Helm value | Pod env | Use |
| --- | --- | --- |
| `global.notificationApplicationIdentifier` | `NOTIFICATION_APPLICATION_IDENTIFIER` | Novu application identifier. Empty until you copy it from the Novu environment |
| `global.notificationBackendUrl` | `NOTIFICATION_BACKEND_URL` | Public API URL, `https://` plus `global.notificationApiHostname` |
| `global.notificationWebsocketUrl` | `NOTIFICATION_WEBSOCKET_URL` | Public WebSocket URL, `https://` plus `global.notificationWsHostname` |
| `global.notificationHmacSecretKey` | `NOTIFICATION_SECRET_KEY` | Key `novu-secret-key` on the Novu secret. Server-only |

The inbox client reads `NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER`, `NEXT_PUBLIC_NOVU_BACKEND_URL`, and `NEXT_PUBLIC_NOVU_SOCKET_URL`. Wire those from the three public values above. Do not point the browser at `http://commons-novu-api:3000`.

## Docker

Staff API and Celery images install the connector from git. Both Dockerfiles take:

| Build arg | Default |
| --- | --- |
| `NOTIFICATION_REPO` | `openg2p/notifications` |
| `NOTIFICATION_REF` | `develop` |

The pip URL is `git+https://github.com/${NOTIFICATION_REPO}@${NOTIFICATION_REF}#subdirectory=connector`.

* [Staff API Dockerfile](https://github.com/OpenG2P/registry-platform/blob/develop/docker/staff-api/Dockerfile)
* [Celery Dockerfile](https://github.com/OpenG2P/registry-platform/blob/develop/docker/celery/Dockerfile)

The AWE image builds a wheel of the same URL in the builder stage and installs `openg2p-notification` in the runtime stage. Args are the same `NOTIFICATION_REPO` and `NOTIFICATION_REF`. Source: [AWE Dockerfile](https://github.com/OpenG2P/awe/blob/develop/Dockerfile).

A registry variant image (`FROM` the platform staff API or Celery image) keeps the connector that was installed in the base. Rebuild the platform image when the connector ref changes, then rebuild the variant.

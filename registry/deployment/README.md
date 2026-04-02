---
description: Deploying OpenG2P Registry on Kubernetes using Helm charts.
---

# Deployment

OpenG2P Registry is deployed on Kubernetes using Helm charts. This section covers everything needed to deploy, configure, and maintain a Registry instance.

## Pre-requisites

The following infrastructure must be in place before deploying Registry.

For detailed infrastructure setup, refer to the [Deployment Guide](../../deployment/).

* Kubernetes cluster (v1.24+)
* PostgreSQL database
* Keycloak (for IAM)
* MinIO or S3-compatible object storage
* Rancher (recommended for cluster management)

## Deployment steps

1. **Set up infrastructure** -- Refer to the common [Deployment Guide](../../deployment/).
2. **Install Registry via Helm chart** -- See [Helm Chart 4.x](helm-chart-4.x.md).
3. **Post-installation configuration** -- See [Post-Installation](post-installation.md).

## In this section

{% content-ref url="helm-chart-4.x.md" %}
helm-chart-4.x.md
{% endcontent-ref %}

{% content-ref url="post-installation.md" %}
post-installation.md
{% endcontent-ref %}

{% content-ref url="upgrade-guide.md" %}
upgrade-guide.md
{% endcontent-ref %}

---
description: Custom Keycloak Docker image with OpenG2P themes pre-installed
---

# Keycloak Custom Docker Image

## Overview

OpenG2P maintains a custom Keycloak Docker image that bundles branded login and admin themes on top of the upstream Bitnami Keycloak image. This avoids the complexity of runtime theme mounting via ConfigMaps and ensures themes are version-pinned to the image.

### Source code

[https://github.com/OpenG2P/keycloak-themes](https://github.com/OpenG2P/keycloak-themes)

## Base image

| Property | Value |
| -------- | ----- |
| Base image | `openg2p/keycloak:24.0.5-debian-12-r1` |
| Source | [OpenG2P Docker Hub](https://hub.docker.com/r/openg2p/keycloak) |
| Upstream origin | Bitnami Keycloak 24.0.5 on Debian 12 |
| Custom image tag format | `openg2p/keycloak:24.0.5-debian-12-r1-g2pN` |

## Why a custom image?

The OpenG2P Keycloak deployment requires custom login and admin themes for branding. Two approaches were evaluated:

| Approach | Verdict |
| -------- | ------- |
| **ConfigMap mount** | Not suitable. Themes contain binary assets (PNG images), have a deep nested directory structure (21+ files across 6+ subdirectories), and are subject to the 1 MB ConfigMap size limit. |
| **Custom Docker image** | Recommended. A single `COPY` instruction per theme bakes everything into the image layer. Binary files, nested directories, and reproducibility are handled naturally. |

## Included themes

The custom image bundles the following themes:

| Theme | Type | Description |
| ----- | ---- | ----------- |
| `g2p-advisor` | Login | Dark-themed login page with OpenG2P branding and gold accents, supporting login, OTP, password reset, and email verification flows. |
| `staff-portal-login-theme` | Login | Login theme for the OpenG2P Staff Portal. |
| `staff-portal-admin-theme` | Admin | Admin console theme for the OpenG2P Staff Portal. |

## Key resources

| Resource | Link |
| -------- | ---- |
| Themes source code | [github.com/OpenG2P/keycloak-themes](https://github.com/OpenG2P/keycloak-themes) |
| Dockerfile | [keycloak-themes/Dockerfile](https://github.com/OpenG2P/keycloak-themes/blob/main/Dockerfile) |
| GitHub Actions workflow | [keycloak-themes/.github/workflows/docker-build.yml](https://github.com/OpenG2P/keycloak-themes/blob/main/.github/workflows/docker-build.yml) |
| Helm chart for Keycloak | [openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm) |

## Building the Docker image

### Triggering a build via GitHub Actions

The image is built using a **manual workflow dispatch** from the keycloak-themes repository.

1. Go to the [Actions tab](https://github.com/OpenG2P/keycloak-themes/actions) of the `keycloak-themes` repository.
2. Select the **Build and Push Keycloak with Themes** workflow.
3. Click **Run workflow**.
4. Enter the G2P version suffix in the `g2p_version` field (e.g., `g2p1`, `g2p2`, `g2p3`).
5. Click **Run workflow** to start the build.

The workflow will:

* Validate that the version matches the `g2pN` format.
* Check that the tag does not already exist on Docker Hub to prevent accidental overwrites.
* Build the image for the `linux/amd64` platform.
* Push the image to Docker Hub as `openg2p/keycloak:24.0.5-debian-12-r1-<g2p_version>`.

{% hint style="info" %}
The repository must have `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets configured under **Settings > Secrets and variables > Actions**.
{% endhint %}

### Building locally (macOS / Apple Silicon)

To build the amd64 image locally on an Apple Silicon Mac:

```bash
cd keycloak-themes/
docker build --platform linux/amd64 -t openg2p/keycloak:24.0.5-debian-12-r1-g2p1 .
```

To push manually:

```bash
docker push openg2p/keycloak:24.0.5-debian-12-r1-g2p1
```

## Updating the Docker image version

When themes are modified, a new image version must be built and published.

1. Make and commit your theme changes to the `keycloak-themes` repository.
2. Determine the next G2P version suffix by incrementing the previous one (e.g., if the latest is `g2p2`, use `g2p3`).
3. Trigger the GitHub Actions workflow with the new version suffix as described above.
4. After the image is published, update the Keycloak Helm chart values to reference the new tag:

```yaml
image:
  registry: docker.io
  repository: openg2p/keycloak
  tag: "24.0.5-debian-12-r1-g2p3"   # <-- update this
```

5. Redeploy Keycloak using the updated Helm values.

{% hint style="warning" %}
Always use a new `g2pN` suffix for each change. Never overwrite an existing tag -- this ensures rollback is always possible.
{% endhint %}

## Applying themes in Keycloak

Once the custom image is deployed, themes must be activated per realm:

1. Log in to the **Keycloak Admin Console**.
2. Select the target **Realm** from the dropdown in the top-left corner.
3. Navigate to **Realm Settings** in the left sidebar.
4. Go to the **Themes** tab.
5. Select the desired theme from the dropdowns:
   * **Login theme** -- choose `g2p-advisor` or `staff-portal-login-theme`
   * **Admin console theme** -- choose `staff-portal-admin-theme`
6. Click **Save**.

Changes take effect immediately for new sessions.

## Tag history

| Tag | Date | Notes |
| --- | ---- | ----- |
| `24.0.5-debian-12-r1-g2p1` | 2026-04-03 | Initial build with g2p-advisor, staff-portal-login-theme, and staff-portal-admin-theme. |

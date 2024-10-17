---
description: How to create SR Docker Package
---

# 📘 Docker Packaging Guide

## Concepts

Dockers are created via GitHub workflows by triggering them manually. Dockers may be created using command line as well. The contents of the Docker are listed in a [package file](https://github.com/OpenG2P/openg2p-packaging/tree/main/packaging/packages/) available in the [openg2p-packaging ](https://github.com/OpenG2P/openg2p-packaging)repo. This package file is read by the [package\_docker.yml](https://github.com/OpenG2P/openg2p-packaging/blob/main/.github/workflows/package\_docker.yml) workflow. This workflow creates the Docker and pushes it to the Docker Hub.  The name and tag of the Docker are specified as the first line in the package file followed by the base version of the Odoo that is used to create the Docker. See example below.

<pre><code><strong>#!openg2p/openg2p-social-registry-odoo-package:1.3.1
</strong>#!17.0.20240505-debian-12-r0

# OCA dependencies
oca = git://v1.2.2//https://github.com/openg2p/openg2p-social-registry-community-addons

# OpenG2P developed modules
openg2p_registry = git://v1.3.0//https://github.com/openg2p/openg2p-registry
openg2p_social_registry = git://v1.3.0//https://github.com/openg2p/openg2p-social-registry
</code></pre>

The package may contain private repositories, in which case, the token to clone the repositories must be set in the respective repositories.

Versions of all repositories that are used to create the Docker are specified in the package file. For Dockers that are "frozen" it is assumed that all versions of repositories are frozen as well (i.e. tagged).&#x20;

## Steps

### Creating tokens to clone private repositories

> This procedure only applies if repositories in your Docker package are private. Otherwise, skip to the next step.

1. Create a new token for OpenG2P Bot user and add it to the private repo with the name `OPENG2P_BOT_GITHUB_PAT`. This token must have read permissions to the repository
2. To create this token you will have to log in to Github as OpenG2P Bot user.
3. Give _Write_ permission to OpenG2P Bot user on Github (under Settings --> Collaborators and Teams).

### Tagging the repositories

1. Run the "Tag the repo" (`tag.yml` ) workflow using Github Actions.  Make sure `OpenG2PBot` user on Github has 'Write' permission to the repository. The workflow checks if there are any changes w.r.t. to the previous version specified. If there are no changes the workflow fails with a message and a new tag is not created.

### Creating Docker package

1. Create a package file for the new version that you want to create.  See [example](https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/social-registry/1.3.1.txt). The name of the package file can be arbitrary but it is recommended that it reflects the Docker tag version.  E.g. `1.3.1.txt`.
2. <mark style="color:red;">IMPORTANT</mark>: Update the first line in the package file for the new version.  (This is critical otherwise previous tag will get overwritten on Docker Hub)
3. Inspect the contents of the package file on which versions of repositories need to be packed in this Docker.
4. Make sure the repositories are tagged with the versions matching in the package file.  See above section on tagging.
5. Trigger Docker build and push using the Github Actions.  Provide the above file path as input w.r.t to `packages` folder.
6. Verify that the new Docker has been pushed on Docker Hub.
7. Update the details of this version on the [Versions](../versions.md) page.

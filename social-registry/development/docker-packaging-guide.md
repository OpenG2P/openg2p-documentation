---
description: How to create SR Docker Package
---

# 📘 Docker Packaging Guide

## Concepts

### Package file and Github workflow

Dockers are created via Github workflows by triggering the same manually when required. Dockers may be created manually as well if required. The contents of the Docker are listed in a [package file](https://github.com/OpenG2P/openg2p-packaging/tree/main/packaging/packages/) available in the [openg2p-packaging ](https://github.com/OpenG2P/openg2p-packaging)repo. This package file is read by the [package\_docker.yml](https://github.com/OpenG2P/openg2p-packaging/blob/main/.github/workflows/package\_docker.yml) workflow. This workflow creates the Docker and pushes it to the Docker Hub.  The name and tag of the Docker are specified as the first line in the package file followed by the base version of the Odoo that is used to create the Docker. See [example](https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/social-registry/1.3.1.txt).&#x20;

The package may contain private repositories, in which case, the token to clone the repositories must be set in the respective repositories.

Versions of all repositories that are used to create the Docker are specified in the package file. For Dockers that are "frozen" it is assumed that all versions of repositories are frozen as well (i.e. tagged).&#x20;

### Creating tokens to clone private repositories

1. Create a new token for OpenG2P Bot user and add it to the private repo with the name `OPENG2P_BOT_GITHUB_PAT`. This token must have read permissions to the repository
2. To create this token you will have to log in to Github as OpenG2P Bot user.

### Tagging the repositories

1. For private repositories give Write permission to OpenG2P Bot user on Github (under Settings --> Collaborators and Teams).
2. Run the `tag.yml` workflow using Github Actions.  The workflow checks if there are any changes w.r.t. to previous version specified. If there are no changes the workflow fails with a message and new tag is not created.

### Creating Docker package

1. Create a package file for the new version that you want to create. The name of the package file should reflect the new version.  E.g. `1.3.1.txt`.
2. Update the first line in the package file for the new version.
3. Inspect the contents of the package file on which versions of repositories need to be packed in this Docker.
4. Make sure the repositories are tagged with the versions matching in the package file.  See above section on tagging.
5. Add this version in the Github [workflow file ](https://github.com/OpenG2P/openg2p-packaging/blob/main/.github/workflows/package\_docker.yml)so that it appears as a drop-down while running the workflow.
6. Trigger Docker build and push using the Github Actions.
7. Verify that the new Docker has been pushed on Docker Hub.

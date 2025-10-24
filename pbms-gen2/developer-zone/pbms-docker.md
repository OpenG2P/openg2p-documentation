---
description: >-
  Information regarding PBMS odoo and background task docker images and their
  creation
---

# PBMS Docker

## Concepts

Dockers are created via GitHub workflows by triggering them manually. Dockers may be created from the command line as well. The docker images for PBMS Odoo and Background Tasks (API, Celery Beat Producer, and Celery Worker) are created independent of each other.

The contents of the Docker are listed in a package file available in the [openg2p-pbms-docker](https://github.com/OpenG2P/openg2p-pbms-docker) repo. This package file is read by the [docker-build-odoo.yml](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/.github/workflows/docker-build-odoo.yml) workflow for odoo and [docker-build-bg-tasks.yml](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/.github/workflows/docker-build-bg-tasks.yml) workflow for background tasks. These workflows create the Docker Images and push them to the Docker Hub. &#x20;

For odoo, the name and tag of the Docker are specified as the first line in the [package file](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/openg2p-pbms-odoo/3.0.0.txt) followed by the base version of the Odoo that is used to create the Docker. See example below.

```
#!openg2p/openg2p-pbms-core:3.0.0
#!17.0-20250807

# OCA dependencies
oca = git://v1.0.4//https://github.com/openg2p/openg2p-pbms-community-addons

# OpenG2P developed modules
openg2p_commons = git://v1.4.0//https://github.com/OpenG2P/openg2p-odoo-commons
openg2p_pbms = git://v3.0.0//https://github.com/openg2p/openg2p-pbms-odoo
openg2p_pbms_extensions = git://v3.0.0//https://github.com/openg2p/openg2p-pbms-odoo-extensions 
```

For background tasks, separate package files are provided for the [API](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/openg2p-pbms-bg-tasks/bg-task-api.txt), [Celery Beat](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/openg2p-pbms-bg-tasks/bg-task-celery-beat.txt), and [Celery Worker](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/openg2p-pbms-bg-tasks/bg-task-celery-worker.txt) services. The Docker image name and tag are defined on the second line of each file, followed by the Dockerfile reference used to build the image. Any additional dependencies required can be listed at the end of the file. See the example API packaging below.

```
# bg-task-api.txt
#!openg2p/openg2p-pbms-bg-task-api:3.0.0
#!openg2p-pbms-bg-tasks/Dockerfile.api
#!.
git+https://github.com/openg2p/openg2p-pbms-bg-tasks-extensions@v3.0.0#subdirectory=openg2p-bg-task-registry-adapters
```

The package may contain private repositories, in which case, the token to clone the repositories must be set in the GitHub secret.

Versions of all repositories that are used to create the Docker are specified in the package file. For Dockers that are "frozen" it is assumed that all versions of repositories are frozen as well (i.e., tagged).

## Steps to create PBMS Docker

### Creating tokens to clone private repositories

> This procedure only applies if repositories in your Docker package are private. Otherwise, skip to the next step.

1. Create a new token for OpenG2P Bot user and add it to the private repo with the name `OPENG2P_BOT_GITHUB_PAT`. This token must have read permissions to the repository
2. To create this token you will have to log in to Github as OpenG2P Bot user.
3. Give _Write_ permission to OpenG2P Bot user on Github (under Settings --> Collaborators and Teams).

### Tagging the repositories

1. Run the "Tag the repo" (`tag.yml` ) workflow using Github Actions.  Make sure `OpenG2PBot` user on Github has 'Write' permission to the repository. The workflow checks if there are any changes w.r.t. to the previous version specified. If there are no changes the workflow fails with a message and a new tag is not created.

### Creating Docker Packages

{% tabs %}
{% tab title="Odoo" %}
#### Docker package for Odoo

1. Create a package file for the new version that you want to create.  See [example](https://github.com/OpenG2P/openg2p-pbms-docker/blob/3.0/openg2p-pbms-odoo/3.0.0.txt). The name of the package file can be arbitrary but it is recommended that it reflects the Docker tag version.  E.g. `3.0.0.txt`.
2. <mark style="color:red;">IMPORTANT</mark>: Update the first line in the package file to the new version.  (This is critical otherwise previous tag will get overwritten on Docker Hub.)
3. Inspect the contents of the package file on which versions of repositories need to be packed in this Docker.
4. Make sure the repositories are tagged with the versions matching in the package file.  See above section on [tagging](pbms-docker.md#tagging-the-repositories).
5. Trigger `OpenG2P PBMS Odoo Dockers` action using the Github Actions.  Provide the correct branch and above file path as input w.r.t to `packages` folder.
6. Verify that the new Docker has been pushed on Docker Hub.
{% endtab %}

{% tab title="Background Tasks" %}
#### Docker package for BG Tasks

1.  Create a package file each (api, celery-beat, and celery-worker) for the new version that you want to create.  See [examples](https://github.com/OpenG2P/openg2p-pbms-docker/tree/3.0/openg2p-pbms-bg-tasks). The name of the package file can **NOT** be arbitrary (it is recommended that for a new version the packaging be done on a new branch) since a static path is used in the workflow.

    ```
    serviceFile:
       - openg2p-pbms-bg-tasks/bg-task-api.txt
       - openg2p-pbms-bg-tasks/bg-task-celery-worker.txt
       - openg2p-pbms-bg-tasks/bg-task-celery-beat.txt
    ```
2. <mark style="color:red;">IMPORTANT</mark>: Update the second line in the package file to the new version.  (This is critical otherwise previous tag will get overwritten on Docker Hub.)
3.  Inspect the contents of the package file and corresponding Dockerfile on which versions of repositories and additional dependencies need to be packed in this Docker. See below an example of package and Dockerfile for api:

    ```
    # bg-task-api.txt
    #!openg2p/openg2p-pbms-bg-task-api:3.0.0
    #!openg2p-pbms-bg-tasks/Dockerfile.api
    #!.
    git+https://github.com/openg2p/openg2p-pbms-bg-tasks-extensions@v3.0.0#subdirectory=openg2p-bg-task-registry-adapters
    ```

    ```
    FROM python:3.12.11-alpine3.22

    ARG G2P_REF=v3.0.0

    RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers make \
     && apk add --no-cache bash git gettext libpq-dev libmagic

    WORKDIR /app

    # Dynamic deps from workflow (optional)
    COPY adapters.requirements.txt /tmp/adapters.requirements.txt
    RUN if [ -s /tmp/adapters.requirements.txt ]; then pip install --no-cache-dir -r /tmp/adapters.requirements.txt --verbose; fi

    # Core libs (as in your current API Dockerfile)
    RUN pip install --no-cache-dir git+https://github.com/openg2p/openg2p-fastapi-common@v1.1.3\#subdirectory=openg2p-fastapi-common  \
     && pip install --no-cache-dir git+https://github.com/openg2p/openg2p-fastapi-common@v1.1.3\#subdirectory=openg2p-fastapi-auth \
     && pip install --no-cache-dir git+https://github.com/openg2p/openg2p-g2pconnect-common-lib@v2.0.0\#subdirectory=openg2p-g2pconnect-common-lib \
     && pip install --no-cache-dir git+https://github.com/openg2p/openg2p-g2pconnect-common-lib@v2.0.0\#subdirectory=openg2p-g2pconnect-mapper-lib

    # Always from openg2p-g2p-bridge repo (no local installs)
    RUN pip install --no-cache-dir \
        "git+https://github.com/openg2p/openg2p-pbms-bg-tasks@${G2P_REF}#subdirectory=openg2p-pbms-models" \
        "git+https://github.com/openg2p/openg2p-pbms-bg-tasks@${G2P_REF}#subdirectory=openg2p-bg-task-models" \
        "git+https://github.com/openg2p/openg2p-pbms-bg-tasks@${G2P_REF}#subdirectory=openg2p-bg-task-api"

    RUN apk del --no-network .build-deps

    ENV PYTHONUNBUFFERED=1
    ENV BG_TASK_WORKER_TYPE=gunicorn
    ENV BG_TASK_HOST=0.0.0.0
    ENV BG_TASK_PORT=8000
    ENV BG_TASK_NO_OF_WORKERS=8

    # Use module path for migrate and Gunicorn WSGI app
    CMD python3 -m openg2p_bg_task_api.main migrate; \
        ${BG_TASK_WORKER_TYPE} "openg2p_bg_task_api.main:app" --workers ${BG_TASK_NO_OF_WORKERS} --worker-class uvicorn.workers.UvicornWorker --bind ${BG_TASK_HOST}:${BG_TASK_PORT}
    ```
4. Make sure the repositories are tagged with the versions matching in the package file.  See above section on [tagging](pbms-docker.md#tagging-the-repositories).
5. Trigger `OpenG2P PBMS Background Task Dockers`  action using the Github Actions.  Provide the correct branch and run the workflow.
6. Verify that the new Dockers has been pushed on Docker Hub.
{% endtab %}
{% endtabs %}

## Automatic build and upload of private Dockers

Refer to the guide:  [Automatic Build and Upload of Private Dockers](../../deployment/deployment-guide/automatic-build-and-upload-of-private-dockers.md)

---
description: Guide to build and upload on Docker hub from private Github repositories
---

# Automatic Build and Upload of Private Dockers

## Docker Hub

1. Create a private repository on Docker Hub for all dockers that will be uploaded.
2. Make sure a 'bot' user is created on Docker Hub that has read/write access to these repositories
3. Create an access token for this user. (Refer Docker Hub docs)

## Creation of Github actions

1. Clone the private repo on the command line (example, `openg2p-myrepo`)
2. Under `openg2p-myrepo/.github` folder create the following folder structure

```
.github/
├── docker_packages
└── workflows
```

3. Inside `docker_packages` folder create package files for modules like Social Registry, PBMS, etc. See [sample package files](https://github.com/OpenG2P/openg2p-packaging/tree/main/samples/sample-packages-for-private-repo).  Replace `openg2p-myrepo` with your private repo name.
4. Run following command in your private repo root folder `openg2p-myrepo/:`

```sh
git submodule add https://github.com/openg2p/openg2p-packaging .github/docker_packaging
```

This will clone `openg2p-packaging` repo into the `docker_packaging` folder. The folder structure will look like

<pre><code>.github/
├── docker_packages
<strong>|── docker_packaging
</strong>└── workflows
</code></pre>

5. Inside `workflows` folder copy [`docker_build.yml`](https://github.com/OpenG2P/openg2p-packaging/blob/main/samples/docker-build.yml)  and modify the following for your repo:
   1. Set `SERVICE_NAME` to name of your Docker Hub repository&#x20;
   2. Replace `openg2p-myrepo` with your repo name
6. Check in all the above.

## Enabling Github actions

1. Under _Secrets and variables->Actions_ create the following secrets:
   * DOCKER\_HUB\_ACTOR: Docker Hub user id that has permission to read/write the above registry
   * DOCKER\_HUB\_ORGANIZATION: Organization under which your private repo resides
   * DOCKER\_HUB\_TOKEN: Access token for this user on Docker Hub
2. Under your private repo _Settings->Actions->General,_ enable "**Allow all actions and reusable workflows**"

## Run

The above workflow will automatically run when a PR is merged into the private repo. Dockers will be built and posted to Docker Hub.

# Packaging Odoo based Docker

This page contains steps for packaging different Odoo add-ons repositories into a Docker image. These instructions can be helpful for System Integrators who want to create Docker images that package their custom Odoo addons along with OpenG2P addons.

## Procedure

Steps to create the Docker image are given below.

* Clone the [https://github.com/OpenG2P/openg2p-packaging](https://github.com/OpenG2P/openg2p-packaging) and go to the [packaging](https://github.com/OpenG2P/openg2p-packaging/tree/develop/packaging) directory.
*   Create a text file, for example `my-package.txt` . This signifies a package. This file should include all OpenG2P modules (repositories) to be packaged into a new docker. Each line describes one repository to include, and the structure of each line looks like this.

    ```
    repo_name = git://<github branch name>//<github url to pull from>
    repo2_name = file://<path of the package in local system>
    ```
*   Any underscore in the repository name will be converted to a hyphen during installation. For example,

    ```
    repo_name = git://<github branch name>//<github url to pull from>
    ```

    This is internally converted to `repo-name`.
* The above configuration can also be made via environment variables.
  *   Any variable with the prefix `G2P_PACKAGE_my_package_` will be considered as a repository to install i.e., `G2P_PACKAGE_<package_name>_<repo_name>`. For example,

      ```
      G2P_PACKAGE_my_package_repo3_name=git://<github branch name>//<github url to pull from>
      ```
  * These environment variables can be added in `.env` file (in the same folder). The `.env` file will automatically be considered.
  * If the same package is available in `my-package.txt`, `.env,` and environment variable, then their preference order will be considered (highest to lowest).
    * `.env` file.
    * Environment variable.
    * `my-package.txt`
  * Use the `.env` to overload packages from `my-package.txt`
* Gather all the community addon dependencies into one repo. And add a line for the community addon repo also in the `my-package.txt` .
*   Run the following to download all packages.

    ```bash
    ./package.sh my-package.txt
    ```
*   After downloading packages, run the following to build the Docker image.

    ```bash
    docker build . -t <docker image name>
    ```

    * If you wish to use a different version of the Odoo base, use the `BASE_VERSION` build arg. This arg is nothing but the tag of the base Odoo image. Check [here](https://hub.docker.com/_/odoo/tags) for the full list of Odoo image tags.
    *   If you wish to remove certain Odoo addons from the Docker, use the `MODULES_TO_REMOVE` build arg. This arg should be given in the form of a regex (PCRE). The script searches for all Odoo addons that match this regex and removes them.

        ```bash
        docker build . -t <docker image name> \
            --build-arg BASE_VERSION="17.0-20250807" \
            --build-arg MODULES_TO_REMOVE='(^iap.*$)|(^hr.*$)'
        ```
*   Then push the image.

    ```bash
    docker push <docker image name>
    ```

Notes:

* The entire flow of creating Docker images from a package.txt can be made easier using the GitHub action. OpenG2P official images are built using this approach. For example, refer to the [Social Registry Docker packaging](../../social-registry/deployment/registry-helm-chart/docker-packaging-guide.md) guide.
* The above uses the [Docker library Odoo](https://hub.docker.com/_/odoo) image as base.
* This also installs any Python requirements configured in `requirements.txt` inside each package.
* Reference packages can be found in `packaging/packages` directory.

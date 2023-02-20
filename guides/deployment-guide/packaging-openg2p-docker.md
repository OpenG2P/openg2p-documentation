---
description: Work in progress
---

# Packaging OpenG2P Docker

This page contains steps to be performed for packaging different components and addons, of OpenG2P and similar, into a docker image.

## Instructions

* Clone the [https://github.com/OpenG2P/openg2p-packaging](https://github.com/OpenG2P/openg2p-packaging)  and go to [packaging](https://github.com/OpenG2P/openg2p-packaging/tree/develop/packaging) directory
*   Create text file, example `my-package.txt` . This signifies a package. This file should include all openg2p modules (repositories) to be packaged into a new docker. Each line describes one repository to include, and the structure of each line looks like this.

    ```
    repo_name = git://<github branch name>//<github url to pull from>
    repo2_name = file://<path of the package in local system>
    ```

    *   Any underscore in the repository name will be converted to hyphen during installation. For example:

        ```
        repo_name = git://<github branch name>//<github url to pull from>
        ```

        This is internally converted to `repo-name`.
* The above configuration can be made via environment variables also.
  *   Any variable with the prefix `G2P_PACKAGE_my_package_` will be considered as repository to install i.e., `G2P_PACKAGE_<package_name>_<repo_name>`. For example;

      ```
      G2P_PACKAGE_my_package_repo3_name=git://<github branch name>//<github url to pull from>
      ```
  * These env variables can be added in `.env` file (in the same folder). The `.env` file will automatically be considered.
  * If same package is available in `my-package.txt`, `.env` and environment variable, then this will be the preference order in which they are considered (highest to lowest).
    * `.env` file
    * Environment variable.
    * `my-package.txt`
  * Use the `.env` to overload packages from `my-package.txt`
*   Run the following to download all packages:

    ```
    ./package.sh my-package.txt
    ```
*   After downloading packages, run the following to build docker image:

    ```
    docker build . -t <docker image name>
    ```
*   Then push the image.

    ```
    docker push <docker image name>
    ```
* Notes:
  * The above uses bitnami's odoo image as base.
  * This script also pulls in any OCA dependencies configured, in `oca_dependencies.txt` inside each package. Use this env variable to change the version of OCA dependencies to be pulled, `OCA_DEPENDENCY_VERSION` (defaults to `15.0`).
  * This also installs any python requirements configured in `requirements.txt` inside each package.
  * Reference packages can be found in packages directory inside packaging directory.

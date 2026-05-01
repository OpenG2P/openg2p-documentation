---
description: How to create a Helm Package for Social Registry
---

# Registry Helm Chart - 2.x

{% hint style="warning" %}
The material here applies to all Social Registry charts with 2.x versions.  The environment deployment architecture going forward is changed and consequently the charts have changed too. For newer charts refer to documentation on 3.x version of charts and above&#x20;
{% endhint %}

## Creation of Helm Chart

Below are steps to create 2.x  Helm Chart for Registry ().

### Tagging Helm repo

The charts are located in [this](https://github.com/OpenG2P/openg2p-social-registry-deployment/) repo.

1. Decide on which branch you would like to create the tag.
2. On the marked branch, create another temporary branch with the same name as the version, e.g. 1.3.1 (or some generic name like `temp`).
3. On this branch make the necessary changes in the chart:
   1. Update all `Chart.yaml` files. Make sure 3 digit version without any suffix is updated in the file.
   2. Update any dependency chart versions. Make sure all the versions of other charts are frozen versions (not develop/prerelease versions).
   3. Update `values.yaml` with the tagged version of all the Docker images. (There are multiple places where tags of docker images have to be updated. Find all lines containing `image:`.)
4. Commit the changes on this branch
5. Create a tag following tagging conventions out of this temporary branch. E.g. `v1.3.1`.
6. The GitHub workflow action to package Helm charts and push to the `openg2p-helm` repo should be triggered automatically.
7. Delete the temporary branch that was created in the above steps.
8. Update the [Versions](../versions.md) page on this documentation.
9. Once the GitHub actions are finished, the packages should be available on Rancher also (Use the refresh button on the Rancher Charts page to see the latest versions).

{% hint style="warning" %}
Do NOT make these changes to the temporary branch directly on GitHub. Create the temporary branch on GitHub first, commit all the changes locally, and then make a push to the temporary branch from local. (This is done this way because of how the GitHub action gets triggered.)
{% endhint %}

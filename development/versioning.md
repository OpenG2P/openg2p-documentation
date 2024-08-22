---
description: Version and branch conventions followed in OpenG2P
---

# Versioning

In general, OpenG2P follows  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). However,  there are exceptions concerning Oodo modules which follow [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning). &#x20;

Versioning is applied to the following artifacts. &#x20;

| Artifacts           | Versioning                                                                                                                                                                                                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Non-Odoo modules    |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                                                                                                                                                                                                                                                              |
| Odoo modules        | [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning).  To indicate the maturity of a version (like alpha/beta etc.) use `development_status` field in the `__manifest__.py` file as described [here](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/oca\_module\_lifecycle\_development\_status.rst). |
| Dockers             |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                                                                                                                                                                                                                                                              |
| Helm Charts         |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). See more details [here](../deployment/helm-charts.md#helm-chart-versions).                                                                                                                                                                                                                  |
| Repository branches | As per guidelines given [here](versioning.md#git-branch-and-tag).                                                                                                                                                                                                                                                                                            |

## Pre-release versions

Pre-release versions maybe appended with a tag like "rc1", "rc2" etc. For example "1.2.0-rc1".  Such a tag will be reflected in all the artifacts -- Odoo, Dockers, Helm Charts etc.

## Git branch and tag

Typically, branches on Git repositories match the version number of the module/component.

For **Odoo** module repositories, a prefix of Odoo version is added to the branch name, e.g. `17.0-1.0.0, 17.0-develop.`Within a branch, multiple Git tags may be created like `17.0-1.0.0-rc1`, `17.0-1.0.0-rc2` etc.

For **non-Odoo** module repositories, you should find a `develop` branch in the repo where in-progress work may be checked-in.

For releases, a release branch is forked out of the "develop" branch and given a version number for the release (like `1.2.0-rc1` or `1.3.0`). Subsequently, release specific check-ins like bug fixes are made on this branch. For the final release, this branch is Git tagged, frozen (no further check-ins allowed) and merged into the `develop` branch. Thus, all the changes related to the release are available in `develop` for further development. The recommended Github tagging convention for a final release is to have a prefix `v` before the version number. For example, `v15.0.1.0.0, release-15.0.1.0.0, v1.0.0, release-1.0.0`

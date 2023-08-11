# Contributing

## Introduction

OpenG2P is a collaborative effort of several contributors. We welcome contributions to the OpenG2P Project.

## Issues

Raise bugs/issues/tasks on GitHub Issues of individual repositories.

All the issues and tasks are tracked using [Jira](https://openg2p.atlassian.net).

## Discussions

Join our [community](https://community.openg2p.org) for keeping track of key announcements, and updates and discuss any matters related to the project with the larger community. You may post your technical questions on the platform here.

## Code contributions

To contribute code to the OpenG2P project, follow the steps given below:

1. Create an issue on Github related to your task.
2. Fork the corresponding repository.
3. Commit your changes in your forked repo. Make sure the issue id of GitHub is mentioned in square braces, e.g. `[#6] Minor changes to fix the bug.`
4. Raise a Pull Request (PR) on the appropriate branch. In general, it is safe to send PRs to `develop` branch of a repo.
5. The PRs shall be reviewed by the technical team and merged after approval.

## Coding conventions

* For Odoo modules, follow the [Odoo Coding Guidelines.](https://www.odoo.com/documentation/15.0/contributing/development/coding\_guidelines.html)
* For non-Odoo Python code, follow [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/).

## Documentation contributions

The documentation of the project is available as `.md` files in the [Documentation repository](https://github.com/openg2p/openg2p-documentation). To highlight a correction or request for additional documentation, raise a GitHub Issue on the repository. To contribute to the documentation follow the steps given under [Code contributions](contributing-to-openg2p.md#code-contributions).

## Versioning of modules

For Odoo modules, follow the [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning). To indicate the maturity of a version (like alpha/beta etc.) use `development_status` field in the `__manifest__.py` file as described [here](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/oca\_module\_lifecycle\_development\_status.rst).

For Non-Odoo modules, follow [Semantic Versioning](https://semver.org/).

OpenG2P release will follow Semantic Versioning. For GitHub branches and tags versions, refer to the sections below.

## Branching and tagging conventions

For Odoo module repositories, a prefix of Odoo version is added to the branch name, e.g. `15.0-1.0.0, 15.0-develop.`Within a branch, multiple Git tags may be created like `15.0-1.0.0-rc1`, `15.0-1.0.0-rc2` etc.

For non-Odoo module repositories, you should find a `develop` branch in the repo where in-progress work may be checked-in.

For releases, a release branch is forked out of the `develop` branch and subsequently, release specific check-ins like bug fixes are made on this branch. For the final release, this branch is Git tagged, frozen (no further check-ins allowed) and merged into the `develop` branch. Thus, all the changes related to the release are available in `develop` for further development. The recommended Github tagging convention for a final release is to have a prefix `v` or `release` before the version number. For example, `v15.0.1.0.0, release-15.0.1.0.0, v1.0.0, release-1.0.0`

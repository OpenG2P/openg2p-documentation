# Contributing to OpenG2P

## Introduction

We welcome contributions to the OpenG2P Project.

## Issues

Raise bugs/issues/tasks on Github Issues of individual repo.

## Code contributions

1. Create an issue on Github related to your task.
2. Fork the corresponding repository.
3. Commit your changes in your forked repo. Make sure issue id of Github is mentioned in square braces, e.g. `[#6] Minor changes to fix the bug.`
4. Raise a Pull Request (PR) on the appropriate branch. In general it is safe to send PRs to `develop` branch of a repo.
5. The PRs shall be reviewed by the technical team and merged after approval.

## Coding conventions

* For Odoo modules, follow the [Odoo Coding Guidelines.](https://www.odoo.com/documentation/15.0/contributing/development/coding\_guidelines.html)
* For non-Odoo Python code, follow [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/).

## Documentation contributions

The documentation of the project is available as `.md` files in the [Documentation repository](https://github.com/openg2p/documentation). To highlight a correction or request for additional documentation, raise a Github Issue on the repository. To contribute to the documentation follow the steps given under [Code contributions](contributing-to-openg2p.md#code-contributions).

## Branching conventions

For Odoo module repositories, a prefix of Odoo version is added to the branch name, e.g. `15.0-develop`. For non-Odoo module repositories, you should find a `develop` branch where in-progress work may be checked-in.

A release branch is forked out of the `develop` branch and subsequently release specific check-ins are made on this branch. After the release, this branch is tagged, frozen and merged into the `develop` branch. Thus, all the changes related to the release are available in `develop` for further development.

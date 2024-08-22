---
description: Version and branch conventions followed in OpenG2P
---

# Versioning

In general, OpenG2P follows  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). However,  there are exceptions concerning Oodo modules which follow [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning). &#x20;

## Versioning conventions for artifacts

| Artifacts           | Versioning                                                                                                                                                                                                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Non-Odoo modules    |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                                                                                                                                                                                                                                                              |
| Odoo modules        | [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning).  To indicate the maturity of a version (like alpha/beta etc.) use `development_status` field in the `__manifest__.py` file as described [here](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/oca\_module\_lifecycle\_development\_status.rst). |
| Dockers             |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                                                                                                                                                                                                                                                              |
| Helm Charts         |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). See more details [here](../deployment/helm-charts.md#helm-chart-versions).                                                                                                                                                                                                                  |
| Repository branches | As per guidelines given [here](versioning.md#git-branch-and-tag).                                                                                                                                                                                                                                                                                            |



## Git branch and tag

A moving branch may have names like `develop`, `17.0-develop` or even `1.2`.  Here `1.2` is considered a moving branch until a tag like `v1.2.2` is created. &#x20;

## Frozen versions

A version of any artifact (like a Helm chart, docker, git repository etc.)  is considered "frozen", or "tagged', or "pegged" if all the components, and source code inside that artifact is frozen -- there are no moving versions like "develop". Thus, a frozen version allows tracing to exact versions of code at the lower most level.  Therefore, a frozen version artifact may be exactly recreated if required.

A 3 digit version is deemed frozen if it does not have any other suffixes like -`develop` or `-alpha` etc. Conversely, any version which is not 3 digit or has a suffix, cannot be considered a frozen version -- the version may have parts that are moving.  Here are some examples to illustrate the same:



<table><thead><tr><th width="200">Artifact</th><th width="185">Version</th><th>Interpretation</th></tr></thead><tbody><tr><td>Git repository</td><td>v1.2.0</td><td>This is Git tag (not branch) and is frozen as tags are generally not moved</td></tr><tr><td>Git repository</td><td>1.2</td><td>A moving branch</td></tr><tr><td>Git repository</td><td>1.2.0</td><td>A branch created temporarily only to tag a version</td></tr><tr><td>Odoo module</td><td>17.0.1.2.0-develop</td><td>Moving version related to branch 1.2.  </td></tr><tr><td>Odoo module</td><td>17.0.1.2.0</td><td>Frozen version </td></tr><tr><td>Docker</td><td>1.2.0</td><td>Frozen package</td></tr><tr><td>Docker</td><td>1.2</td><td>Moving version</td></tr><tr><td>Docker</td><td>1.2-develop</td><td>Moving version</td></tr><tr><td>Helm chart</td><td>0.0.0-develop</td><td>Moving version - latest in <code>develop</code> branch</td></tr><tr><td>Helm chart</td><td>1.2.3</td><td>Frozen package</td></tr></tbody></table>


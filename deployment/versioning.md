---
description: Version and branch conventions followed in OpenG2P
---

# Versioning

In general, OpenG2P follows  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). However,  there are exceptions concerning Oodo modules which follow [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning). &#x20;

## Versioning conventions for artifacts

| Artifacts        | Versioning                                                                                                                    |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Helm Charts      |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html). See more details [here](helm-charts.md#helm-chart-versions). |
| Dockers          |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                               |
| Git repositories | As per guidelines given [here](versioning.md#git-repository-versioning).                                                      |
| Odoo modules     | [Odoo Versioning](https://setuptools-odoo.readthedocs.io/en/latest/#versioning)                                               |
| Non-Odoo modules |  [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html)                                                               |

## Git repository versioning

All repositories have a running `develop` , `main` or `master` branch which contains latest development code.  To release a specific version a branch like `1.2` may be created and further development on this  branch is controlled and typically restricted to only bug fixes. On branch `1.2` Git tags may be created. These tags must necessarily follow 3 digit version like `v1.2.4`.  Note that a Git tag always has the `v` prefix.  For Odoo repositories, the Odoo version is prefixed on the branch name. Example `17.0-develop`, `17.0-1.2`. However, the Git tag does not contain this prefix - the same will still be v`1.2.5` for example.

## Frozen versions

A version of any artifact (like a Helm chart, docker, git repository etc.)  is considered "frozen", or "tagged', or "pegged" if all the components, and source code inside that artifact is frozen -- there are no moving versions like "develop". Thus, a frozen version allows tracing to exact versions of code at the lower most level.  Therefore, a frozen version artifact may be exactly recreated if required.

A 3 digit version is deemed frozen if it does not have any other suffixes like -`develop` or `-alpha` etc. Conversely, any version which is not 3 digit or has a suffix, cannot be considered a frozen version -- the version may have parts that are moving. &#x20;

{% hint style="warning" %}
EXCEPTION: In case of sub modules within a repository (Odoo modules in Odoo repositories, and FastAPI modules in other repositories), we are not maintaining the sub module version as it requires high maintenance effort to increment the version numbers in the manifest files of these modules.  The version number may indicate a version on the branch but it is advised to trace the exact code based on repository tag.
{% endhint %}

Here are some examples to illustrate the same:

<table><thead><tr><th width="200">Artifact</th><th width="185">Version</th><th>Interpretation</th></tr></thead><tbody><tr><td>Git repository</td><td>v1.2.0</td><td>This is Git tag (not branch) and is frozen as tags are generally not moved</td></tr><tr><td>Git repository</td><td>1.2</td><td>A moving branch</td></tr><tr><td>Git repository</td><td>1.2.0</td><td>A branch created temporarily only to tag a version</td></tr><tr><td>Odoo module</td><td>17.0.1.2.0</td><td>On branch 17.0-1.2, but may be moving. <em>See note above</em></td></tr><tr><td>Docker</td><td>1.2.0</td><td>Frozen package</td></tr><tr><td>Docker</td><td>1.2</td><td>Moving version</td></tr><tr><td>Docker</td><td>1.2-develop</td><td>Moving version</td></tr><tr><td>Helm chart</td><td>0.0.0-develop</td><td>Moving version - latest in <code>develop</code> branch</td></tr><tr><td>Helm chart</td><td>1.2.3</td><td>Frozen package</td></tr></tbody></table>


---
description: >-
  Agri Stack versions: Alpha, the first version, and the modules it is
  installed from, with links to their current versions and change logs.
---

# Versions

## Agri Stack Alpha

**Status: Alpha.** The first version of Agri Stack. It installs and passes the [test](../deployment/testing.md) end to end; features, APIs and chart values may still change.

**What it includes:**

* The Exchange: the Composite, Partner Management, and the Consent Manager with its partner portal. Partners use it through use cases, with the farmer's consent.
* Two reference registries: the Farmer Registry and the Crop Sown Registry.
* One use case: `loan-profile`.
* Setup at install: the Composite's key, its onboarding in every Partner Management, and the partner portal realm.

### Module versions

Alpha uses the `develop` versions of all its modules. The versions will be tagged later, after feedback and testing are incorporated. Each module's current version and change log: [OpenG2P Versions](https://openg2p.github.io/versions/index.html).

| Module | Charts | Installed in | Versions and change log |
| --- | --- | --- | --- |
| Composite | `openg2p-agri-composite` | The Exchange | [agri-stack](https://openg2p.github.io/versions/agri-stack/CHANGELOG.html) |
| Commons | `openg2p-commons-base`, `openg2p-commons-services` | The Exchange and every department | [commons](https://openg2p.github.io/versions/commons/CHANGELOG.html) |
| Farmer Registry | `openg2p-farmer-registry` | Agriculture Department (`trial`) | [farmer-registry](https://openg2p.github.io/versions/farmer-registry/CHANGELOG.html) |
| Crop Sown Registry | `openg2p-crop-sown-registry` | Crops Department (`dept1`) | [crop-sown-registry](https://openg2p.github.io/versions/crop-sown-registry/CHANGELOG.html) |

Commons Services pins the versions of the services it installs. Their change logs: [Partner Management](https://openg2p.github.io/versions/partner-management/CHANGELOG.html), [Consent Manager](https://openg2p.github.io/versions/consent-manager/CHANGELOG.html), [keycloak-init](https://openg2p.github.io/versions/keycloak-init/CHANGELOG.html), [Master Data](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html), [Audit Manager](https://openg2p.github.io/versions/audit-manager/CHANGELOG.html), [IAM](https://openg2p.github.io/versions/iam/CHANGELOG.html), [Mock Identity System](https://openg2p.github.io/versions/mock-id-system/CHANGELOG.html).

**Installing Alpha:** the latest `0.0.0-develop.NN` of each chart (the default in Rancher), every install of one Agri Stack from builds of the same day. After any upgrade, run the [test](../deployment/testing.md).

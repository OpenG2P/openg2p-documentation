---
description: >-
  Agri Stack versions and source code: Alpha, the first version, and every
  module it is installed from, with its charts, source code repository, and
  current versions and change log.
---

# Versions & Source Code

## Agri Stack Alpha

**Status: Alpha.** The first version of Agri Stack. It installs and passes the [test](../deployment/testing.md) end to end; features, APIs and chart values may still change.

**What it includes:**

* The Exchange: the Composite, Partner Management, and the Consent Manager with its partner portal. Partners use it through use cases, with the farmer's consent.
* Two reference registries: the Farmer Registry and the Crop Sown Registry.
* One use case: `loan-profile`.
* Setup at install: the Composite's key, its onboarding in every Partner Management, and the partner portal realm.

## Modules

Alpha uses the `develop` versions of all its modules. The versions will be tagged later, after feedback and testing are incorporated. Each module's current version and change log: [OpenG2P Versions](https://openg2p.github.io/versions/index.html).

What each module does: [Architecture & Concepts](../architecture/README.md).

### Installed from their own charts

| Module | Charts | Installed in | Source code | Versions and change log |
| --- | --- | --- | --- | --- |
| Composite | `openg2p-agri-composite` | The Exchange | [OpenG2P/agri-stack](https://github.com/OpenG2P/agri-stack) | [agri-stack](https://openg2p.github.io/versions/agri-stack/CHANGELOG.html) |
| Commons | `openg2p-commons-base`, `openg2p-commons-services` | The Exchange and every department | [OpenG2P/commons](https://github.com/OpenG2P/commons) | [commons](https://openg2p.github.io/versions/commons/CHANGELOG.html) |
| Farmer Registry | `openg2p-farmer-registry` | Agriculture Department (`trial`) | [OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) | [farmer-registry](https://openg2p.github.io/versions/farmer-registry/CHANGELOG.html) |
| Crop Sown Registry | `openg2p-crop-sown-registry` | Crops Department (`dept1`) | [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) | [crop-sown-registry](https://openg2p.github.io/versions/crop-sown-registry/CHANGELOG.html) |

### Installed by Commons Services

Commons Services pins their versions.

| Module | Source code | Versions and change log |
| --- | --- | --- |
| Partner Management | [OpenG2P/partner-management](https://github.com/OpenG2P/partner-management) | [partner-management](https://openg2p.github.io/versions/partner-management/CHANGELOG.html) |
| Consent Manager, with its partner portal | [OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager) | [consent-manager](https://openg2p.github.io/versions/consent-manager/CHANGELOG.html) |
| Master Data | [OpenG2P/master-data-service](https://github.com/OpenG2P/master-data-service) | [master-data-service](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html) |
| Audit Manager | [OpenG2P/audit-manager](https://github.com/OpenG2P/audit-manager) | [audit-manager](https://openg2p.github.io/versions/audit-manager/CHANGELOG.html) |
| IAM | [OpenG2P/iam](https://github.com/OpenG2P/iam) | [iam](https://openg2p.github.io/versions/iam/CHANGELOG.html) |
| Approval Workflow Engine (registries) | [OpenG2P/awe](https://github.com/OpenG2P/awe) | [awe](https://openg2p.github.io/versions/awe/CHANGELOG.html) |
| keycloak-init (realms, clients, roles) | [OpenG2P/keycloak-init](https://github.com/OpenG2P/keycloak-init) | [keycloak-init](https://openg2p.github.io/versions/keycloak-init/CHANGELOG.html) |
| Mock Identity System (testing) | [OpenG2P/mock-id-system](https://github.com/OpenG2P/mock-id-system) | [mock-id-system](https://openg2p.github.io/versions/mock-id-system/CHANGELOG.html) |
| eSignet (national-ID login) | [mosip/esignet](https://github.com/mosip/esignet) | MOSIP's releases |

**Installing Alpha:** the latest `0.0.0-develop.NN` of each chart (the default in Rancher), every install of one Agri Stack from builds of the same day. After any upgrade, run the [test](../deployment/testing.md).

## Licence

All modules are open source under the Mozilla Public License 2.0 ([licence](../../license.md)).

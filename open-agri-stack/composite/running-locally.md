---
description: >-
  Running the Composite and its tests on a laptop.
---

# Running the Composite Locally

The service is in [`composite/backend`](https://github.com/openg2p/agri-stack/tree/develop/composite/backend). It needs Python 3.11 or later (the image uses 3.12), [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) from `develop` (its `PartnerMgmtKeyStore`, for partner keys from PM, is not in a 1.2.x release yet) and `iam-core` from the [IAM](https://github.com/OpenG2P/iam) `develop` line (the console's staff login; its 1.4.x releases do not work with the framework's `develop`).

```bash
cd composite/backend
python3.11 -m venv .venv && . .venv/bin/activate
pip install "git+https://github.com/openg2p/openg2p-fastapi-common@develop#subdirectory=openg2p-fastapi-common"
pip install "git+https://github.com/openg2p/iam@develop#subdirectory=iam-core"
pip install -e ".[test]"
pytest                                     # no network needed

python ../../scripts/partner_kit.py keys      # test keys in scripts/kit-out (git-ignored)
export AGRI_COMPOSITE_USE_CASES_DIR=../use-cases
export AGRI_COMPOSITE_SIGNING_P12_PATH=../../scripts/kit-out/composite.p12 AGRI_COMPOSITE_SIGNING_P12_PASSWORD=openg2p-test
export AGRI_COMPOSITE_PARTNER_MGMT_API_URL=http://localhost:9001          # a PM partner-api
export AGRI_COMPOSITE_REGISTRIES='{"farmer-registry":{"url":"http://localhost:9002/dci/registry/sync/search"},
                                  "crop-sown-registry":{"url":"http://localhost:9003/dci/registry/sync/search"}}'
python -m openg2p_agri_composite.main run  # http://localhost:8000/docs
```

* The ports are examples: point `PARTNER_MGMT_API_URL` and `REGISTRIES` at a PM partner API and the registries' partner APIs you can reach, e.g. through `kubectl port-forward`.
* The partner's and the Composite's public keys must be in that PM (`PARTNER_BANK_A`, `PARTNER_AGRI_COMPOSITE`), and the partner needs a policy there for the use case (`loan-profile@1`); `partner_kit.py keys` prints the onboarding requests, the partner's with its policy for the use case.
* With the console off (the default outside the chart) the service has no database; startup only loads the use cases. The chart turns the console on, which needs a database, IAM and Redis (see [Composite console](console.md)).
* The chart sets the consent mode to `exchange`. Run this way, set `AGRI_COMPOSITE_CONSENT_MODE=exchange` too, and `AGRI_COMPOSITE_CONSENT_EXCHANGE_CM_URL` to a reachable CM partner API.
* Every setting is listed in [Use-Case Configuration](use-case-configuration.md).

Then call it as a partner:

```bash
python ../../scripts/partner_kit.py describe --url http://localhost:8000
python ../../scripts/partner_kit.py call --url http://localhost:8000 \
    --subject FAYDA_FAN:<FAN of a registered farmer> --param crop_year=2019 --param season=SEASON_MEHER
```

## Building the image

The Dockerfile is [`composite/docker/agri-composite-api/Dockerfile`](https://github.com/openg2p/agri-stack/blob/develop/composite/docker/agri-composite-api/Dockerfile). CI builds and publishes the image (`openg2p/openg2p-agri-composite-api`) and the chart only when something under `composite/` changes, not on documentation-only pushes.

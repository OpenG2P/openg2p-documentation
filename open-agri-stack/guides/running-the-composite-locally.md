---
description: >-
  Running the use-case composite and its tests on a laptop.
---

# Running the Composite Locally

The service is in [`composite/backend`](https://github.com/openg2p/agri-stack/tree/develop/composite/backend). It needs Python 3.11 and [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) from `develop` (its `PartnerMgmtKeyStore`, for partner keys from PM, is not in a 1.2.x release yet).

```bash
cd composite/backend
python3.11 -m venv .venv && . .venv/bin/activate
pip install "git+https://github.com/openg2p/openg2p-fastapi-common@develop#subdirectory=openg2p-fastapi-common"
pip install -e ".[test]"
pytest                                     # no network needed

python ../scripts/partner_kit.py keys      # test keys in scripts/kit-out (git-ignored)
export AGRI_COMPOSITE_USE_CASES_DIR=../use-cases
export AGRI_COMPOSITE_SIGNING_P12_PATH=../scripts/kit-out/composite.p12 AGRI_COMPOSITE_SIGNING_P12_PASSWORD=openg2p-test
export AGRI_COMPOSITE_PARTNER_MGMT_API_URL=http://localhost:9001          # a PM partner-api
export AGRI_COMPOSITE_REGISTRIES='{"farmer-registry":{"url":"http://localhost:9002/dci/registry/sync/search"},
                                  "crop-sown-registry":{"url":"http://localhost:9003/dci/registry/sync/search"}}'
python -m openg2p_agri_composite.main run  # http://localhost:8000/docs
```

* The ports are examples: point `PARTNER_MGMT_API_URL` and `REGISTRIES` at a PM partner API and the registries' partner APIs you can reach, e.g. through `kubectl port-forward`.
* The partner's and the composite's public keys must be in that PM (`PARTNER_BANK_A`, `PARTNER_AGRI_COMPOSITE`); `partner_kit.py keys` prints the onboarding requests.
* The service has no database; startup only loads the use cases.
* Every setting is listed in [composite configuration](composite-configuration.md).

Then call it as a partner:

```bash
python ../scripts/partner_kit.py describe --url http://localhost:8000
python ../scripts/partner_kit.py call --url http://localhost:8000 \
    --subject FAYDA_FAN:<FAN of a registered farmer> --param crop_year=2019 --param season=SEASON_MEHER
```

## Building the image

The Dockerfile is [`composite/docker/agri-composite-api/Dockerfile`](https://github.com/openg2p/agri-stack/blob/develop/composite/docker/agri-composite-api/Dockerfile). CI builds and publishes the image (`openg2p/openg2p-agri-composite-api`) and the chart only when something under `composite/` changes, not on documentation-only pushes.

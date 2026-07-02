---
description: openg2p-g2p-bridge-example-bank (bank simulator)
---

# Example Bank

The Example Bank is bundled in the consolidated `g2p-bridge` monorepo (under `example-bank/`) and packaged in the `openg2p-bridge` Helm chart — it is no longer a separate repository.

It is a Bank simulator that provides implementations of the APIs a Sponsor Bank would expose.

This Example Bank should not be deployed in production. The functionality provided by this Example Bank - should be provided by the Sponsor Bank (where the bank account that funds the benefit program is serviced)

The Example Bank repository has 3 projects

1. openg2p-g2p-bridge-example-bank-models
2. openg2p-g2p-bridge-example-bank-api
3. openg2p-g2p-bridge-example-bank-celery

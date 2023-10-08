---
description: Work in progress
---

# G2P Payments Bridge

## Introduction

The G2P Payments Bridge (GPB) is expected to fit the payment chain as shown below.&#x20;

The module is envisaged to exist as an independent module in bridging the gap between a G2P system and a bank to initiate large-scale G2P cash transfers. Being specific to G2P transfers, (and not P2G, P2P, P2M etc), the module promises to be low cost, simple in design, easy to install and highly performant as real-time fast transfers are not a requirement in most social benefit transfer scenarios. However, the volume of transfers is expected to be large.&#x20;

The module will support the following functionalities at a high level

1. Upstream interface layer compliant with G2P Connect or any other standard
2. Downstream interface layer to connect to bank with specific/proprietary interfaces
3. Query ID Account Mapper to fetch individual bank account information (optional)
4. History of past transactions
5. Reporting

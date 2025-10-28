# Cash, goods & services

The G2P Bridge subsystem of OpenG2P handles all kinds of commodities and services that a benefit program wishes to disburse. All commodities and services are internally classified into 5 types

1. **Cash - Digitally transferred** (into beneficiary bank accounts or mobile wallets)
2. **Cash - Physically** given to beneficiaries by on field agents (G2P Bridge transfers money into accounts or wallets of agents)
3. **Goods** - Staples, fuels, books and other goods
4. **Services** - Any kind of services delivered as part of benefit delivery
5. **Combination** - A combination of goods & services&#x20;

A single benefit program in the PBMS system might deliver more than one benefit (of varying types). However, prior to handing over the disbursement information to G2P Bridge, the upstream PBMS has to split the disbursement into distinct disbursement envelopes. Each envelope handles exactly one benefit code. Thus if a benefit program is configured to distribute 3 products, let's say, Wheat, Soy Beans and Oil, the PBMS will create 3 envelopes in G2P Bridge and hand over the individual disbursements under each of these distinct envelopes.

The processing of disbursement instructions within an envelope depends on the envelope's benefit code type (one of the 5 types given above).

The following diagram shows the detailed workflow within G2P Bridge for each of these product types.

{% embed url="https://miro.com/app/board/uXjVJf5HgOI=/?share_link_id=142748356432" %}

\
\
\

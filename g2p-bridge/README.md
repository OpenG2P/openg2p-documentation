---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# G2P Bridge

The G2P Bridge subsystem bridges the upstream Program Management (aka MIS systems) modules with the downstream Service Providers.&#x20;

The G2P Bridge system is designed to cater to programs that offer Commodities as well as Services to their beneficiaries, handling both digital as well as physical deliveries.

**Digital Cash Transfers** to beneficiaries' bank accounts & mobile money wallets are treated as a degenerate case of digital transfer of commodities. In this case, the Bridge interfaces with the Sponsor Bank (the bank that services the program funding account) to initiate these beneficiary transfers. The sponsor bank in turn interfaces with the National Switch / Clearing network to effect these payments.

{% embed url="https://miro.com/app/board/uXjVIXaOBI8=/?embedAutoplay=true&share_link_id=625316279070" %}
G2P Bridge overview
{% endembed %}

Being a G2P system (not a P2G, P2P, P2M, etc), the platform does not desire to offer high performance and real time cash transfers, since these features are not typically required in a G2P transfer chain. Rather, the G2P Bridge emphasises on the following characteristics

1. Operate on an asynchronous paradigm
2. Handle high volume of transactions
3. Ease of operation with low costs of maintenance and operations
4. Efficient reconciliations
5. Extensibility to allow easy integrations with Sponsor Banks and other Service Providers

The following figure shows how the G2P Bridge digital cash transfer subsystem fits into the overall G2P landscape



{% embed url="https://miro.com/app/board/uXjVKX-8Zq0=/?embedAutoplay=true&share_link_id=992769892719" %}
G2P Bridge in the G2P landscape
{% endembed %}

## Technical overview

{% embed url="https://miro.com/app/board/uXjVKWoMWx0=/?embedAutoplay=true&share_link_id=312099976717" %}
G2P Bridge - Technical Architecture
{% endembed %}




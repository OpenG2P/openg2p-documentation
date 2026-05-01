---
description: Discussion
---

# Alternate Data Sharing Mechanisms

Social Registry supports [Data Sharing mechanisms](../../features/data-share/). Apart from the mechanisms already described, alternate data-sharing mechanisms are being considered for large-volume data sharing across networks.

* While Kafka can be used for data sharing it has the following limitations:
  * It recreates partitions if the TCP connection drops (explain)
  * Accessing Kafka across networks on the Internet is a challenge as it does not run on standard ports like 80,443.  This makes it hard to make it work across systems as firewall rules prevent access to non-standard ports.
  * So Kafka is a great option for sharing data within a network, or data center but not for sharing data across data centers.
* In OpenG2P we are considering similar system for sharing registry data for printing of social ID cards.

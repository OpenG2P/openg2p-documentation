---
description: >-
  This guide explains how to configure Slack alerts for a Kubernetes cluster
  using Prometheus Alertmanager.
---

# Set up Slack alerts for a Kubernetes cluster

## **Introduction**

Alerting is essential for monitoring modern systems, ensuring issues are detected and communicated in real-time. In Kubernetes, tools like Prometheus and Alertmanager handle metrics monitoring and alert routing to channels like Slack or email. Effective alerting minimizes downtime, improves response times, and maintains system performance.

## Prerequisites

* A Kubernetes cluster with Prometheus and Alertmanager installed. It comes by default when installing cattle-monitoring-system.
* A Slack workspace with a channel for receiving alerts.
* Permissions to create and manage Slack webhooks.

## Procedure

1. **Create a Slack Incoming Webhook.**
   1. Go to the Slack [API Webhooks page](https://api.slack.com/messaging/webhooks).
   2. Create a new Slack App (if you don’t have one already).
   3. Add an **Incoming Webhook** to the app.
   4. Select the Slack channel where you want alerts to appear.
   5. Copy the generated Webhook URL (e.g., `https://hooks.slack.com/services/...`).
2. **Deploy alerting configuration to kuberenets cluster.**
   1. Clone the [repository](https://github.com/OpenG2P/openg2p-deployment/tree/main/alerting) to you local and update the required changes mentioned below.
   2. Update **slack\_api\_url** and **channel** in **alertmanager.yaml**&#x20;
   3.  Modify the `routes` and `receivers` in the **alertmanager.yaml** configuration to customize which alerts are sent to Slack., as shown below.

       ```yaml
       routes:
       - match:
           alertname: Watchdog
         receiver: 'null'
       ```
   4. The monitoring package provided by Rancher includes various default alerting rules, which are often sufficient for most use cases. Sample custom alerts are available under the `custom-alerts` directory. Modify these as needed.
   5. Add cluster name in, `patch-cluster-name.yaml`
   6. Run **install.sh** to apply the configuration for alertmanager.
   7. And restart the alert-manager service on k8s-cluster.
   8.  Verify whether the alerts are firing from the Prometheus UI and check if Slack notifications are being received.\


       <figure><img src="../../.gitbook/assets/image (22).png" alt=""><figcaption><p><em><strong>Prometheus dashboard</strong></em><br></p></figcaption></figure>

       <figure><img src="../../.gitbook/assets/image (1) (1).png" alt=""><figcaption><p><em><strong>slack channel</strong></em></p></figcaption></figure>


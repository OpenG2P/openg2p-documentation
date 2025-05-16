---
description: >-
  This document provides a step-by-step guide to configure Slack alerts for a
  standalone node using the Netdata monitoring tool.
---

# Set Up Slack Alerts for a Standalone Node using Netdata

### 📘 Introduction to netdata

Netdata is an open-source, real-time monitoring tool designed to visualize and alert on system and application performance metrics. It provides powerful visualization dashboards, health monitoring with automatic alarms, and integrations with popular notification platforms like Slack.

### 🛠️ Step 1: Install netdata on the VM

1.  Run the following command to download and install Netdata:

    ```bash
    wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh && sh /tmp/netdata-kickstart.sh
    ```
2. ✅ Verify the script integrity
   * During the process, the script will validate itself. If successful, it will return: `OK, VALID`&#x20;
   *   You can use this command to check the status of netdata server.

       ```bash
       sudo systemctl status netdata
       ```

### 🔔 Step 2: Configure slack notifications

1.  Change to the Netdata config directory:

    ```bash
    cd /etc/netdata 2>/dev/null || cd /opt/netdata/etc/netdata
    ```
2.  Edit the Slack notification config:

    ```bash
    sudo ./edit-config health_alarm_notify.conf
    ```
3.  Update the configuration as follows:

    ```bash
    SEND_SLACK="YES"
    SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXXXXXX/XXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    DEFAULT_RECIPIENT_SLACK="#alarms"  # replace 'alarms' with your Slack channel name
    ```
4. If you don't have a Slack webhook URL, you can create one by following the link below.\
   [Create a Slack Incoming Webhook](https://docs.openg2p.org/deployment/deployment-guide/set-up-slack-alerts-for-a-kubernetes-cluster)

### 💾 Step 3: Configure disk usage alert

1.  Navigate to the health configuration directory:

    ```bash
    cd /etc/netdata 2>/dev/null || cd /opt/netdata/etc/netdata
    ```
2.  Edit the disk usage alarm:

    ```bash
    sudo ./edit-config health.d/disk_usage.conf
    ```
3.  Example configuration:

    ```bash
    # you can disable an alarm notification by setting the 'to' line to: silent
    # -----------------------------------------------------------------------------
    # low disk space
    # checking the latest collected values
    # raise an alarm if the disk is low on available disk space
    template: disk_space_usage
    on: disk.space
    class: Utilization
    type: System
    component: Disk
    chart labels: mount_point=!/dev !/dev/* !/run !/run/* !HarddiskVolume* *
    calc: $used * 100 / ($avail + $used)
    units: %
    every: 1m
    warn: $this > 90
    crit: $this > 95
    delay: up 1m down 15m multiplier 1.5 max 1h
    repeat: warning 1200s critical 600s
    summary: Disk ${label:mount_point} space usage
    info: Total space utilization of disk ${label:mount_point} (ENV: sandbox )
    to: sysadmin
    ```

### 🔁 Step 4: Restart netdata

Restart Netdata to apply configuration changes:

```bash
sudo systemctl restart netdata
```

### 🧪 Step 5: Test slack alert delivery

1.  Run the following test command to trigger a dummy alert:

    ```bash
    cd /etc/netdata 2>/dev/null || cd /opt/netdata
    /usr/libexec/netdata/plugins.d/alarm-notify.sh test
    ```
2. ✅ You should receive a test message in your Slack channel.

### ❌ Step 6: Uninstall netdata (if needed)

If you want to remove Netdata from your system:

```
wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh && sh /tmp/netdata-kickstart.sh --uninstall
```

This setup helps ensure you are promptly notified of potential issues on your VM, enhancing system reliability and awareness. And you can refere more on netdata [here](https://learn.netdata.cloud/docs/netdata-agent/installation/linux/).

\

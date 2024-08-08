---
description: This guide is to fix "Storage Issues" caused by the NFS server on a node.
---

# "No Space Left on the Device" Warning

### Configuring Logrotate for Hourly Rotation

To manage storage issues caused by excessive log files, you can configure `logrotate` to handle log rotation on an hourly basis. This guide provides step-by-step instructions for modifying the `logrotate` configuration.\


1.  Open the `rsyslog` logrotate configuration file in a text editor:

    ```bash
    sudo vim /etc/logrotate.d/rsyslog
    ```
2. Modify the configuration to set up hourly rotation:
   1. Change the rotate directive to 6:\
      `rotate 6`
   2. Change the `weekly` directive to `hourly`:\
      `hourly`
   3. Add the `maxsize` directive if it's not already present:\
      `maxsize 0`
3.  Test the configuration to ensure there are no syntax errors:

    ```bash
    sudo logrotate -d /etc/logrotate.conf
    ```
4.  Open the logrotate timer configuration file in a text editor:

    ```bash
    sudo nano /lib/systemd/system/logrotate.timer
    ```
5. Modify the timer to trigger log rotation hourly:\
   Change `OnCalendar=daily` to `OnCalendar=hourly`
6.  Restart the `logrotate.timer` to apply the changes:

    ```bash
    sudo systemctl restart logrotate.timer
    ```

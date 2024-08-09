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

# No Space Left on the Device Warning

This guide is to resolve **Storage Issues** caused by the NFS server on a node.

### Configuring logrotate for hourly rotation

You can configure `logrotate` to handle log rotation on an hourly basis to manage storage issues caused by excessive log files.

Below are the step-by-step instructions for modifying the `logrotate` configuration.

1.  Open the `rsyslog` logrotate configuration file in a text editor.

    ```bash
    sudo vim /etc/logrotate.d/rsyslog
    ```
2. Modify the configuration to set up hourly rotation.
   1. Change the rotate directive to 6.\
      `rotate 6`
   2. Change the `weekly` directive to `hourly.`\
      `hourly`
   3. Add the `maxsize` directive if it is not already present.\
      `maxsize 0`
3.  Test the configuration to ensure there are no syntax errors.

    ```bash
    sudo logrotate -d /etc/logrotate.conf
    ```
4.  Open the logrotate timer configuration file in a text editor.

    ```bash
    sudo nano /lib/systemd/system/logrotate.timer
    ```
5. Modify the timer to trigger log rotation hourly.\
   Change `OnCalendar=daily` to `OnCalendar=hourly`
6.  Restart the `logrotate.timer` to apply the changes.

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart logrotate.timer
    ```
7.  If needed, clear other log files using the following commands to free up more storage.

    ```bash
    sudo rm -f /var/log/*.gz /var/log/*.1 /var/log/*.old
    ```

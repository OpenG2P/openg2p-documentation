---
description: >-
  This document explains how to set up a cron job to clear the cache on ubuntu
  systems.
---

# Automating Cache Cleanup on K8s Cluster Nodes with Cron Job

### Overview

Linux caches data in memory to improve performance, but over time, excessive caching can lead to high memory usage. To free up RAM, we can follow the below procedure.

### Procedure

To optimize memory usage on RKE2 cluster nodes, a cron job can be scheduled to periodically clear the RAM cache using the following command.

```bash
sync; echo 3 > /proc/sys/vm/drop_caches
```

* [ ] Use `sync` to ensure all data is written to disk.
* [ ] `echo 3` Clears **page cache, dentries, and inodes**.

### Steps to add the cron job

1. Open the crontab file for editing as a **root user**.\
   `crontab -e`
2. Add the following line to schedule the cache clearing every week.\
   `0 0 * * 6 sync; echo 3 > /proc/sys/vm/drop_caches`
3. Save and exit the editor.
4. Check if the cron job is added successfully.\
   `crontab -l`

This cron job will run every week on saturday 12am, ensuring that RAM cache is cleared periodically to optimize memory usage on RKE2 nodes.

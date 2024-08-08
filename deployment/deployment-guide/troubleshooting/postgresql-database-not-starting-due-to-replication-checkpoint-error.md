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

# PostgreSQL Database not Starting due to Replication Checkpoint Error

This guide is to fix PostgreSQL **replication checkpoint** error when the file is corrupted.

## **Common reasons for the error**

1. **Hardware Issues:** Disk failures or other hardware malfunctions.
2. **Software Issues:** Improper shutdowns, crashes, or incomplete write operations.

## Solution&#x20;

1. Connect to NFS node where the PostgreSQL data is stored.
2.  Navigate to PostgreSQL PVC.

    ```bash
    cd /path/to/your/postgres/pvc/data/pg_logical/
    ```
3.  Delete or rename the corrupted `replorigin_checkpoint` file.

    ```bash
    sudo mv replorigin_checkpoint replorigin_checkpoint_corrupted
    ```
4. Restart the PostgreSQL service to allow it to generate a new `replorigin_checkpoint` file.

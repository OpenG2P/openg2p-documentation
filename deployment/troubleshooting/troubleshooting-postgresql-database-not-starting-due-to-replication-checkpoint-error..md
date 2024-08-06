---
description: >-
  Guide to fix PostgreSQL "replication checkpoint" error when the file
  corrupted.
---

# Troubleshooting:PostgreSQL database not starting due to replication checkpoint error.

### Common reasons for this :

1. The checkpoint file might be corrupted due to hardware issues, such as disk failures, or software issues, like improper shutdowns or crashes.
2. If the database server crashed or was forcibly shut down while writing to the checkpoint file, it might lead to an incomplete or corrupted file.

### Solution :

1. Login to NFS node and cd in to postgres PVC and goto this directory called d**ata/pg\_logical/** and delete or raname the replorigin\_checkpoint to replorigin\_checkpoint\_currupted.&#x20;
2. And then restart the postgresql service to make service up. It will generate the new replorigin\_checkpoint file.

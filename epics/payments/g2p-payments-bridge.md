---
description: Work in progress
---

# G2P Payments Bridge

## Introduction

The G2P Payments Bridge (GPB) is expected to fit the payment chain as shown below.&#x20;

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/gpb-payment-chain.png" alt=""><figcaption></figcaption></figure>

The module is envisaged to exist as an independent module in bridging the gap between a G2P system and a bank to initiate large-scale G2P cash transfers. Being specific to G2P transfers, (and not P2G, P2P, P2M etc), the module promises to be low cost, simple in design, easy to install and highly performant as real-time fast transfers are not a requirement in most social benefit transfer scenarios. However, the volume of transfers is expected to be large.&#x20;

The module will support the following functionalities at a high level

1. Upstream interface layer compliant with G2P Connect or any other standard
2. Downstream interface layer to connect to bank with specific/proprietary interfaces
3. Query ID Account Mapper to fetch individual bank account information (optional)
4. History of past transactions
5. Reporting

## Architecture



<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/gpb-architecture.png" alt=""><figcaption><p>GPB Architecture</p></figcaption></figure>

### G2P Request Handler

This functional block receives cash transfer requests from upstream systems like OpenG2P via the G2P Connect Disbursement APIs. The block parses the incoming request and writes in the DB. The Disbursement API is assumed to be Synchronous such that after DB write, 200 OK is returned back to the caller.  The disbursement request is expected to be split into batches depending on the optimum performance of the system in terms of CPU and Memory.

When a Status API is called by the upstream system, this block reads the data from DB and returns back the status of requested transactions. The output may need to be 'paginated' depending on the volume of data returned.

### Requests DB

All the requests are persisted in a DB like Postgres along with status of each transfer request. THE DB would have the following tables:

#### 1. Payment Instructions

<table><thead><tr><th width="258">Column</th><th>Description</th></tr></thead><tbody><tr><td><code>batch_id</code></td><td>ID of the requested batch</td></tr><tr><td>request_id</td><td>ID of the request (this may be assigned by the G2P Request Handler in case not available in the Disbursement request)</td></tr><tr><td>request_timestamp</td><td></td></tr><tr><td>from_fa</td><td>Finanal Address of the sender. If there is only one sender, then this may be not be populated here, but configured in the system</td></tr><tr><td>to_fa</td><td>This may be an ID or contain account details (TBD)</td></tr><tr><td>amount</td><td></td></tr><tr><td>currency</td><td></td></tr><tr><td>status</td><td>Status of the request. This will be updated by multiple entities. The status enumeration may be NEW, FILED, PAID/FAILED</td></tr><tr><td>file</td><td>The file name in which the instruction has been written</td></tr><tr><td>error_code</td><td>Any error code if the status is FAILED. This will be used by the upsteam system to take necessary action like retry or giveup.</td></tr><tr><td>error_msg</td><td>Text error message </td></tr></tbody></table>

The table is expected to contain millions of records and a history of past transactions. Indexing of columns will be critical for performance. Besides, the previous records may be 'archived'. This could be achieved via horizontal partitioning. The management of DB in this regard needs to be worked out during implementation.

#### 2. File Dispatch

This table will hold the status of files dispatched

<table><thead><tr><th width="280">Column</th><th>Description</th></tr></thead><tbody><tr><td>file_name</td><td></td></tr><tr><td>status</td><td>NEW/DISPATCHED</td></tr></tbody></table>

## Payment File Creator

This block will be like a cronjob that runs periodically and does the following

* Read all the payment instructions that have not been processed yet (status: NEW) via direct query of DB
* Create an output file specific to the format accepted by a bank.&#x20;
* Write the file in the File Storage
* Update the status of all processed instructions as FILED.
* Update status in the File Dispatch table as NEW.

This functional block may be implemented as a script that is run as cronjob. The features will be implemented:

* Unique file names -- could be composed of the batch ID with a few more fields or it could be completely UUID based.
* Full in-memory processing
* Process data in a batch size as expected by the bank, provided the data can be accommodated in the RAM. (This should be fine because typically banks will not expect very large files. The number of rows may be in the order of a few thousand).
* Entire processing and updates in DB should happen atomically. In case there is a failure, the script should be able to discard the incomplete file and start all over again.
* The batch size should be configurable
* The file format will be specific to a bank. The script should be designed such that several file formats can be configured without having to make major changes in the code. &#x20;
* Configuration for bucket ID, location, and credentials for accessing [File Store](g2p-payments-bridge.md#file-store).

## File Store

This will typically be large S3-compliant storage (like MinIO or AWS S3) to store all the payment instruction files. It will have two buckets - one for outgoing payment files and another for received payment files.

## File Dispatcher

The File Dispatcher is also like a cronjob that does the following:

* Picks an unprocessed (un-sent) file from the bucket and using bank interface transfers the file to the bank. This could be a mechanism like SFTP. This would be very bank-specific.
* Update status in File Dispatch table in the DB as DISPATCHED.

Features:

* The implementation may be done via script called periodically.
* The file dispatch mechanism will be specific to a bank. The script should be designed such that several dispatch mechanisms can be configured without having to make major changes in the code




---
description: Work in progress
---

# G2P Payments Bridge

## Introduction

The G2P Payments Bridge (GPB) fits in the payment chain as shown below.&#x20;

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

This functional block receives cash transfer requests from upstream systems like OpenG2P via the G2P Connect Disbursement APIs. The block parses the incoming request and writes in the DB. The Disbursement API is assumed to be Synchronous such that after DB write, 200 OK is returned to the caller. The disbursement request is expected to be split into batches depending on the optimum performance of the system in terms of CPU and Memory.

When a Status API is called by the upstream system, this block reads the data from DB and returns the status of requested transactions. The output may need to be 'paginated' depending on the volume of data returned.

### Requests DB

All the requests are persisted in a DB like Postgres along with the status of each transfer request. The DB has the following tables:

#### 1. Payment Instructions

<table><thead><tr><th width="258">Column</th><th>Description</th></tr></thead><tbody><tr><td>batch_id</td><td>ID of the requested batch</td></tr><tr><td>request_id</td><td>ID of the request (this may be assigned by the G2P Request Handler in case not available in the Disbursement request)</td></tr><tr><td>request_timestamp</td><td></td></tr><tr><td>from_fa</td><td>Finanal Address of the sender. If there is only one sender, then this may be not be populated here, but configured in the system</td></tr><tr><td>to_fa</td><td>This may be an ID or contain account details (TBD)</td></tr><tr><td>amount</td><td></td></tr><tr><td>currency</td><td></td></tr><tr><td>status</td><td>Status of the request. This will be updated by multiple entities. The status enumeration may be NEW, FILED, PAID/FAILED</td></tr><tr><td>file</td><td>The file name in which the instruction has been written</td></tr><tr><td>error_code</td><td>Any error code if the status is FAILED. This will be used by the upsteam system to take necessary action like retry or giveup.</td></tr><tr><td>error_msg</td><td>Text error message </td></tr></tbody></table>

The table is expected to contain millions of records and a history of past transactions. Indexing of columns will be critical for performance. Besides, the previous records may be 'archived'. This could be achieved via horizontal partitioning. The management of DB in this regard needs to be worked out during implementation.

#### 2. File Outgoing

This table will hold the status of files dispatched

<table><thead><tr><th width="280">Column</th><th>Description</th></tr></thead><tbody><tr><td>file_name</td><td></td></tr><tr><td>status</td><td>NEW/DISPATCHED</td></tr></tbody></table>

#### 3. File Incoming

This table will hold the status of files received from bank.

<table><thead><tr><th width="280">Column</th><th>Description</th></tr></thead><tbody><tr><td>file_name</td><td></td></tr><tr><td>status</td><td>NEW/PROCESSED</td></tr></tbody></table>

## Payment File Creator

This block will be like a cronjob that runs periodically and does the following

* Read all the payment instructions that have not been processed yet (status: NEW) via direct query of DB
* Query ID Account Mapper if translation from ID to bank account information is required.
* Create an output file specific to the format accepted by a bank.&#x20;
* Write the file in the File Storage
* Update the status of all processed instructions as FILED.
* Update status in the [File Outgoing](g2p-payments-bridge.md#2.-file-outgoing) table as NEW.

This functional block may be implemented as a script that is run as cronjob. The features will be implemented:

* Unique file names -- could be composed of the batch ID with a few more fields or it could be completely UUID based.
* Full in-memory processing
* Process data in a batch size as expected by the bank, provided the data can be accommodated in the RAM. (This should be fine because typically banks will not expect very large files. The number of rows may be in the order of a few thousand).
* Entire processing and updates in DB should happen atomically. In case there is a failure, the script should be able to discard the incomplete file and start all over again.
* The batch size should be configurable
* The file format will be specific to a bank. The script should be designed such that several file formats can be configured without having to make major changes in the code. &#x20;
* Configuration for bucket ID, location, and credentials for accessing [File Store](g2p-payments-bridge.md#file-store).

## File Store

This will typically be large S3-compliant storage (like MinIO or AWS S3) to store all the payment instruction files. It will have two buckets:

* **Outgoing**: For outgoing payment files and another for received payment files.
* **Incoming**: For files fetched from bank(s)

## File Dispatcher

The File Dispatcher is like a cronjob that does the following:

* Picks an unprocessed (un-sent) file from the bucket and using bank interface transfers the file to the bank. This could be a mechanism like SFTP. This would be very bank-specific.
* Update status in [File Outgoing](g2p-payments-bridge.md#2.-file-outgoing) table in the DB as DISPATCHED.

Features:

* The implementation may be done via script called periodically.
* The file dispatch mechanism will be specific to a bank. The script should be designed such that several dispatch mechanisms can be configured without having to make major changes in the code

## File Fetcher

The File Fetcher is like a cronjob that does the following:

* Fetch fresh files form bank's systems and stores them in Incoming bucket
* Update status in [File Incoming](g2p-payments-bridge.md#3.-file-incoming) table in the DB as NEW.

Features:

* The implementation may be done via script called periodically.
* The file dispatch mechanism will be specific to a bank. The script should be designed such that several fetch mechanisms can be configured without having to make major changes in the code

## Payment File Reader

This block will be like a cronjob that runs periodically and does the following

* Read an unprocessed file from File Store -> Incoming bucket. The list of unprocessed files is obtained by reading the [File Incoming](g2p-payments-bridge.md#3.-file-incoming) table.
* Parse the file to read the status of each transaction. Translate the status to a common standard code if required.
* Update the status in DB as PAID or FAILED.
* Update error code and error messages
* Update the status in the [File Incoming ](g2p-payments-bridge.md#3.-file-incoming)table as PROCESSED.

This functional block may be implemented as a script that is run as cronjob. The features will be implemented:

* Full in-memory processing
* Entire processing and updates in DB should happen atomically. In case there is a failure, the script should be able to discard the incomplete process and start all over again.
* Configuration for bucket ID, location, and credentials for accessing [File Store](g2p-payments-bridge.md#file-store).

## Status codes

Mapping of status codes returned by the bank and as expected by upstream G2P systems need to be worked out.  At this point of time, the following codes are defined by G2P Connect:

```
rjct.reference_id.invalid
rjct.reference_id.duplicate 
rjct.timestamp.invalid
rjct.payer_fa.invalid
rjct.payee_fa.invalid
rjct.amount.invalid
rjct.schedule_ts.invalid 
rjct.currency_code.invalid 
```

## Performance and capacity

G2P payments are typically not real-time and can happen over several hours or even days. Assuming that SSD disks are used for DB and file storage, and all processing happens in-memory it should be possible to read a batch of 10, 000 to 100,000 from DB, process it, and write into a file in a few seconds (_hypothesis needs to be tested)._ Thus_,_ several million transactions processing should be possible in a day. A barebone calculation: if we assume 10,000 records can be read from DB, processed and written in a file in 10 seconds, then 3.6 million records can be processed in 1 hour.

The response time of ID Account Mapper also needs to be considered. The query to ID Account Mapper should be in Sync mode to keep the design simple.

The Payment File Creator, Payment File Reader, File Dispatcher, and File Fetcher must be designed such that they can run on independent CPUs.

The DB must be suitably indexed for fast reads and updates.

With this capacity, a single instance of each of the above would suffice. There may not be a need to have multiple instances of these blocks running in parallel as it will significantly increase the complexity of the design.


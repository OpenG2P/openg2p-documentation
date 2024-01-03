# G2P Cash Transfer Bridge

## Concept

The G2P Cash Transfer Bridge (GPB) fits in the payment chain as shown below.

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/gpb-payment-chain.png" alt=""><figcaption></figcaption></figure>

The module is envisaged to exist as an independent module in bridging the gap between a G2P system and a bank to initiate large-scale G2P cash transfers. Being specific to G2P transfers, (and not P2G, P2P, P2M etc), the module promises to be low cost, simple in design, easy to install and highly performant as real-time fast transfers are not a requirement in most social benefit transfer scenarios. However, the volume of transfers is expected to be large.

The module will support the following functionalities at a high level

1. Upstream interface layer compliant with G2P Connect or any other standard
2. Downstream interface layer to connect to bank with specific/proprietary interfaces
3. Query ID Account Mapper to fetch individual bank account information (optional)
4. History of past transactions
5. Reporting

## Architecture

<figure><img src="../../../.gitbook/assets/gpb-architecture.png" alt=""><figcaption></figcaption></figure>

## Design

### Disbursement API Controller

This functional block receives cash transfer requests from upstream systems like OpenG2P via the G2P Connect Disbursement APIs. The block parses the incoming request and writes in the DB. The Disbursement API is assumed to be Synchronous such that after DB write, 200 OK is returned to the caller. The disbursement request is expected to be split into batches by the upstream system depending on the system's optimum performance in terms of CPU and Memory.

When a Status API is called by the upstream system, this block reads the data from DB and returns the status of requested transactions. The output may need to be 'paginated' depending on the volume of data returned.

### Requests DB

All the requests are persisted in a DB like Postgres along with the status of each transfer request. The DB has the following tables:

#### 1. Payment Instructions

<table><thead><tr><th width="217">Column</th><th>Description</th></tr></thead><tbody><tr><td>batch_id</td><td>ID of the requested batch</td></tr><tr><td>request_id</td><td>ID of the request (this may be assigned by the Disbursement Controller in case not available in the Disbursement request)</td></tr><tr><td>request_timestamp</td><td></td></tr><tr><td>from_fa</td><td>Finanal Address of the sender. If there is only one sender, then this may be not be populated here, but configured in the system</td></tr><tr><td>to_fa</td><td>This may be an ID or contain account details (TBD)</td></tr><tr><td>amount</td><td></td></tr><tr><td>currency</td><td></td></tr><tr><td>status</td><td>Status of the request. This will be updated by multiple entities. The status enumeration may be NEW, FILED, PAID/FAILED</td></tr><tr><td>file</td><td>The file name in which the instruction has been written</td></tr><tr><td>error_code</td><td>Any error code if the status is FAILED. This will be used by the upsteam system to take necessary action like retry or giveup.</td></tr><tr><td>error_msg</td><td>Text error message</td></tr></tbody></table>

The table is expected to contain millions of records and a history of past transactions. Indexing of columns will be critical for performance. Besides, the previous records may be 'archived'. This could be achieved via horizontal partitioning. The management of DB in this regard needs to be worked out during implementation.

### Payment Backends. (Describe what is payment backend and what it does)

* What are the available payment backends right now:
  * Simple Mpesa Payment Backend
  * Mojaloop Payment Backend
  * [File-based Payment Backend](../g2p-payments-bridge.md)

## Installation Guide

### Installation on Kubernetes

* Refer to Deployment guide for deployment instructions.
  * Pre Installation Configuration
  * Installation Steps
  * Post Installation

### Installation Locally

* TBD

## Usage Guide

* Call Disburse api. Note down Txn id
* Call Disburse Status API with Txn id

## Detailed Description

* Each Concept from the above Concepts Sections, if it has any technical concepts defined here.
* ID Translation Service:
  * It can talk to G2P Connect ID Account Mapper.
* Multiplexer:
  * has some n things. TBD.
* Backend:
  * TBD

## API Docs

### REST API

Use Stoplight Integration for API docs.

### Status codes

Mapping of status codes returned by the bank and as expected by upstream G2P systems need to be worked out. At this point of time, the following codes are defined by G2P Connect:

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

## Available Payment Backends

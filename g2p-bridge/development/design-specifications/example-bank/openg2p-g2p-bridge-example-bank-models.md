---
description: openg2p-g2p-bridge-example-bank-models
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# example-bank-models

This is a library project - that contains all the sqlalchemy models and pydantic schemas - that are required to provide the required features of a Sponsor Bank.

## Persistent Objects - Design

### **account**

<mark style="color:blue;">Table used - to maintain accounts for benefit programs. This table will also maintain the book balance, available balance and funds blocked for these program accounts.</mark>

| Attribute             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| account\_number       | <p><strong>Unique Index - will hold the Account that funds the benefit program</strong><br>In the Sponsor Bank, this is the account number that will be debited for every disbursement<br><br>The corresponding credit will be either to the beneficiary_account (if the beneficiary account is serviced by the sponsor bank itself)<br><br>OR<br><br>The corresponding credit will be to the clearing account Nostro (mirror of the sponsor bank's account with the clearing house)</p> |
| account\_holder\_name | Should identify the Benefit Program that uses this account                                                                                                                                                                                                                                                                                                                                                                                                                               |
| account\_currency     | The currency in which funds are held in the account                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| book\_balance         | This is the ledger balance in the account                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| available\_balance    | <p>This is the available balance (funds available for use for disbursements)<br>available_balance = book_balance - blocked_amount</p>                                                                                                                                                                                                                                                                                                                                                    |
| blocked\_amount       | <p>This is the total amount that has been reserved (earmarked) by the program for specific purposes.<br><br>The G2P Bridge - blocks the entire envelope amount - for every disbursement_envelope.<br><br>The sponsor bank - creates an Amount Block for every block request. These amount blocks are available in the table - fund_blocks. The sum total of all records in fund_blocks equals this blocked_amount</p>                                                                    |

### **fund\_blocks**

<mark style="color:blue;">Table used - to maintain funds blocks for program accounts. Every successful funds block request will be identified by a "block\_reference\_no"  and will have exactly one record in this table.</mark>

| Attribute            | Description                                                                                                                                                                                                                                                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| block\_reference\_no | **Unique Index - for every block transaction.** Every request for an amount block - generates this unique Id.                                                                                                                                                                                                                                                             |
| account\_number      | The account funding the benefit program                                                                                                                                                                                                                                                                                                                                   |
| currency             | The currency in which the account operates                                                                                                                                                                                                                                                                                                                                |
| amount               | <p>The amount that has been blocked under this block_reference_no.<br><br>The g2p-bridge subsystem requests an amount block for the total envelope amount. <br><br>This amount reflects that total envelope amount in this scenario</p>                                                                                                                                   |
| amount\_released     | <p>The amount released - (partial) against this amount_block<br><br>In the g2p-bridge scenario, every disbursement diminishes (releases) the amount block partially<br><br>Once all the disbursements are effected, the amount released will equal to the amount blocked. When this happens, the column - blocked_amount in the account table - will become zero.<br></p> |

### initiate\_payment\_batch\_requests

<mark style="color:blue;">When the g2p-bridge initiates a payment request for a bunch of disbursements, all the disbursements in a single request are treated as a single batch. A batch\_id is allocated to this group of disbursements. A batch\_id will have a single record in this table. Further downstream processing in terms of generating book keeping entries will be processed together for a batch\_id.</mark>

| Attribute                 | Description                                                                                                                                                                                                                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| batch\_id                 | <p><strong>Unique Index.</strong><br>The G2P Bridge will initiate payments in batches. <br>Each API invocation (initiate_payment) will result in a creation of a <strong>unique batch_id</strong>.<br>All individual disbursements (payments)  in that request will be grouped under this batch_id.</p> |
| accounting\_log\_attempts | <p>The actual payment itself (generating book keeping entries) is handled asynchronously. A celery beat picks up all PENDING batches and delegates the batch_id to a task.<br>This attribute - keeps a count of these attempts.</p>                                                                     |
| accounting\_status        | <p>PENDING, PROCESSED<br>A celery beat picks all PENDING records and delegates the batch_id to a celery worker.<br>The worker picks up the individual payment records for this batch_id and effects book keeping entries for the "remitting_account"</p>                                                |

### initiate\_payment\_requests

| Attribute                             | Description                                                                                                                                                                                                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| batch\_id                             | <p><strong>Index. Not unique.</strong><br>A single batch_id will have many disbursements. Disbursements initiated from g2p-bridge in a single API invocation will be grouped together under a single batch_id.</p>                                                       |
| payment\_reference\_number            | <p><strong>Unique Index</strong></p><p>Every disbursement is treated as an individual payment request. <br>Every payment request is uniquely identified by a payment_reference_number <br>The g2p-bridge populates "disbursement_id" as the payment_reference_number</p> |
| remitting\_account                    | <p>This is the account that is debited for this payment request.<br>In the g2p-bridge scenario, this account will be the program's funding account.</p>                                                                                                                  |
| remitting\_account\_currency          | This is the currency in which the remitting\_account operates. This will typically be the local currency of the nation, in which this benefit program runs.                                                                                                              |
| payment\_amount                       | The payment amount, the amount that will be transferred to the beneficiary's account. In the g2p-bridge scenario, this amount will be the disbursement amount.                                                                                                           |
| payment\_date                         |                                                                                                                                                                                                                                                                          |
| funds\_blocked\_reference\_number     |                                                                                                                                                                                                                                                                          |
| beneficiary\_name                     |                                                                                                                                                                                                                                                                          |
| beneficiary\_account                  |                                                                                                                                                                                                                                                                          |
| beneficiary\_account\_currency        |                                                                                                                                                                                                                                                                          |
| beneficiary\_account\_type            |                                                                                                                                                                                                                                                                          |
| beneficiary\_bank\_code               |                                                                                                                                                                                                                                                                          |
| beneficiary\_branch\_code             |                                                                                                                                                                                                                                                                          |
| beneficiary\_mobile\_wallet\_provider |                                                                                                                                                                                                                                                                          |
| beneficiary\_phone\_no                |                                                                                                                                                                                                                                                                          |
| beneficiary\_email                    |                                                                                                                                                                                                                                                                          |
| beneficiary\_email\_wallet\_provider  |                                                                                                                                                                                                                                                                          |
| narrative\_1                          |                                                                                                                                                                                                                                                                          |
| narrative\_2                          |                                                                                                                                                                                                                                                                          |
| narrative\_3                          |                                                                                                                                                                                                                                                                          |
| narrative\_4                          |                                                                                                                                                                                                                                                                          |
| narrative\_5                          |                                                                                                                                                                                                                                                                          |
| narrative\_6                          |                                                                                                                                                                                                                                                                          |

### accounting\_logs

| Attribute                           | Description |
| ----------------------------------- | ----------- |
| reference\_no                       |             |
| corresponding\_block\_reference\_no |             |
| customer\_reference\_no             |             |
| debit\_credit                       |             |
| account\_number                     |             |
| transaction\_amount                 |             |
| transaction\_date                   |             |
| transaction\_currency               |             |
| transaction\_code                   |             |
| narrative\_1                        |             |
| narrative\_2                        |             |
| narrative\_3                        |             |
| narrative\_4                        |             |
| narrative\_5                        |             |
| narrative\_6                        |             |

### account\_statements

| Attribute                | Description |
| ------------------------ | ----------- |
| id                       |             |
| account\_number          |             |
| account\_statement\_lob  |             |
| account\_statement\_date |             |


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
| accounting\_status        | <p><strong>PENDING, PROCESSED</strong><br>A celery beat picks all PENDING records and delegates the batch_id to a celery worker.<br>The worker picks up the individual payment records for this batch_id and effects book keeping entries for the "remitting_account"</p>                               |

### initiate\_payment\_requests

<mark style="color:blue;">The payment requests initiated from g2p-bridge are stored in this table. A Celery beat producer later picks up all PENDING batch\_ids from the "initiate\_payment\_batch\_requests" table and delegates the actual book keeping task to a Celery worker.</mark>&#x20;

<mark style="color:blue;">This worker then translates all the payment\_requests for that batch\_id into book\_keeping entries in accounting\_log. Since this is only a simulator, only the Debit entries (debiting the program account) are generated.</mark>

<table><thead><tr><th width="375">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>batch_id</td><td><strong>Index. Not unique.</strong><br>A single batch_id will have many disbursements. Disbursements initiated from g2p-bridge in a single API invocation will be grouped together under a single batch_id.</td></tr><tr><td>payment_reference_number</td><td><p><strong>Unique Index</strong></p><p>Every disbursement is treated as an individual payment request. <br>Every payment request is uniquely identified by a payment_reference_number <br>The g2p-bridge populates "disbursement_id" as the payment_reference_number</p></td></tr><tr><td>remitting_account</td><td>This is the account that is debited for this payment request.<br>In the g2p-bridge scenario, this account will be the program's funding account.</td></tr><tr><td>remitting_account_currency</td><td>This is the currency in which the remitting_account operates. This will typically be the local currency of the nation, in which this benefit program runs.</td></tr><tr><td>payment_amount</td><td>The payment amount, the amount that will be transferred to the beneficiary's account. In the g2p-bridge scenario, this amount will be the disbursement amount.</td></tr><tr><td>payment_date</td><td>The date on which the payment needs to be effected. <br>g2p-bridge will send this date as the disbursement_date.</td></tr><tr><td>funds_blocked_reference_number</td><td>This is the block_reference_number, under which the funds have been earmarked for the disbursement_envelope.<br>For every payment actually effected, the funds blocked will be progressively released to eventually bring the blocked_amount to 0.</td></tr><tr><td>beneficiary_name</td><td></td></tr><tr><td>beneficiary_account</td><td></td></tr><tr><td>beneficiary_account_currency</td><td></td></tr><tr><td>beneficiary_account_type</td><td></td></tr><tr><td>beneficiary_bank_code</td><td></td></tr><tr><td>beneficiary_branch_code</td><td></td></tr><tr><td>beneficiary_mobile_wallet_provider</td><td></td></tr><tr><td>beneficiary_phone_no</td><td></td></tr><tr><td>beneficiary_email</td><td></td></tr><tr><td>beneficiary_email_wallet_provider</td><td></td></tr><tr><td>narrative_1</td><td>There is a provision for 6 lines of narrative that can accompany a payment transaction. <br><br>It's upto the implementation to populate these 6 lines with useful information so that g2p-bridge can reconcile the payments against the individual disbursements.<br><br>The "disbursement_id" is the unique reference that is populated as "payment_reference_no". <br><br>Apart from that - the g2p-bridge can use the following attributes to populate the narrative lines.<br>benefit_program_mnemonic<br>cycle_code_mnemonic</td></tr><tr><td>narrative_2</td><td></td></tr><tr><td>narrative_3</td><td></td></tr><tr><td>narrative_4</td><td></td></tr><tr><td>narrative_5</td><td></td></tr><tr><td>narrative_6</td><td></td></tr></tbody></table>

### accounting\_logs

<mark style="color:blue;">Book keeping entries for the Debit leg. These are generated by the Celery worker - process\_payments\_worker</mark>

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

<mark style="color:blue;">Table used to store the requests coming in for generating account statements. There is a REST API to facilitate requests for generating account statements. The REST API persists the requests in this table with a unique ID.</mark> \ <mark style="color:blue;">The API does not immediately generate the statement. It instead delegates this "ID" to a Celery worker - account\_statement\_generator.</mark>

<mark style="color:blue;">The account\_statement\_generator worker generates the MT940 statement and persists the statement as TEXT in the account\_statement\_lob column.</mark>

| Attribute                | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| id                       | Unique ID generated for every statement request                                                                                            |
| account\_number          | The benefit program account number - for which the request is being placed                                                                 |
| account\_statement\_lob  | <p>The actual account statement - TEXT - in MT940 format. <br>Asynchronously generated by Celery worker - account_statement_generator.</p> |
| account\_statement\_date | The date for which the MT940 needs to be generated.                                                                                        |


---
description: Sponsor Bank Simulator
---

# Example Bank

The G2P Bridge subsystem baseline - includes a separate repository - openg2p-g2p-bridge-example-bank.

This repository provides a Bank simulator - that provides implementation of APIs that should be provided by the Sponsor bank.

This Example Bank should not be deployed in production. The functionality provided by this Example Bank - should be provided by the Sponsor Bank (where the bank account that funds the benefit program is serviced)

The Example Bank repository has 3 projects

openg2p-g2p-bridge-example-bank-api

This a FastAPI based microservice and provides the following REST APIs

1. check\_funds
2. block\_funds
3. initiate\_payment
4. generate\_account\_statement

The first 3 APIs, viz. check\_funds, block\_funds and initiate\_payment - will be invoked by the g2p-bridge subsystem, through the example\_bank\_connector (BankInterface).

Persistent Objects - Design

**account**

| Attribute             | Deesreption                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| account\_number       | <p>Primary Key - will hold the Account that funds the benefit program<br>In the Sponsor Bank, this is the account number that will be debited for every disbursement<br><br>The corresponding credit will be either to the beneficiary_account (if the beneficiary account is serviced by the sponsor bank itself)<br><br>OR<br><br>The corresponding credit will be to the clearing account Nostro (mirror of the sponsor bank's account with the clearing house)</p> |
| account\_holder\_name | Should identify the Benefit Program that uses this account                                                                                                                                                                                                                                                                                                                                                                                                             |
| account\_currency     | The currency in which funds are held in the account                                                                                                                                                                                                                                                                                                                                                                                                                    |
| book\_balance         | This is the ledger balance in the account                                                                                                                                                                                                                                                                                                                                                                                                                              |
| available\_balance    | <p>This is the available balance (funds available for use for disbursements)<br>available_balance = book_balance - blocked_amount</p>                                                                                                                                                                                                                                                                                                                                  |
| blocked\_amount       | <p>This is the total amount that has been reserved (earmarked) by the program for specific purposes.<br><br>The G2P Bridge - blocks the entire envelope amount - for every disbursement_envelope.<br><br>The sponsor bank - creates an Amount Block for every block request. These amount blocks are available in the table - fund_blocks. The sum total of all records in fund_blocks equals this blocked_amount</p>                                                  |

**fund\_blocks**

| Attribute            | Description                                                                                                                                                                                                                                                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| block\_reference\_no | Unique Id - for every block transaction. Every request for an amount block - generates this unique Id.                                                                                                                                                                                                                                                                    |
| account\_number      | The account funding the benefit program                                                                                                                                                                                                                                                                                                                                   |
| currency             | The currency in which the account operates                                                                                                                                                                                                                                                                                                                                |
| amount               | <p>The amount that has been blocked under this block_reference_no.<br><br>The g2p-bridge subsystem requests an amount block for the total envelope amount. <br><br>This amount reflects that total envelope amount in this scenario</p>                                                                                                                                   |
| amount\_released     | <p>The amount released - (partial) against this amount_block<br><br>In the g2p-bridge scenario, every disbursement diminishes (releases) the amount block partially<br><br>Once all the disbursements are effected, the amount released will equal to the amount blocked. When this happens, the column - blocked_amount in the account table - will become zero.<br></p> |







openg2p-g2p-bridge-example-bank-celery

openg2p-g2p-bridge-example-bank-models

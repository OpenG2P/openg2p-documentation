---
description: >-
  This guide provides details on implementing the BankConnectorInterface for
  integration with sponsor banks to support various benefit programs in the G2P
  Bridge application.
---

# Bank Connector Interface Guide

#### Overview

The `BankConnectorInterface` is designed to provide a unified approach for interacting with different sponsor banks. Custom implementations of this interface allow partners to integrate specific banking APIs without modifying the core G2P Bridge application. An example implementation, `openg2p-g2p-bridge-example-bank-connector`, connects to a simulated bank for testing purposes.

* **Interface Code**: [BankConnectorInterface on GitHub](https://github.com/OpenG2P/openg2p-g2p-bridge/blob/develop/openg2p-g2p-bridge-bank-connectors/src/openg2p\_g2p\_bridge\_bank\_connectors/bank\_interface/bank\_connector\_interface.py)
* **Example Implementation**: [Example Bank Connector Repository](https://github.com/OpenG2P/openg2p-g2p-bridge/blob/develop/openg2p-g2p-bridge-bank-connectors/src/openg2p\_g2p\_bridge\_bank\_connectors/bank\_connectors/example\_bank\_connector.py)

***

#### Key Components of BankConnectorInterface

The `BankConnectorInterface` requires the following methods:

1. **`check_funds`**
   * **Purpose**: Verifies whether sufficient funds are available in a specific account.
   * **Arguments**:
     * `account_number` (str): The bank account number to check.
     * `currency` (str): Currency type of the account.
     * `amount` (float): Amount to verify for availability.
   * **Returns**: An instance of `CheckFundsResponse`:
     * `status` (FundsAvailableWithBankEnum): Indicates if funds are available (`FUNDS_AVAILABLE`) or not (`FUNDS_NOT_AVAILABLE`).
     * `error_code` (str): Error code if the check fails.
2. **`block_funds`**
   * **Purpose**: Blocks a specified amount in the account for a disbursement cycle.
   * **Arguments**:
     * `account_number` (str): The bank account to block funds in.
     * `currency` (str): Currency of the account.
     * `amount` (float): Amount to block.
   * **Returns**: An instance of `BlockFundsResponse`:
     * `status` (FundsBlockedWithBankEnum): Block status, either `SUCCESS` or `FAILURE`.
     * `block_reference_no` (str): Reference number of the block if successful.
     * `error_code` (str): Error code if blocking fails.
3. **`initiate_payment`**
   * **Purpose**: Sends payment instructions to the bank. This API acknowledges the payment instruction, but the bank processes it asynchronously.
   * **Arguments**: A list of `DisbursementPaymentPayload`, where each payload includes:
     * `disbursement_id` (str): Unique identifier for the disbursement.
     * `remitting_account` (str): Sponsor bank account for the disbursement.
     * `payment_amount` (float): Amount to be paid.
     * `beneficiary_id` (str): Unique ID for the beneficiary.
     * Additional fields include `beneficiary_account`, `beneficiary_name`, and `disbursement_narrative`.
   * **Returns**: An instance of `PaymentResponse`:
     * `status` (PaymentStatus): Payment status, either `SUCCESS` or `ERROR`.
     * `error_code` (str): Error code if the payment fails.
4. **`retrieve_disbursement_id`**
   * **Purpose**: Extracts the disbursement ID from bank transaction records.
   * **Arguments**:
     * `bank_reference` (str): Reference from the bank statement.
     * `customer_reference` (str): Unique disbursement ID in G2P Bridge.
     * `narratives` (str): Transaction narratives from the bank statement.
   * **Returns**: `disbursement_id` (str): Extracted disbursement ID.
5. **`retrieve_beneficiary_name`**
   * **Purpose**: Extracts the beneficiary’s name from bank statement narratives.
   * **Arguments**:
     * `narratives` (str): Narrative fields in the bank statement.
   * **Returns**: `beneficiary_name` (str): Name of the beneficiary.
6. **`retrieve_reversal_reason`**
   * **Purpose**: Identifies the reason for reversal transactions in bank statements.
   * **Arguments**:
     * `narratives` (str): Narrative fields from the bank statement.
   * **Returns**: `reversal_reason` (str): Reason for reversal.

***

#### Data Models and Enums

To implement this interface, several data models and enums are used, imported from the G2P Bridge libraries.

* **`CheckFundsResponse`**: Defines the response structure for fund checks.
* **`BlockFundsResponse`**: Defines the response structure for fund blocking.
* **`DisbursementPaymentPayload`**: Represents the payload for payment initiation.
* **Enums**:
  * `FundsAvailableWithBankEnum`: Represents fund availability statuses.
  * `FundsBlockedWithBankEnum`: Represents fund blocking statuses.
  * `PaymentStatus`: Defines payment outcomes, either `SUCCESS` or `ERROR`.

***

#### Example Implementation Workflow

1. **Define a Custom Connector**: Implement the `BankConnectorInterface` with the sponsor bank’s API details. Use methods like `check_funds`, `block_funds`, and `initiate_payment` to communicate with the bank.
2. **Configure Bank Connector Factory**: Implement `get_bank_connector(sponsor_bank_code: str)` to return an instance of the custom bank connector based on `sponsor_bank_code`.
3. **Testing**: Use the [Example Bank Connector ](https://github.com/OpenG2P/openg2p-g2p-bridge/blob/develop/openg2p-g2p-bridge-bank-connectors/src/openg2p\_g2p\_bridge\_bank\_connectors/bank\_connectors/example\_bank\_connector.py)and the[ bank simulator](https://github.com/OpenG2P/openg2p-g2p-bridge-example-bank) for validating your implementation.


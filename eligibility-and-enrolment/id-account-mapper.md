# ID Account Mapper

## Introduction

ID Account Mapper (IAM) is an innovative approach for social benefit programs to transfer cash benefits, subsidies, scholarships, and pensions digitally to beneficiaries. IAM provides a minimalistic component that enables programs to direct payments to beneficiary accounts using just the beneficiary identity numbers from an existing ID system.

An IAM is a key/value lookup registry that maps beneficiary ID with beneficiary account address. The registry entries in IAM can be added, deleted (soft/hard), updated, resolved to an account address, and verified for status.

The beneficiary ID is normalised to represent functional or foundational ID. Similarly, the account address is normalised to represent a bank account number, mobile wallet address, voucher, prepaid card, or digital currency. The account address can also point to the financial institution holding the account.

### OpenG2P G2P Payments Bridge

Social benefit delivery programs can use OpenG2P G2P Payments Bridge to connect with ID Account Mapper as shown in the diagram below.

<figure><img src="../.gitbook/assets/id-account-mapper (2).png" alt=""><figcaption></figcaption></figure>

These are the steps of payment disbursement using the OpenG2P G2P Payments Bridge:

1. The G2P Payments Bridge creates a mapping list containing beneficiary IDs and corresponding entitlement amounts for a program.
2. G2P Payments Bridge connects with the Mojaloop Payment Switch and provides the treasury account details and mapping list.
3. Mojaloop Payment Switch retrieves the beneficiary account details from the ID Account Mapper using the beneficiary ID provided by G2P Payments Bridge.
4. Mojaloop Payment Switch transfers the entitlement amount from the treasury bank account to the beneficiary's choice of account, i.e. mobile wallet, bank account, and prepaid card.

#### Advantages of using G2P Payments Bridge

1. Only the beneficiary ID and entitlement amounts are required to process payments. Beneficiary account details are not stored in the OpenG2P registry thus preserving the privacy of the beneficiary
2. The beneficiary has a choice of payment mode - wallet, account, prepaid card, or voucher.
3. A program can initiate bulk payments without dealing with multiple payment service providers.
4. A program can run efficiently without recollecting beneficiary account information and re-configuring payment service providers in the OpenG2P platform.

### Demo video

{% embed url="https://www.loom.com/share/c7d6f607f614429d81156cd3bf0e954f?sid=6c1e036a-63cd-47da-9fe8-a7829dfcceeb" %}

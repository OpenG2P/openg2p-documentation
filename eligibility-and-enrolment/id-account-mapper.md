# ID Account Mapper

## Introduction

ID Account Mapper (IAM) is an innovative approach for social benefit programs to transfer cash benefits, subsidies, scholarships, and pensions digitally to beneficiaries. IAM provides a minimalistic component that enables programs to direct payments to beneficiary accounts using just the beneficiary identity numbers from an existing ID system.&#x20;

An IAM is a key/value lookup registry that maps beneficiary ID with beneficiary account address. The registry entries in IAM can be added, deleted (soft/hard), updated, resolved to an account address, and verified for status.&#x20;

The beneficiary ID is normalised to represent functional or foundational ID. Similarly, the account address is normalised to represent a bank account number, mobile wallet address, voucher, prepaid card, or digital currency. The account address can also point to the financial institution holding the account.

### IAM integration with OpenG2P

Social benefit delivery programs can use OpenG2P to integrate with ID Account Mapper as shown in the diagram below.

<figure><img src="../.gitbook/assets/id-account-mapper (2).png" alt=""><figcaption></figcaption></figure>

#### Advantages of using IAM

1. Beneficiary account details are not stored in the OpenG2P registry thus preserving the privacy of the beneficiary
2. The beneficiary has a choice of payment mode - wallet, account, prepaid card, or voucher.
3. A program can initiate bulk payments without dealing with multiple payment service providers.
4. A program can run efficiently without recollecting beneficiary account information and re-configuring payment service providers in the OpenG2P platform.


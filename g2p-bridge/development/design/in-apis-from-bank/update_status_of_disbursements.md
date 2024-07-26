---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# upload\_mt940

MT940 is a structured account statement. The sponsor bank will send this statement (for the benefit program funding account) everyday.&#x20;

The exact mechanics of how this statement will be delivered to the government department will vary across implementations, viz. FTP, SMTP, API invoked by the bank etc.

Depending on the physical delivery mechanism, the implementation can create an integration layer and use this API to upload the MT940 message.

| API Attributes |                                                                   |
| -------------- | ----------------------------------------------------------------- |
| Direction      | Inward                                                            |
| Invoked by     | Sponsor bank, Implementation Integration work                     |
| Mode           | Synchronous                                                       |
| Tables         | <p>benefit_program_account_statement<br>account_statement_lob</p> |

## Object design

### account\_statement

<table><thead><tr><th width="287">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>statement_id</strong></td><td><strong>Unique ID</strong></td></tr><tr><td>statement_date</td><td>Tag :60F: of MT940 - Header Section</td></tr><tr><td>account_number</td><td>Tag :25: of MT940 - Header Section</td></tr><tr><td>reference_number</td><td>Tag :20: of MT940 - Header Section</td></tr><tr><td>statement_number</td><td>Tag :28C: of MT940 - Header Section</td></tr><tr><td>sequence_number</td><td>Tag :28C: of MT940 - Header Section</td></tr><tr><td>opening_balance</td><td>Tag :60F: of MT940 - Header Section<br>Positive Number -- Stands for Credit Balance<br>Negative Number -- Stands for Debit Balance</td></tr><tr><td>opening_balance_date</td><td>Tag :60F: of MT940 - Header Section</td></tr><tr><td>closing_balance</td><td>Tag :62F: of MT940 - Trailer Section<br>Positive Number -- Stands for Credit Balance<br>Negative Number -- Stands for Debit Balance</td></tr><tr><td>closing_balance_date</td><td>Tag :62F: of MT940 - Trailer Section</td></tr><tr><td>closing_available_balance</td><td>Tag :64: of MT940 - Trailer Section<br>Positive Number -- Stands for Credit Balance<br>Negative Number -- Stands for Debit Balance</td></tr><tr><td>closing_available_balance_date</td><td>Tag :64: of MT940 - Trailer Section</td></tr><tr><td>statement_upload_timestamp</td><td></td></tr><tr><td>statement_process_status</td><td>Enum<br>PENDING<br>PROCESSED</td></tr><tr><td>statement_process_timestamp</td><td></td></tr><tr><td>statement_process_error_code</td><td></td></tr><tr><td>statement_process_attempts</td><td></td></tr></tbody></table>

### account\_statement\_lob

| Attribute      | Description                                            |
| -------------- | ------------------------------------------------------ |
| statement\_id  |                                                        |
| statement\_lob | <p>TEXT type<br>Stores the MT940 Statement as TEXT</p> |

### Business logic

1. Persist the Account Statement in the two tables - account\_statement & account\_statement\_lob
2. In the table - account\_statement, only the following columns are populated - statement\_id, statement\_upload\_timestamp and statment\_process\_status = UNPROCESSED
3. In the table - account\_statement\_lob, the entire text is persisted with the statement\_id

### mt940\_processor\_beat\_producer

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>attempts</td><td>yes. subject to a configurable limit specified by  configuration yml</td></tr><tr><td><mark style="color:purple;">driving table</mark></td><td><mark style="color:purple;">account_statement</mark></td></tr><tr><td>eligible envelopes</td><td><mark style="color:blue;">statement_process_status = 'PENDING'</mark></td></tr></tbody></table>

1. Picks up all eligible account\_statement\_records
2. For each account statement, delegates a task to mt940\_processor\_worker
3. Payload -- statement\_id

### mt940 - statement format

<figure><img src="../../../../.gitbook/assets/MT940-Account-Statement-Format.png" alt=""><figcaption><p>MT940 - Account Statement - Detailed - Structure</p></figcaption></figure>

### mt940\_processor\_worker

1. Payload -- statement\_id
2. Picks up the record from account\_statement
3. Picks up the lob from account\_statement\_lob
4. Parse the mt940 - header and trailer and retrieve the following
   1.  sponsor bank account number - Tag :25: of MT940 - Header Section

       E.g. - <mark style="color:purple;">:25:032000136465</mark>
   2.  reference\_number - Tag :20: of MT940 - Header Section

       E.g. - <mark style="color:purple;">:20:CSCT032000136465</mark>
   3.  statement\_number - Tag :28C: of MT940 - Header Section

       E.g. - <mark style="color:purple;">:28C:00001/001</mark> (section before slash "/" is statement number)
   4.  sequence\_number - Tag :28C: of MT940 - Header Section

       E.g. - :28C:00001/001 (section after slash "/" is sequence number)
   5.  opening\_balance - Tag :60F: of MT940 - Header Section

       E.g. - <mark style="color:purple;">:60F:C171120AUD98838,27</mark>

       C or D -- stands for Credit Balance or Debit Balance

       171120 -- 6 characters - Statement Date in YYMMDD format

       AUD -- Australian Dollar - Currency of the Account

       98838,27 -- Ninety Eight Thousand Eight Hundred Thirty Eight AUD and Twenty Seven Cents - The comma is to be treated as decimal
   6.  closing\_balance - Tag :62F: of MT940 - Trailer Section

       Similar to Tag 60F
   7.  closing\_available\_balance - Tag :64: of MT940 - Trailer Section

       Similar to Tag 60F and 62F
5. Update these attributes in the table - account\_statement
6. Now loop through the transaction section of the MT940&#x20;
7. Each Transaction consists of two lines (tags) - :61: & :86: (Statement and Narrative)
8.  :61: is known as the Statement line and has the following structure

    <mark style="color:purple;">:61:1507020702D115945,00F014NARRATIVE//0207150143062089CRLF1234567890</mark>

    1. <mark style="color:purple;">150702 -- 6 digits -- Transaction Value Date in YYMMDD format</mark>
    2. <mark style="color:purple;">0702 -- 4 digits -- Transaction Booking Date in MMDD format</mark>
    3. <mark style="color:purple;">C/D -- 1 digit -- Credit or Debit indicator</mark>
    4. <mark style="color:purple;">115945,00 -- Transaction Amount -- Maximum 19 characters</mark>
    5. <mark style="color:purple;">F014 -- Transaction Code -- Should be a standard transaction code - 1 for Credit and another 1 for Debit</mark>
    6. <mark style="color:purple;">NARRATIVE -- Transaction Narrative -- Should be the Beneficiary Name -- This should be as sent by the g2p-bridge to the Sponsor Bank</mark>
    7. <mark style="color:purple;">// Reference Separator</mark>
    8. <mark style="color:purple;">0207150143062089CRLF1234567890 -- Transaction Reference Number issued by the Bank for this transaction</mark>
9. :86: is known as the Narrative Line - It can have 6 lines of 65 characters each. g2p-bridge should send as many details about the Benefit Program and Beneficiary in the Disbursement payload to ensure that the narrative text is as rich as possible
10. Create a List of Transactions for a Statement based on the Statement lines. The Statement Pydantic model should contain the following attributes
    1. Transaction Value Date
    2. Transaction Book Date
    3. Transaction Amount
    4. Debit-Credit Indicator
    5. Beneficiary Name -- NARRATIVE field (after the Reference Separator //)
    6. XX
11. Loop through the transactions. For each transaction
    1. Based on the Transaction Book Date -- go back 2 days (book date minus 2)
    2. This 2 (can be a configuration)
    3. get the benefit program based on the sponsor bank account number (benefit\_program\_configuration)
    4. for this benefit program, get a. list of all disbursements from Book Date minus 2
    5. the idea is that - based on an SLA -- the book date represents when the bank would have processed the disbursements after g2p-bridge dispatched them to the bank
    6. every disbursement should ideally have a corresponding Debit entry in the account statement
    7. match the transaction amount and the beneficiary details and the program details (how the narrative is formed has to be discussed)
    8. update the table - disbursement\_





### disbursement\_recon\_from\_bank

<table><thead><tr><th width="312">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>bank_disbursement_batch_id</td><td></td></tr><tr><td>disbursement_id</td><td>Unique Index</td></tr><tr><td>recon_statement_id</td><td>This is the Unique ID that is given to each MT940 that is uploaded into the platform</td></tr><tr><td>bank_statement_number</td><td>This is the Statement Number that is found in the MT940 header - field 28C</td></tr><tr><td>corresponding_entry_sequence</td><td>This is the sequence number of the entry in this statement - the entry that corresponds to this disbursement. This entry will be reflected as a "Debit" in the Program Account with the Sponsor Bank.</td></tr><tr><td>bank_reference_number</td><td>Bank's unique reference number for the transaction. Every disbursement will have a unique reference assigned by the bank.</td></tr><tr><td>reversal_found</td><td></td></tr><tr><td>reversal_statement_id</td><td></td></tr><tr><td>reversal_bank_statement_number</td><td></td></tr><tr><td>reversal_entry_sequence</td><td></td></tr><tr><td>reversal_reason</td><td></td></tr></tbody></table>

The sponsor bank invokes this API after it gets back the status of the disbursement from the destination bank through the national clearing / payment switch.

This API (as the name suggests) updates the status of the disbursment.

There are two possibilities - the disbursement either is successful or is a failure.

<mark style="color:blue;">**SUCCESS**</mark>

Update the following attributes in disbursement\_batch\_status

| Attribute                      | Datatype                                                                                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| reply\_status\_from\_bank      | <mark style="color:green;">**SUCCESS**</mark>                                                                                       |
| reply\_from\_bank\_time\_stamp | Time stamp of receipt of reply from Sponsor bank                                                                                    |
| reply\_success\_fsp\_code      | If the disbursement is a success, the fsp (the financial service provider / destination bank) code - where the account was credited |
| reply\_success\_fa             | The full Financial Address (including account number, branch code / mobile number) where the disbursement was credited              |

<mark style="color:blue;">**FAILURE**</mark>

Update the following attributes in disbursement\_batch\_status

| Attribute                      | Datatype                                                                                                                                                 |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| reply\_status\_from\_bank      | <mark style="color:red;">**FAILURE**</mark>                                                                                                              |
| reply\_from\_bank\_time\_stamp | Time stamp of receipt of reply from Sponsor bank                                                                                                         |
| reply\_failure\_error\_code    | Error code from the downstream G2P chain participants (Sponsor bank, Payment switch, Destination banks) in case of a FAILURE (reply\_status\_from\_bank) |
| reply\_failure\_error\_message | Error message describing the failure\_error\_code                                                                                                        |

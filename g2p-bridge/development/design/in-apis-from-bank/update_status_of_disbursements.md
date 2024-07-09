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

| API Attributes |                                               |
| -------------- | --------------------------------------------- |
| Direction      | Inward                                        |
| Invoked by     | Sponsor bank, Implementation Integration work |
| Mode           | Synchronous                                   |
| Tables         | benefit\_program\_account\_statement          |

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

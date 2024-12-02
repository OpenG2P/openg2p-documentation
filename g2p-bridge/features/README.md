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

# Features

The g2p-bridge subsystem offers the following functional features

## Incoming APIs from MIS/PBMS systems

1.  <mark style="color:orange;">**creation of disbursement envelope**</mark>

    A disbursement envelope is an object that represents the header level information for a single benefit program - for a single disbursement cycle.

    A benefit program will typically go through multiple disbursement cycles - some programs might have weekly disbursement cycles, some monthly, some quarterly and so on. Every disbursement cycle will potentially have 1000s of beneficiaries with their individual disbursement amounts.\
    The disbursement envelope is an object that summarizes a single disbursement cycle - in terms of number of beneficiaries,  the total disbursement amount, the program identification and the cycle identification.
2. <mark style="color:orange;">**status enquiry on a disbursement envelope**</mark>\
   The status enquiry will provide a snapshot of the current state of the envelope. It will provide the following details\
   **a.** program identification\
   **b.** cycle identification\
   **c.** number of beneficiaries\
   **d.** total disbursement amount in the envelope\
   **e.** number of disbursements received from the upstream PBMS/MIS system\
   **f.** number of disbursements shipped downstream to the Sponsor Bank\
   **g.** number of disbursements reconciled with the Sponsor Bank\
   **h.** number of disbursements reversed by the Sponsor Bank based on errors reported from further downstream destination banks&#x20;
3. <mark style="color:orange;">**cancel a disbursement envelope**</mark>\
   After an envelope is created in the g2p-bridge subsystem, the upstream pbms/mis system can cancel an envelope.\
   Once an envelope is cancelled, no further processing takes place in that envelope. \
   A cancellation cannot be undone.

## Outgoing APIs into Sponsor Bank

1. <mark style="color:purple;">**check available balance**</mark>\
   On the payment schedule date, if all the disbursements under an envelope have been received into the G2P-Bridge system, the G2P-Bridge will initiate the workflows related to downstream disbursement (payments) processing. The first step in this workflow is to ascertain availability of funds in the funding account (the account that is used to fund the disbursements. This account is the account that is serviced by the Sponsor Bank. The Sponsor Bank will debit this account for the proceeds of the disbursements).\
   Once the Sponsor Bank confirms availability of funds, the G2P-Bridge will mark this step as complete and initiate the next step.
2. <mark style="color:purple;">**block funds**</mark>\
   After receiving confirmation about availability of funds in the Program Funding Account, the G2P-Bridge initiates the 2nd step of Blocking Funds necessary for processing the Envelope. The G2P-Bridge sends a request to the Sponsor Bank to effect a hold on the account for the necessary amount. The G2P Bridge expects a SUCCESS response from the Bank along with a Block Transaction Reference Number. All further payments under this envelope will carry this Block Transaction Reference Number - so that the Sponsor Bank understands that funds have already been blocked for these payments.\
   Since payments are individually processed, the Sponsor Bank is expected to release the necessary funds (for that Block Reference Number) as it processes each individual payment.&#x20;
3. <mark style="color:purple;">**initiate payments**</mark>\
   This is the 3rd and final step in the Downstream processing of Disbursements. The G2P Bridge system will initiate payment requests in batches. This step has been designed on an Asynchronous paradigm, i.e. the G2P System does not expect a payment status response in terms of SUCCESS or FAILURE. The G2P System only expects an Acknowledgement SUCCESS from the Sponsor Bank. The Sponsor Bank in turn relays these payment messages into the country's payment network. Whether a particular payment was actually successful in crediting the intended beneficiary's account will be not known immediately because of the intermediary payment network. However, if the final credit in the destination bank is unsuccessful due to any reason, then the instruction will come back into the Sponsor Bank through the payment network and the Sponsor Bank will reverse the original transaction. This reversal will be visible in the Program Funding account as a reversal of Debit.

## Incoming APIs from Sponsor Bank&#x20;

1. <mark style="color:green;">**upload MT940 account statement**</mark>\
   The G2P Bridge system expects a daily account statement in MT940 format for all the program funding accounts. The G2P Bridge parses these MT940 statements and marks the status for each disbursement. The G2P Bridge updates the following status attributes for every disbursement\
   \
   **remittance\_reference\_number** - The Bank's reference number for the transaction (Debit Program Account)\
   **remittance\_statement\_id** - The Statement ID in which this Debit transaction is reflected\
   **remittance\_statement\_number** - The Statement Number (generated by the Bank) in which this Debit Transaction is reflected \
   **remittance\_statement\_sequence** - If the MT940 statement for a day has many sequences (due to high number of transaction), then the sequence in which the corresponding Debit transaction appears \
   **remittance\_entry\_sequence** - The sequence number of the corresponding debit transaction in that particular statement and sequence\
   **remittance\_entry\_date** - The booking date of the corresponding debit\
   **remittance\_value\_date** - The value date of the corresponding debit\
   \
   The following attributes are updated (analogous to the above remittance attributes, but applicable for a reversal transaction) if the G2P System detects a reversal transaction in addition to the original debit transaction. \
   \
   **reversal\_found** - TRUE indicates that a reversal corresponding to this disbursal has been found.\
   **reversal\_statement\_id** - The statement id in which the reversal transaction appears\
   **reversal\_statement\_number** - The statement number in which the reversal transaction appears\
   **reversal\_statement\_sequence** - The statement sequence in which the reversal transaction appears\
   **reversal\_entry\_sequence** - The entry sequence number within the statement where this reversal appears\
   **reversal\_entry\_date** - The booking date of this reversal\
   **reversal\_value\_date** - The value date of this reversal\
   **reversal\_reason** - The actual reason why this transaction failed at the Destination Bank (where the ultimate beneficiary is serviced. E.g. Account number incorrect


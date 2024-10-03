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

Incoming APIs from MIS/PBMS systems

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


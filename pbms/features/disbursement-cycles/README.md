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

# Disbursement

A program may have disbursements done in multiple cycles with different start and end dates for each cycle. Such cycles may be defined and triggered as per the schedule defined in each cycle. Each program should have at least one Cycle Manager associated with it.

## Program Manager

The Program Manager is a software module in the OpenG2P platform. It manages the number of cycles in a program and each request to create a cycle is executed through the Program Manager. The Program administrators can easily replicate cycles by selecting the option to copy from the previous cycle. The manager also has a configuration option to create a cycle-less program.&#x20;

## Cycle Manager

While the Program Manager manages all the cycles, each cycle is managed by a Cycle Manager. Cycle Manager provides many convenient single-click actions to enable Program administrators to quickly create new cycles, copy beneficiaries from the program, and prepare and approve entitlements.&#x20;

## Related user guides

:notebook\_with\_decorative\_cover:[Configure Program Manager in Program](../program-management/user-guides/configure-program-manager-in-program.md)

:notebook\_with\_decorative\_cover:[Create and Approve Program Cycle](../../functionality/disbursement-cycles/in-kind-transfer/user-guides/create-and-approve-disbursement-cycle.md)

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

# Config Attributes

The following configuration elements are visualized that influence business logic

g2p\_cash\_bridge

|                                                                |                                                                                                                            |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| <mark style="color:purple;">**g2p\_cash\_bridge**</mark>       |                                                                                                                            |
| <mark style="color:blue;">**inward\_apis\_from\_pbms**</mark>  |                                                                                                                            |
| max\_no\_of\_disbursements\_in\_a\_batch                       | 500                                                                                                                        |
| sla\_number\_of\_days                                          | <p>2<br>The number of days prior to the schedule date, that the system should receive all the disbursement information</p> |
| <mark style="color:blue;">**outward\_apis\_to\_banks**</mark>  |                                                                                                                            |
| max\_no\_of\_disbursements\_in\_a\_batch                       | 500                                                                                                                        |
| <mark style="color:blue;">**inward\_apis\_from\_banks**</mark> |                                                                                                                            |
| max\_no\_of\_disbursements\_in\_a\_batch                       | 500                                                                                                                        |

inward\_apis\_from\_banks.number\_of\_disbursements\_in\_a\_batch

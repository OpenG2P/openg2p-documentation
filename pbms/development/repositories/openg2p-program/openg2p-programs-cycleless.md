# OpenG2P Programs: Cycleless

### Module name

g2p\_program\_cycleless

### Module title

OpenG2P Programs: Cycleless

### Technology base

Odoo

### Functionality

* The proposed modal for this is, to have a flag configurable on the program manager configuration of each program, which marks whether a program is to be considered as a “Cycleless Program”.&#x20;
* Once that flag is set, some elements on the view/UI will change removing the elements of “Cycle” from the program.
* On the back-end one Cycle is created and attached to each program which is marked Cycleless. And further operations performed are considered to be under that cycle.

### Dependencies

Module Dependencies

* g2p\_programs

### Design notes

### User interface

Program ->  Configuration -> Program Manager

### Configuration

Enable "Is Cycleless" while configuring program manager makes respective program to “Cycleless Program”

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_cycleless](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_cycleless)

### Installation

Standard Odoo package installation

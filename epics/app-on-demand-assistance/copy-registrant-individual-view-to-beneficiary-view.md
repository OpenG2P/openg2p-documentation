# Copy registrant (individual) view to beneficiary view

## Introduction

All the view features of the registrant (individual) are copied to the beneficiary view. So, that Program managers can get all the details of individuals enrolled on that program in the beneficiary view itself.

## Getting Started

1. The beneficiary view uses the _g2p.program\_membership_ model and the registrant view uses the _res.partner_ model.
2.  So, to display all the fields in another view, make all related fields in the _g2p.program\_membership_ model which are not present in the _res.partner_ model.\
    \
    example:

    ```python
    registrant_id = fields.Integer(string="Registrant ID", related="partner_id.id")
    ```


3. Now all the fields are present in _g2p.program\_membership_ model.
4.  So, by using xpath expression in the XML file we can display all the fields of the registrant view to the beneficiary view.\
    \
    example:

    ```xml
    <xpath expr="//field[@name='enrollment_date']/.." position="before">
        <field name="registrant_id" />
    </xpath>
    ```


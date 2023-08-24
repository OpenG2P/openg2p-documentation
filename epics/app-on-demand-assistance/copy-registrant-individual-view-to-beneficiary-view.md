# Copy registrant (individual) view to beneficiary view

## Introduction

All the fields of the registrant (individual) are copied to the beneficiary view. In order to get all the details of individuals enrolled on that program in the beneficiary view itself.

In that case, Program Manager will be aware of all attributes associated with a beneficiary.

## Getting Started

1. The beneficiary view uses the _g2p.program\_membership_ model and the registrant view uses the _res.partner_ model.
2.  In order to display all the fields in another view, make all related fields in the _g2p.program\_membership_ model which are not present in the _res.partner_ model.\
    \
    example:

    ```python
    registrant_id = fields.Integer(string="Registrant ID", related="partner_id.id")
    ```


3. All the related fields that are created in _g2p.program\_membership_ model can be displayed in the view.
4.  In order to display these fields in the view, use xpath expression in the XML file to get the same view of the registrant in the beneficiary view.\
    \
    example:

    ```xml
    <xpath expr="//field[@name='enrollment_date']/.." position="before">
        <field name="registrant_id" />
    </xpath>
    ```


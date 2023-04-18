# 🛠 Proxy Means Test

## Introduction

It’s another eligibility criteria where the PMT score will be calculated based on the variables and their weights. The weights on these variables are then used to identify those who will be eligible to receive benefits using an eligibility cut-off line.

## How PMT Score is Calculated

PMT Score = ∑ f\*w

where,\
&#x20;           f = parameter field or variable\
&#x20;           w = weightage

## How to Configure PMT

When the form is submitted either by ODK or the beneficiaries portal, follow the below-mentioned steps:

1. Decide the form field or variable you want to use for PMT calculation.
2.  Create computed fields of the form in the Program Registrant Info model.\


    <figure><img src="../.gitbook/assets/Screenshot from 2023-04-03 15-34-42 (1) (1).png" alt=""><figcaption></figcaption></figure>


3.  After creating the computed fields, assign some weightage to the computed fields.\


    <figure><img src="../.gitbook/assets/Screenshot from 2023-04-03 15-25-01.png" alt=""><figcaption></figcaption></figure>


4. Based on the variable and weightage you will get a PMT Score that you can use in defining the eligibility.

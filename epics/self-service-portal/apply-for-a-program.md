# Apply for a Program

## Introduction

Registrants or individuals can apply for a program and avail themselves of the benefits of the selected program.

## How it works

1. When the user clicks on Apply button from the list of all programs:
   * the form mapped with the program will render.
   * program id is passed in the URL.
2. An application form will render which is created using the website module and collects the necessary information to apply to a program.
3.  After filing the form, when the user clicks on the submit action, the form\_submit\_action method is called, which checks whether all the required fields are correctly filled or not, If not then the toast message <mark style="color:red;">"Please update all mandatory fields"</mark> and the following error message will be shown below the input fields:

    *   not filled

        error-message: 'Please enter' + \<field\_name>
    * filled but incorrect



    | email | Please enter a valid email address    |
    | ----- | ------------------------------------- |
    | url   | Please enter a valid url              |
    | tel   | Please enter a valid telephone number |
4. When all the input checks are performed, finally the form data gets submitted along with the program id in the submitted URL.
5. In the submitted action controller, the form data will be saved in the `additional_g2p_info` field which is present in `res.partner` model in json format.
6. After saving the form data, Application ID is generated.

## How to generate Application ID

Logic- Submission date followed by 5 digit sequence number starting from 00001, e.g. 24012300001\
\
In `g2p.program_membership model` we added a new field `application_id`

```python
def _compute_application_id(self):
    for rec in self:
        d = datetime.today().strftime("%d")
        m = datetime.today().strftime("%m")
        y = datetime.today().strftime("%y")

        random_number = str(random.randint(1, 100000))

        rec.application_id = d + m + y + random_number.zfill(5)
```


# Smartscanner

**Smart Scanner** is a mobile app extension built on top of the [SmartScanner-Core](https://github.com/newlogic/smartscanner-core). It enhances traditional QR code scanning by supporting multiple versions of QR codes and parsing algorithms that vary across different countries.

### Key Features

* **CSV-Based QR Code Versioning**: The app can use a CSV input file to define the different versions of QR codes used in a country.
* **Direct Value Assignment**: QR code type information and configurations can be directly assigned in the ODK form’s data section.
* **Dynamic Parsing**: Smart Scanner identifies the type of QR code from the CSV or data input and applies the appropriate parsing logic.
* **Form Integration**: The scanning results are returned via an intent, providing all the data necessary to fill out a form.

### Supported QR Code Types

Smart Scanner currently supports three QR code types:

1. **CWT (CBOR Web Token)**:
   * The QR code data is encrypted, and the JSON payload is only accessible after verifying the digital signature using a public key.
2. **Plain JSON**:
   * The QR code contains a JSON payload, which is subject to signature verification after scanning. The verification ensures the data’s integrity by using specific fields from the QR code.
3. **Plain Text**:
   * The QR code directly contains a plain text string, which can be used without additional parsing or verification.

### Public Key Verification

* **CWT**: The verification process must succeed before receiving the JSON payload.
* **Plain JSON**: Verification is done after receiving the payload, ensuring the data hasn't been tampered with.

### Input Requirements

To use Smart Scanner, you need to pass an intent with a JSON array containing the following inputs:

1. **qr\_code\_type**:
   * Metadata defining the different QR code types and their versions.
   *   Example:

       ```json
       "[{'qrcode_index':0,'ver':'0', 'type':'json'}, {'qrcode_index':1,'ver':'PH1', 'type':'cwt'}, {'qrcode_index':2, 'type':'plain_text'}]"
       ```
2. **public\_keys** (for CWT and JSON types):
   * Public keys for each version of the QR code to verify its signature.
   *   Example:

       ```json
       "[{'qrcode_index':0,'public_key':'vD3czlgHEpf2sxGcri6iTm4zeEEA+jfd9tTq9S8zxe8='}, {'qrcode_index':1,'public_key':'MCowBQYDK2VwAyEAAF8LPSpgm1XFXR8pZtuT3c80Jxjmub3Q-17gV3sCftU'}]"
       ```
3. **field\_mapper**:
   * A mapping that defines how form fields correspond to fields in the scanned QR code.
   *   Example:

       ```json
       "[{'qrcode_index':0,'mapper':{'firstname':'subject.fName','lastname':'subject.lName','place_of_birth':'subject.POB'}}, {'qrcode_index':1,'mapper':{'firstname':'sb.fn','lastname':'sb.ln','place_of_birth':'sb.POB'}}, {'qrcode_index':2, 'mapper': {'text_field':'text'}}]"
       ```
4. **signature\_mapper** (for JSON types):
   * Fields used for signature verification in the JSON QR code. Includes the order of fields and how they should be prettified.
   *   Example:

       ```json
       "[{'qrcode_index':0,'mapper':['DateIssued','Issuer','subject','alg'],'pretty_spaces':2}, {'qrcode_index':1,'mapper':['sb','img']}]"
       ```

#### Default Behavior

* If no input is passed to the scanner, it returns an error.
* If only a public key is passed, the scanner defaults to CWT logic and attempts to decode all fields in the QR code.

Example for public key-only input:

```json
public_key = "MCowBQYDK2VwAyEAAF8LPSpgm1XFXR8pZtuT3c80Jxjmub3Q-17gV3sCftU"
```

#### Error Codes

When scanning fails, the following fields and codes are returned:

* **QRCODE\_SCAN\_status**: `true` (success) or `false` (failure).
* **QRCODE\_SCAN\_status\_message**: The reason for the failure.
* **QRCODE\_SCAN\_status\_code**: Error code explaining the failure.

| Error Code | Description                                     |
| ---------- | ----------------------------------------------- |
| 101        | QR Code Types Not Specified Correctly           |
| 102        | Public Key Not Specified Correctly              |
| 103        | Signature Mapper Not Specified Correctly        |
| 104        | Fields Not Specified Correctly in Scanner Input |
| 105        | QR Code Not Recognized                          |
| 106        | Failure But Reason Unknown                      |

### Configuration in ODK Forms

#### CSV Input for Scanner

A CSV file can be supplied and referenced in the ODK form. It should follow this format:

```css
key,value
qr_code_type,"[{'qrcode_index':0,'ver':'0', 'type':'json'}, {'qrcode_index':1,'ver':'PH1', 'type':'cwt'}, {'qrcode_index':2,'type':'plain_text'}]"
public_keys,"[{'qrcode_index':0,'public_key':'vD3czlgHEpf2sxGcri6iTm4zeEEA+jfd9tTq9S8zxe8='}, {'qrcode_index':1,'public_key':'MCowBQYDK2VwAyEAAF8LPSpgm1XFXR8pZtuT3c80Jxjmub3Q-17gV3sCftU'}]"
field_mapper,"[{'qrcode_index':0,'mapper':{'firstname':'subject.fName','lastname':'subject.lName','place_of_birth':'subject.POB'}}, {'qrcode_index':1,'mapper':{'firstname':'sb.fn','lastname':'sb.ln','place_of_birth':'sb.POB'}}, {'qrcode_index':2,'mapper':{'text_field':'text'}}]"
signature_mapper,"[{'qrcode_index':0,'mapper':['DateIssued','Issuer','subject','alg'],'pretty_spaces':2},{'qrcode_index':1,'mapper':['sb','img']}]"
```

#### Direct Assignment in ODK Form

Instead of using a CSV file, you can directly assign the values in the ODK form's data section:

```xml
<data id="field_mapper_testing">
    <qr_code_type> 
        [{'qrcode_index':0,'ver':'0', 'type':'json'}, {'qrcode_index':1,'ver':'PH1', 'type':'cwt'}, {'qrcode_index':2,'type':'plain_text'}]
    </qr_code_type>
    <public_keys> 
        [{'qrcode_index':0,'public_key':'vD3czlgHEpf2sxGcri6iTm4zeEEA+jfd9tTq9S8zxe8='}, {'qrcode_index':1,'public_key':'MCowBQYDK2VwAyEAAF8LPSpgm1XFXR8pZtuT3c80Jxjmub3Q-17gV3sCftU'}]
    </public_keys>
    <field_mapper>
        [{'qrcode_index':0,'mapper':{'firstname':'subject.fName','lastname':'subject.lName','place_of_birth':'subject.POB'}}, {'qrcode_index':1,'mapper':{'firstname':'sb.fn','lastname':'sb.ln','place_of_birth':'sb.POB'}}, {'qrcode_index':2,'mapper':{'text_field':'text'}}]
    </field_mapper>
    <signature_mapper>
        [{'qrcode_index':0,'mapper':['DateIssued','Issuer','subject','alg'],'pretty_spaces':2}, {'qrcode_index':1,'mapper':['sb','img']}]
    </signature_mapper>
</data>
```

#### ODK Form Integration

The ODK form should have variable names consistent with the field mapper in the CSV or data input. The form should include variables for the scanning status and the error codes.

Example structure:

```xml
<data id="field_mapper_testing">
    <public_keys />
    <field_mapper />
    <qr_code_type />
    <signature_mapper />
    <qrcodedata>
        <firstname />
        <lastname />
        <place_of_birth />
        <text_field />
        <QRCODE_SCAN_status />
        <QRCODE_SCAN_status_message />
        <QRCODE_SCAN_status_code />
    </qrcodedata>
</data>
```

An intent call in the form would look like this:

```xml
<group appearance="field-list" intent="org.idpass.smartscanner.odk.QRCODE_SCAN(public_keys=/data/public_keys, field_mapper=/data/field_mapper, qr_code_type=/data/qr_code_type, signature_mapper=/data/signature_mapper)" ref="/data/qrcodedata">
    <input ref="/data/qrcodedata/firstname">
        <label>First Name</label>
    </input>
    <input ref="/data/qrcodedata/lastname">
        <label>Last Name</label>
    </input>
    <input ref="/data/qrcodedata/place_of_birth">
        <label>Place Of Birth</label>
    </input>
</group>
```

### Download APK

{% embed url="https://drive.google.com/file/d/1NkIJkRY3goApFDJEMTRoWNQEGNTDhqIP/view?usp=sharing" %}

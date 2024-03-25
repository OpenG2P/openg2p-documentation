# VC Integration with IBR

## Functionality

Provide the following feature in OpenG2P PBMS:

A user who is a beneficiary of a program (or multiple programs) in IBR, can download his beneficiary card (BC) in the form of VC as

* VC in the Inji wallet
* QR code that can be printed on paper

Download method:

**Inji**:

* User logins in using ID via eSignet&#x20;
* User is shown "Download Beneficiary Card" option with a listing of all the programs he is enrolled into
* BC gets downloaded on to Inji wallet (how? is the eSignet login available from Inji itself)

**QR code:**

* User logs in via a desktop into eSignet portal&#x20;
* "Print your Beneficiary Card" option is displayed.&#x20;
* User gets a QR code along with text information in a card format on paper

## Approach

Use

&#x20;[https://github.com/mosip/esignet-mock-services/blob/master/mock-esignet-integratio\[…\]osip/esignet/mock/integration/service/MockVCIssuancePlugin.java](https://github.com/mosip/esignet-mock-services/blob/master/mock-esignet-integration-impl/src/main/java/io/mosip/esignet/mock/integration/service/MockVCIssuancePlugin.java#L110)\
[MockVCIssuancePlugin.java](https://github.com/mosip/esignet-mock-services/blob/master/mock-esignet-integration-impl/src/main/java/io/mosip/esignet/mock/integration/service/MockVCIssuancePlugin.java)\


```
        JWTSignatureResponseDto responseDto = signatureService.jwtSign(jwtSignatureRequestDto);
```

[mosip/esignet-mock-services](https://github.com/mosip/esignet-mock-services) \
This is a MockVC issuance plugin. It has all the code necessary to convert a JSON to VC and also it is a mock so we can take this skeleton and convert it with our DB.

Connect to  DB,  fetch the relevant details and convert to VC\
Assuming we are doing this with PSUT.  This plugin will use the PSUT and query  DB then use the `buildDummyJsonLDWithLDProof` to construct the VC.



For key manager it’s using library. We can change it to rest API will give that sample as well[09:50](https://mosip-team.slack.com/archives/DQ6TTEVMG/p1708057214756349)[https://github.com/mosip/id-repository/blob/f12b9851eb9ca6e2e5becd29d4be8b5a277b6075/id-repository/credential-service/src/main/java/io/mosip/credentialstore/provider/impl/VerCredProvider.java#L240C38-L240C49](https://github.com/mosip/id-repository/blob/f12b9851eb9ca6e2e5becd29d4be8b5a277b6075/id-repository/credential-service/src/main/java/io/mosip/credentialstore/provider/impl/VerCredProvider.java#L240C38-L240C49)[09:51](https://mosip-team.slack.com/archives/DQ6TTEVMG/p1708057271572289)[https://github.com/mosip/id-repository/blob/f12b9851eb9ca6e2e5becd29d4be8b5a277b6075/id-repository/credential-service/src/main/java/io/mosip/credentialstore/util/DigitalSignatureUtil.java#L144](https://github.com/mosip/id-repository/blob/f12b9851eb9ca6e2e5becd29d4be8b5a277b6075/id-repository/credential-service/src/main/java/io/mosip/credentialstore/util/DigitalSignatureUtil.java#L144)[DigitalSignatureUtil.java](https://github.com/mosip/id-repository/blob/f12b9851eb9ca6e2e5becd29d4be8b5a277b6075/id-repository/credential-service/src/main/java/io/mosip/credentialstore/util/DigitalSignatureUtil.java)

```
            String responseString = restUtil.postApi(ApiName.KEYMANAGER_VERCRED_SIGN, null, "", "",
```






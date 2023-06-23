# Deploy Smart-Scanner App

## Description&#x20;

The guide here provides steps to deploy the SmartScanner App. This App allows users to scan the QR code in the entitlement voucher.

## Pre-requisites

The user must possess an Android Phone with an Android OS version (?) or above and a Wireguard conf file. Please reach out to your system administrator to generate the Wireguard conf file.

## Steps

1. Download the SmartScanner APK file named _idpass-smart-scanner-untagged-\<version>.apk_ on Android mobile from this location: [https://drive.google.com/drive/folders/1FMQQtPcKeDnhM3vfR-\_EQHeEvzaPKhfq?usp=drive\_link](https://drive.google.com/drive/folders/1FMQQtPcKeDnhM3vfR-\_EQHeEvzaPKhfq?usp=drive\_link)

<figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption></figcaption></figure>

2. Go to the Downloads folder in Android Mobile and click on the .apk file that you downloaded in the first step. A user prompt will appear with the options _CANCEL_ and _INSTALL._ Click on _INSTALL_.

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

3. For first-time installation, a user prompt may appear to allow unknown apps. Click on _Settings._ If no prompt appears and application installs, then go to step#5.

<figure><img src="../../.gitbook/assets/image (6).png" alt=""><figcaption></figcaption></figure>

4. Enable the option _Allow apps from this source,_ click on the downloaded file, and install the application by clicking _Install_.

<figure><img src="../../.gitbook/assets/image (15).png" alt=""><figcaption></figcaption></figure>



5. If the SmartScanner app is successfully installed, then this icon will appear on the mobile screen.

<figure><img src="../../.gitbook/assets/image (17).png" alt=""><figcaption></figcaption></figure>

6. Search for "wire guard" in the Android Play Store.&#x20;

<figure><img src="../../.gitbook/assets/image (11).png" alt=""><figcaption></figcaption></figure>

7. Install the WireGuard app, open it, and click on the + icon to add the tunnel.

<figure><img src="../../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>

8. A list of options will appear from the bottom of the app. Click the _Import from file or archive_ option.&#x20;

<figure><img src="../../.gitbook/assets/image (1).png" alt=""><figcaption></figcaption></figure>

9. Select the WireGuard conf file provided by the system administrator. On successful tunnel creation, the tunnel name will appear at the top of the app.

<figure><img src="../../.gitbook/assets/image (10).png" alt=""><figcaption></figcaption></figure>

10. Activate the tunnel in WireGuard.

<figure><img src="../../.gitbook/assets/image (18).png" alt=""><figcaption></figcaption></figure>

11. Open the SmartScanner App. It should show the option _Voucher Code_.

<figure><img src="../../.gitbook/assets/image (8).png" alt=""><figcaption></figcaption></figure>

12. Click on the _Voucher Code_ and scan the QR code shown here.

<figure><img src="../../.gitbook/assets/image (7).png" alt=""><figcaption></figcaption></figure>

13. If the SmartScanner App is successfully deployed, then the scan will show these details.

<figure><img src="../../.gitbook/assets/image (16).png" alt=""><figcaption></figcaption></figure>


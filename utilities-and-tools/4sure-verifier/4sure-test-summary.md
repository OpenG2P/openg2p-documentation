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

# 4Sure Test Summary

This document summarises the test strategy, deliverables, and results recorded while testing the [4Sure](./) application.

## Test objective

The purpose of testing is to ensure the functionality of the features in the 4Sure application is in line with the requirements of the stakeholders.

## **Test scope**

The scope is to test the functionality of the features in the 4Sure application.

| Feature                         | Test Cases                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <p>Feature in scope </p><p></p> | [https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?jql=project%20%3D%20%22FS%22%20AND%20type%20%3D%20story%20AND%20status%20IN%20(%22To%20Do%22%2C%22In%20Progress%22)%20ORDER%20BY%20created%20DESC](https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?jql=project%20%3D%20%22FS%22%20AND%20type%20%3D%20story%20AND%20status%20IN%20\(%22To%20Do%22%2C%22In%20Progress%22\)%20ORDER%20BY%20created%20DESC) |
| Feature not in scope            | [https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?jql=project%20%3D%20%22FS%22%20AND%20type%20%3D%20story%20AND%20status%20IN%20(%22To%20Do%22%2C%22In%20Progress%22)%20ORDER%20BY%20created%20DESC](https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?jql=project%20%3D%20%22FS%22%20AND%20type%20%3D%20story%20AND%20status%20IN%20\(%22To%20Do%22%2C%22In%20Progress%22\)%20ORDER%20BY%20created%20DESC) |

## **Test environment**

### 4Sure standalone mode

The 4Sure application is tested in standalone mode by installing the application on Android devices.

<table><thead><tr><th width="294">Device Model</th><th width="347">OS Version</th><th width="116">Test Result</th></tr></thead><tbody><tr><td>Samsung Galaxy Tablet</td><td>Android V14</td><td>Pass</td></tr><tr><td>Moto G(60)</td><td>Android V12</td><td>Pass</td></tr><tr><td> Google pixel 6a</td><td>Android V13</td><td>Pass</td></tr></tbody></table>

### Launch 4Sure application via ODK collect

* The launching of 4Sure application via ODK collect is tested by installing the application on above mentioned Android devices, and&#x20;
* Used explore environment for ODK collect&#x20;

## Test type

The below test types are used to make sure that the application is tested properly.

| Test type  | Description                                                                           |
| ---------- | ------------------------------------------------------------------------------------- |
| Sanity     | It is used to ensure that the major functionality of the application is working fine. |
| Regression | It is used to ensure that the entire functionality    of the application works fine.  |

## Test execution summary

<table><thead><tr><th>Environment</th><th width="225">No. of test case executed</th><th width="98">Passed</th><th width="80">Failed</th><th>Not executed</th></tr></thead><tbody><tr><td>4Sure application Standalone mode</td><td>43</td><td>36</td><td>3</td><td>4</td></tr><tr><td>Launch 4Sure application via ODK Collect</td><td>40</td><td>34</td><td>2</td><td>4</td></tr><tr><td>Total</td><td>83</td><td>70</td><td>5</td><td>8</td></tr></tbody></table>

For detailed summary, click the below link.

{% embed url="https://docs.google.com/spreadsheets/d/1sx6n3-8_Rz1tHmKE8tyF8MjI_-0eIduX2YnIlz_5SaE/edit#gid=1525557454" %}

## **Defect summary**

You can find the defect summaries that are identified during testing in the below links.

| Defect summary                            | Link                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Total number of defects found             | [https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project%20%3D%20%22FS%22%20AND%20type%3D%20bug%20ORDER%20BY%20created%20DESC](https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project%20%3D%20%22FS%22%20AND%20type%3D%20bug%20ORDER%20BY%20created%20DESC)                                                         |
| Total number of defects in "To Do" states | [https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project+=+%22FS%22+AND+type=+bug+AND+status+IN+(%22To+Do%22,%22In+Progress%22)+ORDER+BY+created+DESC](https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project+=+%22FS%22+AND+type=+bug+AND+status+IN+\(%22To+Do%22,%22In+Progress%22\)+ORDER+BY+created+DESC)       |
| Total number of defects in "Done" states  | [https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project%20%3D%20%22FS%22%20AND%20type%3D%20bug%20AND%20status%20%3D%20Done%20ORDER%20BY%20created%20DESC](https://openg2p.atlassian.net/jira/software/c/projects/FS/issues/?filter=allissues\&jql=project%20%3D%20%22FS%22%20AND%20type%3D%20bug%20AND%20status%20%3D%20Done%20ORDER%20BY%20created%20DESC) |

## Release information

* APK link: [ https://drive.google.com/file/d/1GeQFXjSOC69iZx91rX0fu5HWstM3rS5B/view?usp=drive\_link](https://drive.google.com/file/d/1GeQFXjSOC69iZx91rX0fu5HWstM3rS5B/view?usp=drive\_link)
* Build Date: 2024-03-21
* Build name: 4Sure-debug-v0.7.0-21-03-2024-arm64-v8a.apk
* Deployment Target: Android 12 and above


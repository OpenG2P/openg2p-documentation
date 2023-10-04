# Configure Proxy Means Test

## Description

The guide provides steps to enable and configure the Proxy Means Test.

## Pre-requisites

The user must have a Program Manager role.

## Steps

1. Navigate to _Programs_ using the menu bar.

<figure><img src="../../.gitbook/assets/programs.png" alt=""><figcaption></figcaption></figure>

2. Click on the program name for which configuration to be done.

<figure><img src="../../.gitbook/assets/program-list-view-page.png" alt=""><figcaption></figcaption></figure>

3. Navigate to the _PMT_ _Configuration_ section on Program detailed view page.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 20-55-37.png" alt=""><figcaption></figcaption></figure>

4. Enable PMT and click on _Add a line_ in the _PMT Parameters_ field.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 20-50-30.png" alt=""><figcaption></figcaption></figure>

5. Select the field and provide its weightage.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-53-00.png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
The above-mentioned selection fields are computed fields and can be added in the settings.
{% endhint %}

6. Click on the _Save & New_ button to select a new field and provide its weightage or _Save & Close_ button which will save the fields and their weightage to that program under configuration.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 21-47-14.png" alt=""><figcaption></figcaption></figure>

7. Click on the _Save_ button.

## Steps to add computed fields

{% hint style="info" %}
Enable developer mode.

Settings --> Developer Tools --> 'Activate the developer mode'
{% endhint %}

1. Navigate to _Settings_ using the menu bar.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-11-10.png" alt=""><figcaption></figcaption></figure>

2. Click on _Technical_ in the setting menu.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-13-13 (1) (1).png" alt=""><figcaption></figcaption></figure>

3. Navigate to _Models_ under _Database Structure_ heading.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-18-38.png" alt=""><figcaption></figcaption></figure>

4. Search _Program Registrant Info_ model in the search bar.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-23-20.png" alt=""><figcaption></figcaption></figure>

5. Click on _g2p.program.registrant\_info_ model.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-26-46.png" alt=""><figcaption></figcaption></figure>

6. Click on _add a line_ in Fields section.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-41-00.png" alt=""><figcaption></figcaption></figure>

6. Add field name, type, label, dependencies field and compute logic.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-03 15-34-42.png" alt=""><figcaption></figcaption></figure>

8. Click on the _Save & New_ button to select a new computed field or _Save & Close_ button which will save the computed field in the model.

<figure><img src="../../.gitbook/assets/Screenshot from 2023-04-23 22-42-19.png" alt=""><figcaption></figcaption></figure>

9. Click on the _Save_ button.

{% hint style="info" %}
So, these computed fields will display in the selection field of PMT Configuration.
{% endhint %}

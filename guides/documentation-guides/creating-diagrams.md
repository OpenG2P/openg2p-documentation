# Creating Diagrams

## Context

Creating editable diagrams in open formats using open source tools is challenging. Here, we suggest [Draw.io](https://app.diagrams.net/) for creating diagrams and saving them directly in GitHub repository.

## Creating new diagram

* Fork `openg2p-documentation` repository to your local Github account.
* On [Draw.io](https://app.diagrams.net/) website choose Github as your storage.

<figure><img src="../../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

* Authorize the Draw.io app on Github (follow the steps prompted). Select `openg2p-documentation` and the branch you wish to add your diagram.
* Select the format of the diagram as `.svg`.

<figure><img src="../../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

* Select the repository, branch and `.gitbook/assets` folder to save the diagram.
* Create the diagram and save - it will get git committed to your repository.
* Send a Pull Request to `OpenG2P/openg2p-documentation` repo.
* On the Gitbook documentation page insert the image as a URL. The URL in this case will be the complete GitHub URL of the image in **raw** format. E.g. https://github.com/OpenG2P/openg2p-documentation/blob/1.0.0/.gitbook/assets/openg2p-logo.svg

{% hint style="warning" %}
The link above may need to be updated if you move the documentation to another branch of the repository.
{% endhint %}

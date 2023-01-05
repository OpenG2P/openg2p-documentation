# Creating Diagrams

## Context

Creating diagrams such that they are editable is challenging. Further, being an open source project we would like to use open source tools as much as possible.  Here, we suggest using [Draw.io](https://app.diagrams.net/) for creating diagrams and saving them directly in Github repository.

## Creating new diagram

* On [Draw.io](https://app.diagrams.net/) website open choose Github as your storage.

<figure><img src="../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

* Fork `openg2p-documentation` repository to your local Github account.
* Authorize Draw.io app on Github (follow the steps are prompted). Select `openg2p-documentation` and the branch you wish to add your diagram.
* Select format of diagram as `.svg`.

<figure><img src="../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

* Select repository, branch and `.gitbook/assests` folder to save the diagram.
* Create the diagram and save - it will get git committed to your repository.
* Send a Pull Request to `OpenG2P/openg2p-documentation` repo.
* On Gitbook documentation page insert the image as a URL. The URL in this case will be complete Github URL of the image in **raw** format. E.g. https://github.com/OpenG2P/openg2p-documentation/blob/1.0.0/.gitbook/assets/openg2p-logo.svg

{% hint style="warning" %}
CAUTION: The link above may need to be changed if you move the documentation to another branch of the repository.
{% endhint %}

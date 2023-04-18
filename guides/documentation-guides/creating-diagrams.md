# Creating Diagrams

## Context

Creating editable diagrams in open formats using open source tools is challenging. Here, we suggest [Draw.io](https://app.diagrams.net/) for creating diagrams and saving them directly in GitHub repository.

## Creating new diagram

* On [Draw.io](https://app.diagrams.net/) website choose _Device_ as your storage.

<figure><img src="../../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

* Select the format of the diagram as XML`.drawio.`&#x20;

<figure><img src="../../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

* Create the diagram and save it on your local machine. Make sure you follow the file naming convention of lowercase with hyphens as word separations.
* Login to Gitbook and upload the `.drawio` file using the file uploader. Make sure you select _All Files_ on the file explorer popup, otherwise, you may not see the `*.drawio` files.

<figure><img src="../../.gitbook/assets/file-uploader.png" alt=""><figcaption></figcaption></figure>

* After the file is uploaded a [Gitbook Action Workflow](https://github.com/OpenG2P/openg2p-documentation/blob/main/.github/workflows/drawio.yml) will get triggered to convert the same to PNG format with `*.png` extension. The PNG file will be available in the same folder as `.drawio` file. In this case, it will be the repository's `.gitbook/assets` folder.&#x20;
* Insert the image using the _URL_ options shown by Gitbook. The URL to be given will be the Github URL like [https://github.com/OpenG2P/openg2p-documentation/raw/1.0.0/.gitbook/assets/add-deduplication-manager.png](https://github.com/OpenG2P/openg2p-documentation/raw/1.0.0/.gitbook/assets/add-deduplication-manager.png). Make sure you pick this URL in **Raw** format which will available on the _Download_ button on Github

<figure><img src="../../.gitbook/assets/github-raw-image-link.png" alt=""><figcaption></figcaption></figure>

## Editing existing diagram

* Fork `openg2p-documentation` repository to your local Github account.
* On [Draw.io](https://app.diagrams.net/) website choose Github as your storage.

<figure><img src="../../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

* Authorize the Draw.io app on Github (follow the steps prompted).&#x20;
* Select the diagram in `.drawio` format from `openg2p-documentation` --> your branch --> `.gitbook/assests` folder.

<figure><img src="../../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

* Make changes.
* Save the diagram - it will get git committed to your repository.
* Send a Pull Request to `OpenG2P/openg2p-documentation` repo.

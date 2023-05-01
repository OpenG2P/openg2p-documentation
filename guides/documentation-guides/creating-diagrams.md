# Creating Diagrams

## Context

Creating editable diagrams in open formats using open source tools is challenging. Here, we suggest [Draw.io](https://app.diagrams.net/) for creating diagrams and saving them directly in GitHub repository.

## Creating new diagram

1. On [Draw.io](https://app.diagrams.net/) website choose _Device_ as your storage.

<figure><img src="../../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

2. Select the format of the diagram as XML`.drawio.`&#x20;

<figure><img src="../../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

3. Create the diagram and save it on your local machine. Make sure you follow the file naming convention of lowercase with hyphens as word separations.
4. On Github, upload/commit the `.drawio` file to the `openg2p-documentation` repository in the branch of choice to the following folder: `.gitbook/assets`.
5. After the file is uploaded/committed a [Gitbook Action Workflow](../../.github/workflows/drawio.yml) will get triggered to convert the same to PNG format with `*.png` extension. The PNG file will be available in the same folder as the `.drawio` file. In this case, it will be the repository's `.gitbook/assets` folder.&#x20;
6. On Gitbook, insert the PNG image using the _URL_ options shown by Gitbook. The URL to be given will be the GitHub URL like [https://github.com/OpenG2P/openg2p-documentation/raw/1.0.0/.gitbook/assets/add-deduplication-manager.png](https://github.com/OpenG2P/openg2p-documentation/raw/1.0.0/.gitbook/assets/add-deduplication-manager.png). Make sure you pick this URL in **Raw** format which will available on the _Download_ button on Github

<figure><img src="../../.gitbook/assets/github-raw-image-link.png" alt=""><figcaption></figcaption></figure>

## Editing existing diagram

If a `.drawio` already exists in the `.gitbook/assets` folder than you directly edit the repository version of the same by following the procedure given below.

1. Fork `openg2p-documentation` repository to your local Github account.
2. On [Draw.io](https://app.diagrams.net/) website choose Github as your storage.

<figure><img src="../../.gitbook/assets/draw-io-storage.png" alt=""><figcaption></figcaption></figure>

3. Authorize the Draw.io app on Github (follow the steps prompted).&#x20;
4. Select the diagram in `.drawio` format from `openg2p-documentation` --> your branch --> `.gitbook/assests` folder.

<figure><img src="../../.gitbook/assets/draw-io-file-format.png" alt=""><figcaption></figcaption></figure>

5. Make changes.
6. Save the diagram - it will get git committed to your repository.
7. Send a Pull Request to `OpenG2P/openg2p-documentation` repo.
8. Upon acceptance of Pull Request, a [Github Action Workflow](../../.github/workflows/drawio.yml) will trigger the conversion of the`.drawio` file to `.png`.&#x20;
9. If you have not added the URL to Gitbook follow step 6 of [Creating New Diagram](creating-diagrams.md#creating-new-diagram).
10. If URL already exists in Gitbook, the updated image should appear after a page refresh.

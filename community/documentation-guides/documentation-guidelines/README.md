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

# Documentation Guidelines

This guide provides basic guidelines for you to write neat documentation.

## General conventions

* Page title: Capitalize the first letter of every word. Like this page title
* Start a topic with Introduction/Concept/Context
* Use Gitbook's "Heading 1, Heading 2" etc for headings
* Headings must use lowercase except for the first letter. E.g. "Code of conduct"
* Provide reference links to the text as applicable
* Provide a link at the first mention of a new/different topic. For example, if the guide is talking about installing the SmartScanner app, and the WireGuard app is mentioned, then provide the link for WireGuard.
* Avoid using ":" in a heading.  E.g. "Design choices:"&#x20;
* Use clear and crisp images - the images should not appear blurred when seen on full screen.
* If you are adding image files, make sure all file names are lowercase with hyphens. E.g `architecture-diagram.png`.
* The filename for images should follow the naming convention of every word in lower case, and words separated by hyphens i.e. view-all-programs.png.
* For work-in-progress features/functions, you may mention the same under the title as shown below:

<div align="left">

<figure><img src="../../../.gitbook/assets/work-in-progress.png" alt="" width="309"><figcaption></figcaption></figure>

</div>

* Check spelling and grammatical corrections using tools such as Grammarly.

## User guides

In addition to the above while writing user guides follow these conventions:

* Use second-person pronouns i.e. you, your, etc. in the instructions/steps.
* Use the bold and italicized font for UI elements i.e. dashboard names, button labels, information fields, etc.
* Use the exact name and case for the UI elements as shown in the user interface.
* Use quotes for a phrase/word if the phrase/word has to be represented as is.

## Specification for diagram

Follow the below specification while creating diagrams in Miro

<table><thead><tr><th width="116.5"></th><th></th></tr></thead><tbody><tr><td>Font </td><td>Opensans</td></tr><tr><td>Font Size</td><td>18px</td></tr><tr><td>Logos</td><td>Use the font available in the URL: <a href="https://drive.google.com/drive/folders/1LC9F1WXOKv9xPrC6dHLBFuUG5GOaiPvo?usp=drive_link">https://drive.google.com/drive/folders/1LC9F1WXOKv9xPrC6dHLBFuUG5GOaiPvo?usp=drive_link</a></td></tr><tr><td>Zoom</td><td>Default board zoom - 100%.  At this zoom level the diagram must fit in a normal screen.</td></tr><tr><td>Export image</td><td><ul><li>Size: Medium </li><li>Format: JPG</li></ul></td></tr></tbody></table>



{% embed url="https://miro.com/app/board/uXjVN8_Q7nI=/" %}
Diagram specification
{% endembed %}

## Embed a Miro image

To learn how to embed a miro image in the GitBook, [click here](embed-a-miro-diagram.md)

## Set an image within the frame in Miro

To learn how to set an image within the frame in miro, [click here](set-an-image-for-a-start-view.md)

## Avoid repetition

Do not repeat the content from concept documentation to any other type of documentation and vice versa. Instead, provide the relevant link.

Do not repeat the similar content inside the documentation.  Instead, provide the relevant link.

## Usage of consistency in words

| Use           | Do not use     |
| ------------- | -------------- |
| Prerequisites | Pre-requisites |
| eSignet       | e-Signet       |

## Usage of Symbols

<table><thead><tr><th width="147">Document</th><th>Symbol</th></tr></thead><tbody><tr><td>User guide</td><td><ul><li>Click the emoji that appears before the title of the user guide.</li><li>Type book in the search field and select the encircled symbol </li></ul><p><img src="../../../.gitbook/assets/emoji-symbol-user-guide.png" alt="" data-size="original"></p><p>The symbol is displayed before the title of the user guide.</p><p><img src="../../../.gitbook/assets/user-guide-symbol.png" alt="" data-size="original"></p></td></tr><tr><td>Concept </td><td><ul><li>Enter '/' before the title of the user guide that appear at the end of the concept documentation. </li></ul><p>The below options are displayed.</p><p><img src="../../../.gitbook/assets/options-emoji.png" alt=""></p><ul><li>Click the <em><strong>Emoji</strong></em></li><li>Type book in the search field</li><li>Choose the option "<em><strong>:notebook_with_decorative _cover</strong></em>"</li></ul><p><img src="../../../.gitbook/assets/userguide-symbol.png" alt="" data-size="original"></p><p></p><p>The symbol is displayed before the title of the user guide.</p><p></p><p><img src="../../../.gitbook/assets/concept-user-guide-image.png" alt="" data-size="original"></p></td></tr></tbody></table>

## Rules to add link

<table><thead><tr><th width="390">Use</th><th>Do not use</th></tr></thead><tbody><tr><td><p>For external end-users, to hyperlink the URLs to access the OpenG2P system, </p><ul><li>Use a generic URL to hyperlink. For example, the end-users organisation specific URLs after their installation of OpenG2P system.</li></ul></td><td><p>For external end-users, to hyperlink the URLs to access the OpenG2P system, </p><ul><li>Do not hyperlink the internal URLs. For example, the environment-specific URLs such as test, dev, QA, stage, and so on.</li></ul></td></tr></tbody></table>

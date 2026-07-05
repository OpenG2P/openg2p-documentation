# Embed a Miro diagram

## Embed Miro board in Gitbook

To directly embed link of Miro board, follow the procedure given below.  Note that this ensures that the diagram is up-to-date whenever a change is made. _The Downside is it affects usability, esp while scrolling through the pages, in which case you may want to export the diagrams and directly embed them in Gitbook (section below)_

* Make sure the diagram on Miro has permissions for anyone to view the boards (this is available under Share)
* Set a "Start view" for the diagram under Board --> Start view.  Make sure view box is just about the size of the digram.
* Copy the board URL/link
* In Gitbook, insert it using "Embed URL".
* To skip the "See the board" button and view the diagram directly add the parameter `&embedAutoplay=true` to the end of the embed URL. Example:&#x20;

```
https://miro.com/app/board/uXjVNGpmGPw=/?share_link_id=254439439095
&embedAutoplay=true
```

## Export a board and insert in Gitbook

* Miro --> Board --> Export --> Save as image
* Stretch/adjust the frame to cover the diagram completely.
* Select "Medium" resolution for export
* Export the image to your machine
* Rename the image with lower case and hyphens only. Eg.  `g2p-bridge-tech-architecture.jpg`.
* Insert the image in the required location in Gitbook.&#x20;

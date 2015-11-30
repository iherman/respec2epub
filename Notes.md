1. The base.css file is included through a strange procedure into the system in the old TR css files; fantasai's version uses the standard ``@import`` mechanism
    * This means that simulating the import for the old version is still necessary, but becomes unnecessary with the new one. Not sure how to handle that programatically
    * However, **problem**. This approach, at least for the old version, requires to add a *new* link element, maintaining the reference to the base as well as adding a new one. *Which does not work due to the ``html5lib`` bug on handling the DOM elements*, one can only *add* an element at the end of an element, and not as a sibling on the spot. What this means is that handling the old style stuff may not be possible:-(
1. The references to the images should work, but it they are managed via content negotiations. Means
    * Does such a reference, without the suffix, works properly in a reader? (Probably yes). I not, the suffix may have to be added artificially.
1. The changes, probably:
    * in line 178 in ``document.py`` the reference to the base should be maintained (probably) due to the first point above, but the style sheet itself should be added to the overall list, too (and the link reference maintained, maybe with the .css extension added?)
    * in line 182 in ``doc2epub.py`` wonder what is necessary to transfer from the config file. Possibly only the long logo, which then could be handled specifically, and that field can be removed from the config file. Actually, the whole logo transfer may be unnecessary but… it may clash with the ibook problem of margins

However: the whole issue of table of content on the left is in limbo. For an ebook, this is totally unnecessary, because I do create a nav file overall! I wonder if the simplest (and crudest) approach is not to remove the TOC altogether from the generated output… With the new style this may be much more acceptable.

How to do this: does a display none works with a @pages output? Probably not…

The bottomline seems to be: touching the old approach may not be worth the trouble, due to the
* handling of the margins that require changes anyway
* the problem with the ``html5lib`` bug
* the approach of making the TOC invisible anyway...

An alternative is to wait and see whether there will be a possibility to choose between the old version and the new. It may very well be that the new setting would work without further ado (just referring to a different ``base.css``) and with an additional trick of removing the TOC. The real question will be
* Is it possible to see if the document should be processed with the new or the old style sheet, or
* The new style sheet will be the only one that counts

To ask…
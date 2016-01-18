# To-Dos

* Utils.py contains the `change_DOM` method that implements a hack around a Readium bug. When the newer version of Readium is deployed, that hack should be removed.
* If the 2016 style sheets come out, see if there is something to be changed. This may require a revision on how the style sheets are handled in general: with the reading of the css files in place in general, the part on handling the various css files for various document types should be revised to stick with the original structure
    * At the moment, it seems that the current structure is very much the same, except for the names, ie, many things may have to be duplicated:-(
    * The TOC is now using a <nav> element. It may be an idea to move the whole of the nav into the navigation file, and make that stuff display none for the ebook!
    * Changing for a new setting with the old style version is difficult due to a ``html5lib`` bug. See the Notes.md file.
    

# Possible improvements (mainly if there is demand, which is not sure)

* Bikeshed is shaky as for finding the dated uri. At the moment, it does not always work; leave it as is. At some point this may have to be looked at again, if the CSS people are really interested…
* Multi-file documents; essentially, taking over some of the features from [tr2epub](https://github.com/iherman/tr2epub)
* Direct file access?
* Python 3?


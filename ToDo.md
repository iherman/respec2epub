# To-Dos

* Utils.py contains the `change_DOM` method that implements a hack around a Readium bug. When the newer version of Readium is deployed, that hack should be removed.
* With the reading of the css files in place in general, the part on handling the various css files for various document types should be revised to stick with the original structure

# Possible improvements (mainly if there is demand, which is not sure)

* Bikeshed is shaky as for finding the dated uri. At the moment, it does not always work; leave it as is. At some point this may have to be looked at again, if the CSS people are really interested...
* Multi-file documents; essentially, taking over some of the features from [tr2epub](https://github.com/iherman/tr2epub)
* Direct file access?
* Python 3?


# Functional todo-s

* Utils.py contains the `change_DOM` method that implements a hack around a Readium bug. When the newer version of Readium is deployed, that hack should be removed.

## Current code


# Quality todo-s

* Add an option for the unpublished respec document (hm. that may not work because there is no such thing as a short name for that one...): most of the metadata are missing:-(
* There is a dependency on the http://www.w3.org server access right now, even if things are run on localhost, namely to access, e.g., the logos. Maybe worth adding a fallback URI in the conf file for such cases? Or a fallback domain?



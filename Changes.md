# Version 1.2

* Added the  ``-*- coding: utf-8 -*-`` sign to setup.py


# Version 1.1

* Added a hack to add a ``type="text/css`` to link elements referring to stylesheets. Not necessary per HTML, but some reading systems require it
* Added an ``("area","href")`` pair to the list of external references that should be checked and act upon.
* Changed the hack of wrapping all content into a ``<div>``: instead of using ``@id`` with a phony value, using ``@role=main`` itself. A check has also been added to avoid doing that if there is already such a wrapper (this is a feature that may be added to ReSpec). For consistency, the same pattern is used in the cover page.
* The code makes now use of the ReSpec config, if generated into the document by ReSpec (newer releases do). That means that the cover page is a bit richer than without it, and the code itself is cleaner. The old, 'scraping' approach stays in the code, though, for older files and for Bikeshed. 
* Using the ReSpec config data the various other spec types (base, unofficial, etc) are better handled and produce some decent output (even if those documents are not necessarily /TR documents...)


Plus some minor bug and documentation improvements.

# Version 1.0

First "official" release
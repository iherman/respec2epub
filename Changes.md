# Version 1.3
* A basic CSS processing has been added. This means that ``import`` and ``url`` statements in CSS files are recognized, imports are treated recursively, and all resources are downloaded as required. This also means that the built-in knowledge on the structure of CSS files is gone. This change was necessary to be able to adapt the script to the newer versions of TR style sheets
* Some entries have been added to manage the stylesheets introduced in 2016. In particular, the TOC is kept artificially embedded (the approach chosen to push the TOC on the left if the screen is wide enough is not suitable for ePub, where readers have usually their own management of TOC-s.

Plus some minor improvements on programming and documentation.

# Version 1.2

* Added the  ``-*- coding: utf-8 -*-`` sign to setup.py
* Improved the setup procedure, to make it usable directly with pip
* Added a ``page-break-inside: avoid`` in the ``book.css`` template for the ``<figure>`` element to ensure that the capture of a figure is on the same page.
* Added an extra CSS parsing, so that if CSS files are imported via an ``@import`` rule, or whether resources are referred to via ``url`` values in a CSS statement, these are also copied to the output (and references added to the package file).

Plus some minor documentation improvements


# Version 1.1

* Added a hack to add a ``type="text/css`` to link elements referring to stylesheets. Not necessary per HTML, but some reading systems require it
* Added an ``("area","href")`` pair to the list of external references that should be checked and act upon.
* Changed the hack of wrapping all content into a ``<div>``: instead of using ``@id`` with a phony value, using ``@role=main`` itself. A check has also been added to avoid doing that if there is already such a wrapper (this is a feature that may be added to ReSpec). For consistency, the same pattern is used in the cover page.
* The code makes now use of the ReSpec config, if generated into the document by ReSpec (newer releases do). That means that the cover page is a bit richer than without it, and the code itself is cleaner. The old, 'scraping' approach stays in the code, though, for older files and for Bikeshed. 
* Using the ReSpec config data the various other spec types (base, unofficial, etc) are better handled and produce some decent output (even if those documents are not necessarily /TR documents...)

Plus some minor bug and documentation improvements.

# Version 1.0

First "official" release
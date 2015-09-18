.. Respec to EPUB documentation master file, created by
   sphinx-quickstart on Wed Aug 12 15:42:46 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ReSpec to EPUB utility
======================

Get an HTML document in `ReSpec <http://www.w3.org/respec/>`_, or an HTML5 document *generated* by
`ReSpec <http://www.w3.org/respec/>`_ or `Bikeshed <https://wiki.csswg.org/tools/bikeshed>`_
and generate an EPUB3 file for off-line reading. ReSpec “sources” are transformed into HTML on the fly
using a separate Web Service set up (at W3C) for that purpose.  Style sheets, images, scripts, etc.,
are downloaded and included in the book, provided they are on the same Web domain as the original file (i.e., in
Python’s URL library speak, if the URL-s of those resources have the same net location, i.e., ``netloc``).

The package is **not** a generic HTML➝EPUB 3 solution.

The package can be used through a command line tool (see the manual below) or can be the core of a separate Web Service
(it will be installed on the `W3C Labs site <https://labs.w3.org/epub-generator/>`__). The
save menu of ReSpec is extended so that the service can be invoked from within respec when the user generates
the final output (see the `ReSpec <http://www.w3.org/respec/>`__ documentation for further details).

Adjustments to readers
----------------------

The code includes a number of adjustments and hacks to accommodate with the idiosyncrasy's (or bugs) of current readers.
See the :py:meth:`.utils.Utils.change_DOM` and (to a lesser extend) :py:meth:`.utils.Utils.html_to_xhtml` methods for further details.


Dependencies
------------

The package relies on Python 2.7. The script does not work (yet?) with Python 3; the underlying HTML library
(e.g., HTML5Lib) seems to have issues with encoding, UTF-8, etc.

Apart from the standard Python libraries the package also depends on
`HTML5lib <https://pypi.python.org/pypi/html5lib>`__, an HTML5 parser library for
Python. This package has been tested with version 0.99999 of that library; earlier versions had Unicode
encoding issues, and should not be used.

Metadata
--------

* Version: |version|
* Document creation date: |today|
* Author: Ivan Herman
* Contact: ivan@w3.org
* Licence: W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>
* Repository: <https://github.com/iherman/respec2epub>

Thanks also to Zheng Xu (Rakuten/Kobo) who helped me in some of the interoperability problems around ePub readers.


2. Table of Contents
====================

.. toctree::

   manual
   rp2epub
   driver
   document
   package
   utils
   templates
   config

Indices and tables
==================

* :ref:`genindex`


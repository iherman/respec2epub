# -*- coding: utf-8 -*-

"""
Various configuration variables.

.. py:data:: logger

  Logger (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance)

.. py:data:: DEFAULT_FILES

  Items that have to be added to the book's manifest, no matter what; an array tuples of the form ``(file,media-type,id,properties)``

.. py:data:: CSS_LOGOS

  The URL-s to the pictures on the upper left hand side of the front page, denoting the document status, as well as the
  local names of the same images. It is a dictionary with keys set to the possible document status; used to download
  the right image into the book.

.. py:data:: TO_TRANSFER

  Array of (url,local_name) pairs of resources that must be transferred and added to the output. This may be expanded run time;
  by default it includes the W3C logos and the base CSS file.
"""

# logger (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance)
logger = None

# noinspection PyPep8
# Items that have to be added to the book's manifest, no matter what; tuples of the form (file,media-type,id,properties)
DEFAULT_FILES = [
	("nav.xhtml", "application/xhtml+xml", "nav", "nav"),
	("toc.ncx", "application/x-dtbncx+xml", "ncx", ""),
	("Assets/w3c_main.png", "image/png", "w3c_main", ""),
	("Assets/base.css", "text/css", "StyleSheets-base", ""),
	("Assets/book.css", "text/css", "StyleSheets-book", ""),
	("cover.xhtml", "application/xhtml+xml", "start", "")
]

# noinspection PyPep8
# The URL-s to the pictures on the upper left hand side of the front page, denoting the document status,
# and also the path within the book.
CSS_LOGOS = {
	"REC"  : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-REC.png"),
	"NOTE" : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-NOTE.png"),
	"PER"  : ("http://www.w3.org/StyleSheets/TR/logo-PER.png", "Assets/logo-PR.png"),
	"PR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-PR.png"),
	"CR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-CR.png"),
	"WD"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-WD.png"),
	"ED"   : ("http://www.w3.org/StyleSheets/TR/logo-ED.png", "Assets/logo-ED.png"),
}

# noinspection PyPep8
# Default array of (url,local_name) pairs of resources that must be transferred and added to the output.
# This may be expanded run time.
TO_TRANSFER = [
	("http://www.w3.org/Icons/w3c_main.png", "Assets/w3c_main.png"),
	("http://www.w3.org/Icons/w3c_home.png", "Assets/w3c_home.png"),
	("http://www.w3.org/StyleSheets/TR/base.css", "Assets/base.css"),
]

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

.. py:data:: ACCEPTED_MEDIA_TYPES

  Dictionary of media types that are accepted for inclusion in an epub file, providing also the suffix used
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
# and also the path within the book. A dictionary with keys denoting the status; values like the :py:data:`TO_TRANSFER`
CSS_LOGOS = {
	"REC"  : ("http://www.w3.org/StyleSheets/TR/logo-REC.png",  "http://localhost:8001/StyleSheets/TR/logo-REC.png",  "Assets/logo-REC.png"),
	"NOTE" : ("http://www.w3.org/StyleSheets/TR/logo-NOTE.png", "http://localhost:8001/StyleSheets/TR/logo-NOTE.png", "Assets/logo-NOTE.png"),
	"PER"  : ("http://www.w3.org/StyleSheets/TR/logo-PER.png",  "http://localhost:8001/StyleSheets/TR/logo-PER.png",  "Assets/logo-PR.png"),
	"PR"   : ("http://www.w3.org/StyleSheets/TR/logo-PR.png",   "http://localhost:8001/StyleSheets/TR/logo-PR.png",   "Assets/logo-PR.png"),
	"CR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png",   "http://localhost:8001/StyleSheets/TR/logo-CR.png",   "Assets/logo-CR.png"),
	"WD"   : ("http://www.w3.org/StyleSheets/TR/logo-WD.png",   "http://localhost:8001/StyleSheets/TR/logo-WD.png",   "Assets/logo-WD.png"),
	"ED"   : ("http://www.w3.org/StyleSheets/TR/logo-ED.png",   "http://localhost:8001/StyleSheets/TR/logo-ED.png",   "Assets/logo-ED.png"),
}

# noinspection PyPep8
# Default array of (url,local_name) pairs of resources that must be transferred and added to the output.
# This may be expanded run time.
TO_TRANSFER = [
	("http://www.w3.org/Icons/w3c_main.png",      "http://localhost:8001/Icons/w3c_main.png",      "Assets/w3c_main.png"),
	("http://www.w3.org/Icons/w3c_home.png",      "http://localhost:8001/Icons/w3c_home.png",      "Assets/w3c_home.png"),
	("http://www.w3.org/StyleSheets/TR/base.css", "http://localhost:8001/StyleSheets/TR/base.css", "Assets/base.css"),
]

# suffixes and media types for resources that are recognized by EPUB
# noinspection PyPep8,PyPep8
ACCEPTED_MEDIA_TYPES = {
	"text/html"                   : "html",
	"application/xhtml+xml"       : "xhtml",
	"text/css"                    : "css",
	"image/svg+xml"               : "svg",
	"image/png"                   : "png",
	"image/jpeg"                  : "jpg",
	"image/gif"                   : "gif",
	"application/javascript"      : "js",
	"text/csv"                    : "csv",
	"text/turtle"                 : "ttl",
	"application/json"            : "json",
	"application/ld+json"         : "jsonld",
	"application/xml"             : "xml",
	"application/font-woff"       : "woff",
	"application/vnd.ms-opentype" : "opf",
	"audio/mpeg"                  : "mp3",
	"video/mp4"                   : "mp4",
	"video/webm"                  : "webm",
	"video/ogg"                   : "ogg"
}

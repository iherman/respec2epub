# -*- coding: utf-8 -*-

"""
Various configuration variables.

.. py:data:: logger

  Logger (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance)

.. py:data:: DEFAULT_FILES

  Items that have to be added to the book's manifest, no matter what; an array tuples of the form ``(file,media-type,id,properties)``

.. py:data:: DOCTYPE_INFO

  A dictionary keyed by document types (as accepted by ReSpec); each value is a dictionary again with keys ``logo`` for the
  logo URI that has to be extracted from the W3C site, ``logo_local`` for the logo URI that may be available locally (used
  if the script is run locally; these values may have to be adapted for local use), ``logo_asset`` for the URI to be used
  in the generated ``book.css`` file, ``uri_prefix`` for the string that may be used as a prefix in the document
  short name URI (as used at W3C), and ``subtitle`` for the name of the document type in human term

.. py:data:: TO_TRANSFER

  Array of (url,local_name) pairs of resources that must be transferred and added to the output. This may be expanded run time;
  by default it includes the W3C logos and the base CSS file.

.. py:data:: ACCEPTED_MEDIA_TYPES

  Dictionary of media types that are accepted for inclusion in an epub file, providing also the suffix used

.. py:data:: EXTERNAL_REFERENCES

   Pairs of element names and attributes for content that should be downloaded and referred to

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


# Pairs of element names and attributes for content that should be downloaded and referred to
# noinspection PyPep8
EXTERNAL_REFERENCES = [
	("img", "src"),
	("img", "longdesc"),
	("script", "src"),
	("object", "data"),
	("iframe", "src"),
	("embed", "src"),
	("video", "src"),
	("audio", "src"),
	("source", "src"),
	("track", "src")
]

# noinspection PyPep8
# The URL-s to the pictures on the upper left hand side of the front page, denoting the document status,
# and also the path within the book. A dictionary with keys denoting the status; values like the :py:data:`TO_TRANSFER`
DOCTYPE_INFO = {
	"base": {
		"logo"      : None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"  : "W3C Document"
	},
	"MO": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/MO.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/MO.png",
		"logo_asset": "Assets/MO.png",
		"uri_prefix": None,
		"subtitle"	: "W3C Member-Only Document"
	},
	"unofficial": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-unofficial.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-unofficial.png",
		"logo_asset": "Assets/logo-unofficial.png",
		"uri_prefix": None,
		"subtitle"	: "Unofficial Draft"
	},
	"ED": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-ED.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-ED.png",
		"logo_asset": "Assets/logo-ED.png",
		"uri_prefix": "ED",
		"subtitle"	: "W3C Editor's Draft"
	},
	"FPWD": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-WD.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-WD.png",
		"logo_asset": "Assets/logo-WD.png",
		"uri_prefix": None,
		"subtitle"	: "W3C First Public Working Draft"
	},
	"WD": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-WD.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-WD.png",
		"logo_asset": "Assets/logo-WD.png",
		"uri_prefix": "WD",
		"subtitle"	: "W3C Working Draft"
	},
	"LC": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-WD.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-WD.png",
		"logo_asset": "Assets/logo-WD.png",
		"uri_prefix": None,
		"subtitle"	: "W3C Last Call Working Draft"
	},
	"CR": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-CR.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-CR.png",
		"logo_asset": "Assets/logo-CR.png",
		"uri_prefix": "CR",
		"subtitle"	: "W3C Candidate Recommendation"
	},
	"PR": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-PR.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-PR.png",
		"logo_asset": "Assets/logo-PR.png",
		"uri_prefix": "PR",
		"subtitle"	: "W3C Proposed Recommendation"
	},
	"PER": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-PER.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-PER.png",
		"logo_asset": "Assets/logo-PR.png",
		"uri_prefix": "PER",
		"subtitle"	: "W3C Proposed Edited Recommendation"
	},
	"REC": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-REC.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-REC.png",
		"logo_asset": "Assets/logo-REC.png",
		"uri_prefix": "REC",
		"subtitle"	: "W3C Recommendation"
	},
	"RSCND": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-RSCND.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-RSCND.png",
		"logo_asset": "Assets/logo-RSCND.png",
		"uri_prefix": "RSCND",
		"subtitle"	: "W3C Rescinded Recommendation"
	},
	"NOTE": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-NOTE.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-NOTE.png",
		"logo_asset": "Assets/logo-NOTE.png",
		"uri_prefix": "NOTE",
		"subtitle"	: "W3C Note"
	},
	"FPWD-NOTE": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-NOTE.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-NOTE.png",
		"logo_asset": "Assets/logo-NOTE.png",
		"uri_prefix": None,
		"subtitle"	: "W3C Working Group Note"
	},
	"WG-NOTE": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-WG-Note.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-WG-Note.png",
		"logo_asset": "Assets/logo-WG-Note.png",
		"uri_prefix": None,
		"subtitle"	: "W3C Working Group Note"
	},
	"IG-NOTE": {
		"logo" 		: "http://www.w3.org/StyleSheets/TR/logo-IG-Note.png",
		"logo_local": "http://localhost:8001/StyleSheets/TR/logo-IG-Note.png",
		"logo_asset": "Assets/logo-IG-Note.png",
		"uri_prefix": None,
		"subtitle"	: "Interest Group Note"
	},
	"finding": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C TAG Finding"
	},
	"draft-finding": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Draft TAG Finding"
	},
	"Member-SUBM": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Member Submission"
	},
	"Team-SUBM": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Team Submission"
	},
	"BG-DRAFT": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Draft Business Group Report"
	},
	"BG-FINAL": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Business Group Report"
	},
	"CG-DRAFT": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Draft Community Group Report"
	},
	"CG-FINAL": {
		"logo" 		: None,
		"logo_local": None,
		"logo_asset": None,
		"uri_prefix": None,
		"subtitle"	: "W3C Community Group Report"
	}
}

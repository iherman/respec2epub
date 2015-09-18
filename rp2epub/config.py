# -*- coding: utf-8 -*-

"""
Various configuration variables.

.. py:data:: logger

  Logger (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance)

.. py:data:: DEFAULT_FILES

  Items that have to be added to the book's manifest, no matter what; an array tuples of the form ``(file,media-type,id,properties)``.
  Typical example: entry for the table of content file

.. py:data:: DOCTYPE_INFO

  A dictionary keyed by document types (as accepted by ReSpec); each value is a also a dictionary of the form:

  ``logo_transfer``
  	A tuple containing the URL of the logo to be copied into the book, a URL (typically ``http://localhost``
  	for a local version thereof, and the name in the final book, of the form ``Assets/XXXX``
  ``uri_prefix``
  	String that may be used as a prefix in the document short name URI (as used at W3C), e.g., ``WD``
  ``subtitle``
    The name of the document in Human term, e.g., ``W3C Working Draft``
  ``transfer``
    Pointer to an array of tuple (of the same structures as the one in ``logo_transfer``) providing references
    to files that must be copied to the book additionally to the logo.
  ``padding``
    Padding CSS specification (ie, value of a ``padding`` CSS directives) that must be applied to the whole content of the file.

.. py:data:: ACCEPTED_MEDIA_TYPES

  Dictionary of media types that are accepted for inclusion in an epub file. The media types are used as keys, pointing
  at the suffix usually used (if needed)

.. py:data:: EXTERNAL_REFERENCES

   Pairs of HTML element names and corresponding attributes that should be looked for in the source for content that
   may have to be downloaded to the book. (In general, only essentially relative references are considered for download, global
   references are not. There are some exceptions, e.g., W3C specific stylesheets or images.)

**Source code:** `utils.py <https://github.com/iherman/respec2epub/blob/master/rp2epub/utils.py>`_

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
# Default array of (url,local_name) pairs of resources that must be transferred and added to the output.
# This may be expanded run time.

_to_transfer_logos = [
	("http://www.w3.org/Icons/w3c_home.png", "http://localhost:8001/Icons/w3c_home.png", "Assets/w3c_home.png"),
	("http://www.w3.org/Icons/w3c_main.png", "http://localhost:8001/Icons/w3c_main.png", "Assets/w3c_main.png")
]

TO_TRANSFER = _to_transfer_logos + [
	("http://www.w3.org/StyleSheets/TR/base.css", "http://localhost:8001/StyleSheets/TR/base.css", "Assets/base.css")
]

TO_TRANSFER_BG_CG = _to_transfer_logos + [
	("http://www.w3.org/community/src/css/spec/base.css", "http://localhost:8001/community/src/css/spec/base.css", "Assets/base.css")
]

TO_TRANSFER_TEAM_SUBM = TO_TRANSFER + [
	("http://www.w3.org/Icons/team_subm.png", "http://localhost:8001/Icons/team_subm.png", "Assets/team_subm.png")
]

TO_TRANSFER_MEMBER_SUBM = TO_TRANSFER + [
	("http://www.w3.org/Icons/member_subm.png", "http://localhost:8001/Icons/member_subm.png", "Assets/member_subm.png")
]

# noinspection PyPep8
# The URL-s to the pictures on the upper left hand side of the front page, denoting the document status,
# and also the path within the book. A dictionary with keys denoting the status; values like the :py:data:`TO_TRANSFER`
DOCTYPE_INFO = {
	"base": {
		"logo_transfer"	: None,
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"  	: "W3C Document"
	},
	"MO": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/MO.png", "http://localhost:8001/StyleSheets/TR/MO.png", "Assets/MO.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Member-Only Document"
	},
	"unofficial": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-unofficial.png", "http://localhost:8001/StyleSheets/TR/logo-unofficial.png", "Assets/logo-unofficial.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "Unofficial Draft"
	},
	"ED": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-ED.png", "http://localhost:8001/StyleSheets/TR/logo-ED.png", "Assets/logo-ED.png"),
		"uri_prefix"	: "ED",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Editor's Draft"
	},
	"FPWD": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-WD.png", "http://localhost:8001/StyleSheets/TR/logo-WD.png", "Assets/logo-WD.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C First Public Working Draft"
	},
	"WD": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-WD.png", "http://localhost:8001/StyleSheets/TR/logo-WD.png", "Assets/logo-WD.png"),
		"uri_prefix"	: "WD",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Draft"
	},
	"LC": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-WD.png", "http://localhost:8001/StyleSheets/TR/logo-WD.png", "Assets/logo-WD.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Last Call Working Draft"
	},
	"CR": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "http://localhost:8001/StyleSheets/TR/logo-CR.png", "Assets/logo-CR.png"),
		"uri_prefix"	: "CR",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Candidate Recommendation"
	},
	"PR": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-PR.png", "http://localhost:8001/StyleSheets/TR/logo-PR.png", "Assets/logo-PR.png"),
		"uri_prefix"	: "PR",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Proposed Recommendation"
	},
	"PER": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-PER.png", "http://localhost:8001/StyleSheets/TR/logo-PER.png", "Assets/logo-PER.png"),
		"uri_prefix"	: "PER",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Proposed Edited Recommendation"
	},
	"REC": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-REC.png", "http://localhost:8001/StyleSheets/TR/logo-REC.png", "Assets/logo-REC.png"),
		"uri_prefix"	: "REC",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Recommendation"
	},
	"RSCND": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-RSCND.png", "http://localhost:8001/StyleSheets/TR/logo-RSCND.png", "Assets/logo-RSCND.png"),
		"uri_prefix"	: "RSCND",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Rescinded Recommendation"
	},
	"NOTE": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-NOTE.png", "http://localhost:8001/StyleSheets/TR/logo-NOTE.png", "Assets/logo-NOTE.png"),
		"uri_prefix"	: "NOTE",
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Note"
	},
	"FPWD-NOTE": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-NOTE.png", "http://localhost:8001/StyleSheets/TR/logo-NOTE.png", "Assets/logo-NOTE.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Group Note"
	},
	"WG-NOTE": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-NOTE.png", "http://localhost:8001/StyleSheets/TR/logo-NOTE.png", "Assets/logo-NOTE.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Group Note"
	},
	"IG-NOTE": {
		"logo_transfer" : ("http://www.w3.org/StyleSheets/TR/logo-NOTE.png", "http://localhost:8001/StyleSheets/TR/logo-NOTE.png", "Assets/logo-NOTE.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "Interest Group Note"
	},
	"finding": {
		"logo_transfer" : None,
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C TAG Finding"
	},
	"draft-finding": {
		"logo_transfer" : None,
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Draft TAG Finding"
	},
	"Member-SUBM": {
		"logo_transfer" : None,
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_MEMBER_SUBM,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Member Submission"
	},
	"Team-SUBM": {
		"logo_transfer" : None,
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_TEAM_SUBM,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Team Submission"
	},
	"BG-DRAFT": {
		"logo_transfer" : ("http://www.w3.org/community/src/css/spec/back-bg-draft.png", "http://localhost:8001/community/src/css/spec/back-bg-draft.png", "Assets/back-bg-draft.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_BG_CG,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Draft Business Group Report"
	},
	"BG-FINAL": {
		"logo_transfer" : ("http://www.w3.org/community/src/css/spec/back-bg-final.png", "http://localhost:8001/community/src/css/spec/back-bg-final.png", "Assets/back-bg-final.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_BG_CG,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Business Group Report"
	},
	"CG-DRAFT": {
		"logo_transfer" : ("http://www.w3.org/community/src/css/spec/back-cg-draft.png", "http://localhost:8001/community/src/css/spec/back-cg-draft.png", "Assets/back-cg-draft.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_BG_CG,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Draft Community Group Report"
	},
	"CG-FINAL": {
		"logo_transfer" : ("http://www.w3.org/community/src/css/spec/back-cg-final.png", "http://localhost:8001/community/src/css/spec/back-cg-final.png", "Assets/back-cg-final.png"),
		"uri_prefix"	: None,
		"transfer"		: TO_TRANSFER_BG_CG,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Community Group Report"
	}
}

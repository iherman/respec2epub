# -*- coding: utf-8 -*-

"""
Various configuration variables.

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
	"text/plain"                  : "txt",
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
# Note: the base.css file here is only used, by default, to the nav and cover pages. Otherwise
# the relevant base is downloaded automatically
TO_TRANSFER = [
	("http://www.w3.org/Icons/w3c_main.png", "Icons/w3c_main.png"),
	("http://www.w3.org/StyleSheets/TR/base.css", "StyleSheets/TR/base.css")
]

# noinspection PyPep8
# some information necessary per doc type: the prefix to be used when creating the full, dated URI, the padding
# that should be put into the body of the document, and the subtitle to be used on the cover page
# The padding values are need for the pre-2016 style sheets...
DOCTYPE_INFO = {
	"base": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"  	: "W3C Document"
	},
	"MO": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Member-Only Document"
	},
	"unofficial": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "Unofficial Draft"
	},
	"ED": {
		"uri_prefix"	: "ED",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Editor's Draft"
	},
	"FPWD": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C First Public Working Draft"
	},
	"WD": {
		"uri_prefix"	: "WD",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Draft"
	},
	"LC": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Last Call Working Draft"
	},
	"CR": {
		"uri_prefix"	: "CR",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Candidate Recommendation"
	},
	"PR": {
		"uri_prefix"	: "PR",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Proposed Recommendation"
	},
	"PER": {
		"uri_prefix"	: "PER",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Proposed Edited Recommendation"
	},
	"REC": {
		"uri_prefix"	: "REC",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Recommendation"
	},
	"RSCND": {
		"uri_prefix"	: "RSCND",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Rescinded Recommendation"
	},
	"NOTE": {
		"uri_prefix"	: "NOTE",
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Note"
	},
	"FPWD-NOTE": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Group Note"
	},
	"WG-NOTE": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Working Group Note"
	},
	"IG-NOTE": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "Interest Group Note"
	},
	"finding": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C TAG Finding"
	},
	"draft-finding": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Draft TAG Finding"
	},
	"Member-SUBM": {
		"uri_prefix"	: None,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Member Submission"
	},
	"Team-SUBM": {
		"uri_prefix"	: None,
		"padding"		: "2em 1em 2em 70px;",
		"subtitle"		: "W3C Team Submission"
	},
	"BG-DRAFT": {
		"uri_prefix"	: None,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Draft Business Group Report"
	},
	"BG-FINAL": {
		"uri_prefix"	: None,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Business Group Report"
	},
	"CG-DRAFT": {
		"uri_prefix"	: None,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Draft Community Group Report"
	},
	"CG-FINAL": {
		"uri_prefix"	: None,
		"padding"		: "2em 80px 2em 160px;",
		"subtitle"		: "W3C Community Group Report"
	}
}

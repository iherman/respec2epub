#! /usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyPep8
"""
Get a W3C TR document based on its URI and dump it into an EPUB3 file for off-line reading.

It is a bit like the browser archive commands, but the result is an EPUB3 file. Stylesheets and images are
downloaded and included in the book, provided they are on the same Web domain as the original file (i.e., in Python's URL
library speak, if the URL-s of those resources have the same net location, i.e., ``netloc``).

The result is an EPUB3 in the same folder, whose name is the last part of the URI, expanded with the ``.epub`` suffix.

The program depends on the html5lib library for HTML parsing.

.. autodata::
"""
# TODO: handle the possible css references to other css files or to images

# noinspection PyPep8Naming
import zipfile
import html5lib
from xml.etree.ElementTree import ElementTree
from urlparse import urlparse, urlunparse

from .templates import meta_inf, BOOK_CSS
from .document import DocumentWrapper
from .package import Package

from .utils import HttpSession, et_to_book

CONVERTER = "https://labs.w3.org/spec-generator/?type=respec&url="

# These are the items that have to be added to each file and package, no matter what: (id,file,media-type,properties)
# noinspection PyPep8
#: Items that have to be added to the book's manifest, no matter; tuples of the form (id,file,media-type,properties)
DEFAULT_FILES = [
		("nav.xhtml", "application/xhtml+xml", "nav", "nav"),
		("toc.ncx", "application/x-dtbncx+xml", "ncx", ""),
		("cover.xhtml", "application/xhtml+xml", "cover", ""),
		("Assets/w3c_main.png", "image/png", "w3c_main", ""),
		("Assets/base.css", "text/css", "StyleSheets-base", ""),
		("Assets/book.css", "text/css", "StyleSheets-book", "")
]

# noinspection PyPep8,PyPep8,PyPep8
_To_transfer = [
	("http://www.w3.org/Icons/w3c_main.png", "Assets/w3c_main.png"),
	("http://www.w3.org/StyleSheets/TR/base.css", "Assets/base.css"),
]

# noinspection PyPep8
CSS_LOGOS = {
	"REC"  : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-REC.png"),
	"NOTE" : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-NOTE.png"),
	"PR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-PR.png"),
	"CR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-CR.png"),
	"WD"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-WD.png"),
}


###################################################################################
# noinspection PyPep8
class DocToEpub:
	"""
	Top level entry to the program; receives the URI to be retrieved

	:param str top_uri: the URI that was used to invoke the package, ie, the location of the document source
	:param boolean is_respec: flag whether the source is a respec source (ie, has to be transformed through spec generator) or not
	"""
	# noinspection PyPep8
	def __init__(self, top_uri, is_respec=True):
		self._document_wrapper = None
		self._top_uri          = top_uri
		self._book             = None
		self._domain           = urlparse(top_uri).netloc

		spec = GenerateSpec(top_uri, is_respec)
		self._document = spec.document
		self._html     = spec.html
		self._base     = spec.base

	@property
	def base(self):
		"""Base URI for the document (used to retrieve additional resources, if needed)"""
		return self._base

	@property
	def domain(self):
		"""Domain of the URI's home"""
		return self._domain

	@property
	def document(self):
		"""Document, as parsed; an :py:class:`xml.etree.ElementTree.Element` instance"""
		return self._document

	@property
	def document_wrapper(self):
		"""Wrapper around the document, containing extra meta information for packaging"""
		return self._document_wrapper

	@property
	def html(self):
		"""HTML element as parsed; :py:class:`xml.etree.ElementTree.ElementTree` instance"""
		return self._html

	@property
	def top_uri(self):
		"""Top level URI for the file to be processed"""
		return self._top_uri

	@property
	def book(self):
		"""The book to be generated; an open :py:class:`zipfile.ZipFile` instance"""
		return self._book

	def process(self):
		"""
		Process the book, ie, extract whatever has to be extracted and produce the epub file
		"""
		pass

		# Create the wrapper around the parsed version. Initialization will also
		# retrieve the various 'meta' data from the document, like title, editors, document type, etc.
		# It is important to get these metadata before the real processing because, for example, the
		# 'short name' will also be used for the name of the final book
		#self._document_wrapper = DocumentWrapper(self)
	#
	# 	# The extra css file must be added to the book; the content is actually dependent on the type of the
	# 	# document
	# 	with zipfile.ZipFile(self.document_wrapper.short_name + '.epub', 'w', zipfile.ZIP_DEFLATED) as self._book:
	# 		# Initialize the book
	# 		self.book.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
	# 		self.book.writestr('META-INF/container.xml', meta_inf)
	#
	# 		# Add the book.css with the right value set for the background image
	# 		if self.document_wrapper.doc_type in CSS_LOGOS:
	# 			uri, local = CSS_LOGOS[self.document_wrapper.doc_type]
	# 			self.book.writestr('Assets/book.css', BOOK_CSS % local[7:])
	# 			_To_transfer.append((uri, local))
	#
	# 		# Some resources should be added to the book once and for all
	# 		for uri, local in _To_transfer:
	# 			local_session = HttpSession(uri)
	# 			local_session.store_in_book(self.book, local)
	#
	# 		# Massage the document by extracting extra resources, set the right CSS, etc
	# 		self.document_wrapper.process()
	#
	# 		# The main content should be stored in the target book
	# 		et_to_book(self.document, 'Overview.xhtml', self.book)
	#
	# 		Package(self).process()


class GenerateSpec:
	"""
	Create, if necessary, the final html document (ie, run the respec source through the spec generator); parse
	the final document to be used by the rest of the processing.

	(In other words, any reference to respec is hidden here; the rest of the modules and classes see only the
	final document to be put, eventually, into the Overview.xhtml file.)

	:param str top_uri: the URI that was used to invoke the package, ie, the location of the document source
	:param boolean is_respec: flag whether the source is a respec source (ie, has to be transformed through spec generator) or not
	"""
	def __init__(self, url, is_respec=True):
		# Construct the base URL; the query parameter and, possibly, the last portion of the path should be removed
		url_tuples = urlparse(url)
		base_path  = url_tuples.path if url_tuples.path[-1] == '/' else url_tuples.path.rsplit('/', 1)[0] + '/'
		self._base = urlunparse((url_tuples.scheme, url_tuples.netloc, base_path, "", "", ""))

		# Parse the document, possibly converting from respec on the fly
		self._get_document(CONVERTER + url if is_respec else url)

	@property
	def base(self):
		"""Base URL of the source; used to download other resources, if any, to be added to the book"""
		return self._base

	@property
	def document(self):
		""" Top level document DOM for the parsed input; an :py:class:`xml.etree.ElementTree.Element` instance"""
		return self._document

	@property
	def html(self):
		"""HTML element as parsed; :py:class:`xml.etree.ElementTree.ElementTree` instance"""
		return self._html

	def _get_document(self, url):
		def massage_html(html):
			# ugly hack: a space character is added to a <script> element with an external reference
			# this forces to generate a separate closing element rather than a self-closing one
			# this is needed for proper html interpretation
			for script in html.findall(".//script[@src]"):
				if script.text is None:
					script.text = " "

		session = HttpSession(url, raise_exception=True)
		# Parse the generated document
		self._html = html = html5lib.parse(session.data, namespaceHTMLElements=False)
		massage_html(html)
		self._document = ElementTree(html)


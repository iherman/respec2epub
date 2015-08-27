#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The real entry point to the package through the  :py:class:`DocWrapper` class below. Instance of that class controls the
necessary actions

* gets hold of the content, possibly converts the ReSpec source on the fly to HTML
* creates a :py:class:`.document.Document` class around the content that holds all the necessary metadata, and further references
* creates the book and, if required, the folder for the content
* collects all the dependencies from the Web, and copies them to the output
* collects all the auxiliary files (package file, etc) and copies them to the output


.. :class:: DocWrapper

Module content
--------------
"""

# noinspection PyPep8
# TODO: handle the possible css references to other css files or to images

# noinspection PyPep8Naming
import html5lib
from xml.etree.ElementTree import ElementTree
from urlparse import urlparse, urlunparse
import tempfile

from .templates import BOOK_CSS
from .document import Document
from .package import Package
import config

from .utils import HttpSession, Book

#: URI of the service used to convert a ReSpec source onto an HTML file on the fly. This service is used
#: by this script to process ReSpec sources before EPUB3 generation.
CONVERTER = "https://labs.w3.org/spec-generator/?type=respec&url="

# These are the items that have to be added to each file and package, no matter what: (id,file,media-type,properties)
# noinspection PyPep8
#
#  Items that have to be added to the book's manifest, no matter; tuples of the form (id,file,media-type,properties)
DEFAULT_FILES = [
		("nav.xhtml", "application/xhtml+xml", "nav", "nav"),
		("toc.ncx", "application/x-dtbncx+xml", "ncx", ""),
		("cover.xhtml", "application/xhtml+xml", "cover", ""),
		("Assets/w3c_main.png", "image/png", "w3c_main", ""),
		("Assets/base.css", "text/css", "StyleSheets-base", ""),
		("Assets/book.css", "text/css", "StyleSheets-book", "")
]

# noinspection PyPep8
# The pictures on the upper left hand side of the front page, denoting the document status, and also the path within
# the book.
CSS_LOGOS = {
	"REC"  : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-REC.png"),
	"NOTE" : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-NOTE.png"),
	"PER"  : ("http://www.w3.org/StyleSheets/TR/logo-PER.png", "Assets/logo-PR.png"),
	"PR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-PR.png"),
	"CR"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-CR.png"),
	"WD"   : ("http://www.w3.org/StyleSheets/TR/logo-CR.png", "Assets/logo-WD.png"),
	"ED"   : ("http://www.w3.org/StyleSheets/TR/logo-ED.png", "Assets/logo-ED.png"),
}


###################################################################################
# noinspection PyPep8
class DocWrapper:
	"""
	Top level entry class; receives the URI to be retrieved and generates the folders and the EPUB Package (as required)
	in the current directory (by default).


	:param str url: location of the document source
	:param boolean is_respec: flag whether the source is a respec source (ie, has to be transformed through spec generator) or not
	:param boolean package: whether a real zip file should be created or not
	:param boolean folder: whether the directory structure should be created separately or not
	:param boolean temporary: whether the zipped EPUB file should be put into a temporary filesystem location (used when the service is used through the Web)
	:param logger: a python logger (see the logging standard library module) to be used all around; initialized to None (for no logging)
	"""

	# noinspection PyPep8
	# Array of (url,local_name) pairs of resources that must be transferred and added to the output.
	# This is expanded run-time.
	To_transfer = [
		("http://www.w3.org/Icons/w3c_main.png", "Assets/w3c_main.png"),
		("http://www.w3.org/Icons/w3c_home.png", "Assets/w3c_home.png"),
		("http://www.w3.org/StyleSheets/TR/base.css", "Assets/base.css"),
	]

	# noinspection PyPep8
	def __init__(self, url, is_respec=False, package=True, folder=False, temporary=False, logger=None):
		self._html_document = None
		self._top_uri       = url
		self._book          = None
		self._domain        = urlparse(url).netloc
		self._package       = package
		self._folder        = folder

		if logger is not None:
			config.logger = logger
			message = "Handling the '%s' %s source" % (url, "ReSpec" if is_respec else "HTML")
			config.logger.info(message)

		# Get the base URL, ie, remove the possible query parameter and the last portion of the path name
		url_tuples = urlparse(url)
		base_path  = url_tuples.path if url_tuples.path[-1] == '/' else url_tuples.path.rsplit('/', 1)[0] + '/'
		self._base = urlunparse((url_tuples.scheme, url_tuples.netloc, base_path, "", "", ""))

		# Get the data, possibly converting from respec on the fly
		if config.logger is not None and is_respec:
			config.logger.info("Generating HTML via the spec generator service from %s" % url)
		session = HttpSession(CONVERTER + url if is_respec else url, raise_exception=True)

		# Parse the generated document
		self._html          = html5lib.parse(session.data, namespaceHTMLElements=False)
		self._html_document = ElementTree(self._html)

		# representation of the whole document, with the various metadata, etc.
		self._document = Document(self)

		# File name to be used for the final epub file
		if temporary:
			self._book_file_name = (tempfile.mkstemp(suffix='_' + self.document.short_name + '.epub'))[1]
		else:
			self._book_file_name = self.document.short_name + ".epub"

	@property
	def package(self):
		"""Flag whether an epub package is created"""
		return self._package

	@property
	def folder(self):
		"""Flag whether a folder, containing the package content, is created"""
		return self._folder

	@property
	def book_file_name(self):
		"""Name of the book; usually `shortname + .epub`, but can be a temporary file if so requested"""
		return self._book_file_name

	@property
	def base(self):
		"""Base URI for the document (used to retrieve additional resources, if needed)"""
		return self._base

	@property
	def domain(self):
		"""Domain of the original source"""
		return self._domain

	@property
	def html_document(self):
		"""Document, as parsed; an :py:class:`xml.etree.ElementTree.Element` instance"""
		return self._html_document

	@property
	def document(self):
		"""Wrapper around the document, containing extra meta information for packaging"""
		return self._document

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
		"""The book being generated; an open :py:class:`zipfile.ZipFile` instance"""
		return self._book

	def process(self):
		"""
		Process the book, ie, extract whatever has to be extracted and produce the epub file.

		:returns: the instance of the class itself
		"""
		# Create the wrapper around the parsed version. This will also
		# retrieve the various 'meta' data from the document, like title, editors, document type, etc.
		# It is important to get these metadata before the real processing because, for example, the
		# 'short name' will also be used for the name of the final book

		with Book(self.book_file_name, self.document.short_name, self.package, self.folder) as self._book:
			# Add the book.css with the right value set for the background image
			if self.document.doc_type in CSS_LOGOS:
				uri, local = CSS_LOGOS[self.document.doc_type]
				self.book.writestr('Assets/book.css', BOOK_CSS % local[7:])
				self.To_transfer.append((uri, local))

			# Some resources should be added to the book once and for all
			for uri, local in self.To_transfer:
				self.book.write_HTTP(local, uri)

			# Add the additional resources that are referred to from the document itself
			self.document.extract_external_references()

			# The various package files to be added to the final output
			Package(self).process()

			# The main content should be stored in the target book
			self.book.write_element('Overview.xhtml', self.html_document)

		return self

#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The entry point to the package is through the  :py:class:`DocWrapper` class below. An instance of that class controls the
necessary workflow for the EPUB generation, namely:

* gets hold of the content, possibly converts the ReSpec source on the fly to HTML
* creates a :py:class:`.document.Document` class around the content that holds all the necessary metadata and further references
* creates the book and, if required, the folder for the content
* collects all the dependencies from the Web, and copies them to the output
* creates all the auxiliary files (package file, navigation files, etc) and copies them to the output


.. :class:: DocWrapper

Module content
--------------
"""

# noinspection PyPep8

# noinspection PyPep8Naming
import html5lib
from xml.etree.ElementTree import ElementTree
from urlparse import urlparse, urlunparse
import tempfile

from .templates import BOOK_CSS, BOOK_CSS_EXTRAS
from .document import Document
from .package import Package
from .config import TO_TRANSFER
from .config import PADDING_NEW_STYLE, PADDING_OLD_STYLE
from .utils import HttpSession, Book, Logger
import utils


#: URI of the service used to convert a ReSpec source onto an HTML file on the fly. This service is used
#: by this script to convert ReSpec sources into HTML before EPUB3 generation.
CONVERTER = "https://labs.w3.org/spec-generator/?type=respec&url="


###################################################################################
# noinspection PyPep8
class DocWrapper(object):
	"""
    Top level entry class; receives the URI to be retrieved and generates the folders and/or the EPUB Package in the current directory (by default).

    :param str url: location of the document source
    :param boolean is_respec: flag whether the source is a ReSpec source (ie, has to be transformed through spec generator) or not
    :param boolean package: whether a real zip file (ie, the EPUB instance) should be created or not
    :param boolean folder: whether the directory structure should be created separately or not
    :param boolean temporary: whether the zipped EPUB file should be put into a temporary filesystem location (used when the service is used through the Web)
    :param logger: a python logger (see the standard library module on logging) to be used all around;  `None` means no logging
    """

	# noinspection PyPep8
	def __init__(self, url, is_respec=False, package=True, folder=False, temporary=False, logger=None):
		self._html_document = None
		self._top_uri       = url
		self._book          = None
		self._domain        = urlparse(url).netloc
		self._package       = package
		self._folder        = folder
		utils.logger 		= logger

		Logger.info("== Handling the '%s' %s source ==" % (url, "ReSpec" if is_respec else "HTML"))

		# Get the base URL, ie, remove the possible query parameter and the last portion of the path name
		url_tuples = urlparse(url)
		base_path  = url_tuples.path if url_tuples.path[-1] == '/' else url_tuples.path.rsplit('/', 1)[0] + '/'
		self._base = urlunparse((url_tuples.scheme, url_tuples.netloc, base_path, "", "", ""))

		# Get the possible re-write of the ReSpec config file; this will become important when the respec config
		# data is used
		self._url_respec_setting = {}
		if len(url_tuples.query) != 0:
			for setting in url_tuples.query.split(';'):
				to_set = setting.split('=')
				self._url_respec_setting[to_set[0]] = to_set[1]

		# Get the data, possibly converting from respec on the fly
		if is_respec:
			Logger.info("Generating HTML via the spec generator service from %s" % url)
		session = HttpSession(CONVERTER + url if is_respec else url, raise_exception=True, is_respec=is_respec)
		if is_respec:
			Logger.info("ReSpec generation successful, continuing with the result")

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
		"""Flag whether a folder, containing the package content, is created separately"""
		return self._folder

	@property
	def url_respec_setting(self):
		"""Possible ReSpec configuration setting via the query part of the URI of the document"""
		return self._url_respec_setting

	@property
	def book_file_name(self):
		"""Name of the book; usually `shortname + .epub`, but can be a temporary file if so requested (the term “shortname” is a W3C jargon…)"""
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
		"""HTML element as parsed; an :py:class:`xml.etree.ElementTree.ElementTree` instance"""
		return self._html

	@property
	def top_uri(self):
		"""Top level (absolute) URI for the file to be processed"""
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
			if self.document.css_tr_version == 2015:
				try:
					padding = PADDING_OLD_STYLE[self.document.doc_type]
				except KeyError:
					padding = PADDING_NEW_STYLE[2015]
			else:
				try:
					padding = PADDING_NEW_STYLE[self.document.css_tr_version]
				except KeyError:
					# fallback if there is a key error, ie, the padding has not yet been set for a possible new style
					padding = PADDING_NEW_STYLE[2016]

			# Additional CSS statements that has to be added to book.css, depending on the document's TR version
			if self.document.css_tr_version > 2015:
				try:
					css_extras = BOOK_CSS_EXTRAS[self.document.css_tr_version]
				except KeyError:
					css_extras = BOOK_CSS_EXTRAS[2016]
			else:
				css_extras = ""

			self.book.writestr('StyleSheets/TR/book.css', (BOOK_CSS % padding) + css_extras)

			# Some resources should be added to the in any case: icons, stylesheets for cover and nav pages,...
			for uri, local in TO_TRANSFER:
				self.book.write_HTTP(local, uri)

			# Add the additional resources that are referred to from the document itself
			self.document.extract_external_references()

			# Add the various additional media files (typically images), collected from CSS files
			for (local, uri) in self.document.css_references:
				session = utils.HttpSession(uri)
				if session.success:
					self.book.write_session(local, session, self.document.css_change_patterns)
					self.document.add_additional_resource(local, session.media_type)

			# The various EPUB specific package files to be added to the final output
			Package(self).process()

			# The main content should be stored in the target book
			self.book.write_element('Overview.xhtml', self.html_document)

		return self

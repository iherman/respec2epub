"""
:py:class:`Document` Class encapsulating the original source document, plus the various metadata that can and should be
extracted: short name, dated URI, editors, document type, etc. These data are extracted from the file,
usually trying to interpret the content of the file. The metadata also includes information on whether there
is scripting, whether it contains svg of MathML: these should be added to the book's package file.

The class instance collects the various external references that must be, eventually, added to the final book
(images, CSS files, etc.).

Finally, the HTML content (ie, the DOM tree) is also modified on the fly: HTML namespace is added, some metadata
is changed to fit the HTML5 requirements, link references may be updated for, e.g., CSS, etc.

.. :class::

Module content
--------------
"""


from urlparse import urlparse, urljoin
from xml.etree.ElementTree import SubElement
from .utils import HttpSession, Utils
from datetime import date
from . import R2EError
from .config import TO_TRANSFER
import config


# Pairs of element names and attributes for content that should be downloaded and referred to
# noinspection PyPep8
external_references = [
	("img", "src"),
	("img", "longdesc"),
	("script", "src"),
	("object", "data")
]


# Massage the core document
class Document:
	"""
	Encapsulation of the top level document.

	:param driver: the caller instance
	:type driver: :py:class:`.DocWrapper`
	"""

	# noinspection PyPep8,PyPep8
	def __init__(self, driver):
		self._additional_resources = []
		self._index                = 0
		self._driver               = driver
		self.download_targets      = []

		self._title      = None
		self._properties = None
		self._short_name = None
		self._doc_type   = None
		self._dated_uri  = None
		self._date       = None
		self._editors    = None
		self._toc		 = []
		self._issued_as  = None
		self._get_document_metadata()
		self._massage_html()

	@property
	def driver(self):
		"""The caller: a :py:class:`.doc2epub.DocToEpub` instance."""
		return self._driver

	@property
	def html(self):
		"""HTML element as parsed; an :py:class:`xml.etree.ElementTree.Element` instance  """
		return self._driver.html

	@property
	def additional_resources(self):
		"""List of additional resources that must be added to the book. A list of tuples, containing the internal
		reference to the resource and the media type. Built up during processing, it is used in when creating the manifest
		file of the book.
		"""
		return self._additional_resources

	# noinspection PyPep8
	def extract_external_references(self):
		"""Handle the external references (images, etc) in the core file, and copy them to the book. If the content referred to is

		- on the same domain as the original file
		- is one of the 'accepted' media types for epub

		then the file is copied and stored in the book, the reference is changed in the document,
		and the resource is marked to be added to the manifest file
		"""
		def final_target_media(f_session, f_target):
			if f_session.media_type == 'text/html':
				return 'application/xhtml+xml', f_target.replace('.html', '.xhtml', 1)
			else:
				return f_session.media_type, f_target

		# Retrieve the value of the reference. By making a urljoin, relative URI-s are also turned into absolute one;
		# this simplifies the issue
		# Look at generic external references like images, and, possibly copy the content
		for (element, attr) in self.download_targets:
			attr_value = element.get(attr)
			# The TO_TRANSFER array collects the 'system' references collected in Assets. Although some
			# earlier manipulation on the DOM may have already set the external references to those, the
			# HTTPSession is unnecessary (and sometimes leads to 404 anyway)
			# Bottom line: those references must be filtered out
			if attr_value is not None and all(map(lambda x: x[2] != attr_value, TO_TRANSFER)):
				ref = urljoin(self.driver.base, attr_value)
				if urlparse(ref).netloc == self.driver.domain:
					session = HttpSession(ref, check_media_type=True)
					if session.success:
						# Find the right name for the target document
						path = urlparse(ref).path
						if path[-1] == '/':
							target = 'Assets/extras/data%s.%s' % (self._index, config.ACCEPTED_MEDIA_TYPES[session.media_type])
							self._index += 1
						else:
							target = '%s' % path.split('/')[-1]

						# yet another complication: if the target is an html file, it will have to become xhtml :-(
						# this means that the target and the media types should receive a local name, to
						# be stored and used below

						final_media_type, final_target = final_target_media(session, target)

						# We can now copy the content into the final book.
						# Note that some of the media types are not to be compressed; this is taken care in the
						# "Book" instance
						self.driver.book.write_session(target, session)

						# Add information about the new entry; this has to be added to the manifest file
						self._additional_resources.append((final_target, final_media_type))

						# Change the original reference
						element.set(attr, final_target)
					else:
						# That resource is not available
						# Typical situation where it happens: the document is generated from respec
						# on the fly but from a place where the diff file is not yet
						# generated (but referenced from content)
						# Take out those situations that are under the control of this script
						if not element.get(attr).startswith("Assets/"):
							element.attrib.pop(attr)
							if config.logger is not None:
								config.logger.warning("Link to '%s' removed (non-existing local resource or of non acceptable type)" % ref)

	###################################################################################################
	# noinspection PyPep8
	def _massage_html(self):
		"""
		Process a document looking for (and possibly copying) external references and making some modifications on the fly
		"""
		# Do the necessary massaging on the DOM tree to make the XHTML output o.k.
		Utils.html_to_xhtml(self.html)

		# Change the value of @about to the dated URI, which is what counts...
		self.html.set("about", self.dated_uri)

		# The reference to the W3C logo should be localized
		for img in self.html.findall(".//img[@alt='W3C']"):
			img.set('src', 'Assets/w3c_home.png')
			break

		# handle stylesheet references
		for lnk in self.html.findall(".//link[@rel='stylesheet']"):
			ref_details = urlparse(lnk.get("href"))
			if ref_details.netloc == "www.w3.org" and ref_details.path.startswith("/StyleSheets"):
				# This is the local, W3C, style sheet. Actions to be taken:
				# 1. This is exchanged against the general 'base.css'
				# 2. Below, after all the stylesheets are handled, the reference to a separate 'book.css' is added
				# 3. The final book.css is finalized later (through a template and in the "driver"), adding a reference
				# to the background image that corresponds to the documents status
				lnk.set("href", "Assets/base.css")
			else:
				self.download_targets.append((lnk, 'href'))

		head = self.html.find(".//head")
		book_css = SubElement(head, "link")
		book_css.set("rel", "stylesheet")
		book_css.set("href", "Assets/book.css")

		# This is an ugly issue which comes up very very rarely: the base element screws up things
		for element in self.html.findall(".//base"):
			head.remove(element)

		# Change the HTTP equivalent value
		Utils.set_html_meta(self.html, head)

		# change the DOM
		Utils.change_DOM(self.html)

		# Collect the additional download targets
		for (tag_name, attr) in external_references:
			for element in self.html.findall(".//%s" % tag_name):
				self.download_targets.append((element, attr))

		# Extra care should be taken with <a> elements to exclude self references (ie, fragment id-s)
		for element in self.html.findall(".//a[@href]"):
			ref = element.get("href")
			if ref is not None and len(ref) != 0 and ref[0] != '#' and ref != ".":
				self.download_targets.append((element, 'href'))

	###################################################################################################
	# Metadata; all these are filled with value through the _get_document_metadata method, called at
	# initialization time
	@property
	def title(self):
		"""The ``title`` element content."""
		return self._title

	@property
	def properties(self):
		"""The properties of the document, to be added to the manifest entry"""
		return self._properties

	@property
	def short_name(self):
		"""'Short Name', in the W3C jargon"""
		return self._short_name

	@property
	def dated_uri(self):
		"""'Dated URI', in the W3C jargon"""
		return self._dated_uri

	@property
	def doc_type(self):
		"""Document type, ie, one of ``REC``, ``NOTE``, ``PR``, ``PER``, ``CR``, ``WD``, or ``ED``"""
		return self._doc_type

	@property
	def date(self):
		"""Date of publication"""
		return self._date

	@property
	def editors(self):
		"""List of editors (as a string)"""
		return self._editors

	@property
	def toc(self):
		"""Table of content, an array of ``TOC_Item`` objects"""
		return self._toc

	@property
	def issued_as(self):
		""" "W3C Note/Recommendation/Draft/ etc.": the text to be reused as a subtitle on the cover page. """
		return self._issued_as

	def _get_document_metadata(self):
		"""
		Extract metadata from the source, stored as attribute for this class (date, title, editors, etc.)

		:raises R2EError: if the content is not recognized as one of the W3C document types (WD, ED, CR, PR, PER, REC, Note, or ED)
		"""
		# Get the title of the document
		for title_element in self.html.findall(".//title"):
			self._title = ""
			for t in title_element.itertext():
				self._title += t
			break

		# Properties, to be added to the manifest
		props = Utils.get_document_properties(self.html)
		props.add("remote-resources")
		if len(props) > 0:
			self._properties = reduce(lambda x, y: x + ' ' + y, props)

		# Short name of the document
		# Find the official short name of the document
		for aref in self.html.findall(".//a[@class='u-url']"):
			try:
				self._dated_uri = aref.get('href')
				dated_name = self._dated_uri[:-1] if self._dated_uri[-1] == '/' else self._dated_uri
				self._doc_type, self._short_name = Utils.create_shortname(dated_name.split('/')[-1])
			except:
				message = "Could not establish document type and/or short name from '%s'" % self._dated_uri
				if config.logger is not None:
					config.logger.error(message)
				raise R2EError(message)
			break

		# Date of the document, to be reused in the metadata
		if self._doc_type is None:
			message = "Unrecognized document type, unable to convert (should be ED, WD, CR, PR, PER, REC, or NOTE)"
			if config.logger is not None:
				config.logger.error(message)
			raise R2EError(message)
		elif self._doc_type == "ED":
			self._date = date.today()
		else:
			self._date = Utils.retrieve_date(self.dated_uri)

		# Extract the editors
		editor_set = Utils.extract_editors(self.html)
		if len(editor_set) == 0:
			self._editors = []
		elif len(editor_set) == 1:
			self._editors = list(editor_set)[0] + ", (ed.)"
		else:
			self._editors = reduce(lambda x, y: x + ', ' + y, editor_set) + ", (eds.)"

		# Extract the table of content
		self._toc = Utils.extract_toc(self.html, self.short_name)

		# Add the right subtitle to the cover page
		for issued in self.html.findall(".//h2[@property='dcterms:issued']"):
			self._issued_as = ""
			for t in issued.itertext():
				self._issued_as += t



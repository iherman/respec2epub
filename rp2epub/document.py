from urlparse import urlparse, urljoin
from xml.etree.ElementTree import SubElement

from .utils import HttpSession, Utils

# suffixes and media types for resources that are recognized by EPUB
# noinspection PyPep8,PyPep8
extra_media_types = {
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


# Massage the core document
class DocumentWrapper:
	"""
	Manage the top level document, ie, looking at its content and retrieve the necessary references like images
	or style files, possibly modifying the document on the fly.

	:param driver: the caller instance
	:type driver: :py:class:`.DocToEpub`
	"""
	# noinspection PyPep8,PyPep8
	def __init__(self, driver):
		self._additional_resources = []
		self._index = 0
		self._driver = driver

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

	@property
	def driver(self):
		"""The caller: a :class:`.DocToEpub` instance.  """
		return self._driver

	@property
	def html(self):
		"""HTML element as parsed; an :py:class:`xml.etree.ElementTree.Element` instance  """
		return self._driver.html

	@property
	def additional_resources(self):
		"""List of additional resources that have been added to the book. A list of tuples, containing the internal
		reference to the resource and the media type. Built up during processing, it is used in the manifest
		file of the book
		"""
		return self._additional_resources

	###################################################################################################
	# noinspection PyPep8
	def process(self):
		"""
		Process a document looking for (and possibly copying) external references and making some modifications on the fly
		"""
		# Set the xhtml namespace on the top, this is required by epub readers
		self.html.set("xmlns", "http://www.w3.org/1999/xhtml")

		# The script element should not be self-closed, but with a separate </script> instead. Just adding
		# an extra space to a possible link does the trick.
		for script in self.html.findall(".//script[@src]"):
			if script.text is None:
				script.text = " "

		# Change the value of @about to the dated URI, which is what counts...
		self.html.set("about", self.dated_uri)

		# handle stylesheet references
		for lnk in self.html.findall(".//link[@rel='stylesheet']"):
			ref_details = urlparse(lnk.get("href"))
			if ref_details.netloc == "www.w3.org" and ref_details.path.startswith("/StyleSheets"):
				# This is the local, W3C, style sheet. Two actions:
				# 1. This is exchanged against the general 'base.css'
				# 2. Below, after all the stylesheets are handled, the reference to a separate 'book.css' is added
				# 3. The final book.css is finalized later (through a template), adding a reference to the background
				# image that corresponds to the documents status
				lnk.set("href", "Assets/base.css")
			else:
				self._handle_one_reference(lnk, 'href')

		head     = self.html.findall(".//head")[0]
		book_css = SubElement(head, "link")
		book_css.set("rel", "stylesheet")
		book_css.set("href", "Assets/book.css")

		# This is an ugly issue which comes up very very rarely: the base element screws up things if any
		for element in self.html.findall(".//base"):
			head.remove(element)

		# Change the HTTP equivalent value
		#
		#
		Utils.set_html_meta(self.html, head)

		# The easy case: look at generic external references, possibly copy the content
		for (element, attr) in [("img", "src"), ("script", "src"), ("object", "data")]:
			for el in self.html.findall(".//%s" % element):
				self._handle_one_reference(el, attr)

	# noinspection PyPep8
	def _handle_one_reference(self, element, attr):
		"""Handle one reference in the core HTML file.
		If the file referred to is
		- on the same domain as the original file
		- is one of the 'accepted' media types for epub
		Then the file is copied and stored in the book, the reference is changed in the document,
		and the resource is marked to be added to the manifest file

		:param element: the (XML) element that holds the reference in an attribute
		:type element: :py:class:`xml.etree.ElementTree.Element`
		:param str attr: the attribute name that holds the reference
		"""
		# Retrieve the value of the reference. By making a urljoin, relative URI-s are also turned into absolute one;
		# this simplifies the issue
		ref = urljoin(self.driver.top_uri, element.get(attr))

		if urlparse(ref).netloc == self.driver.domain:
			session = HttpSession(ref, accepted_media_types=extra_media_types.keys())
			if not session.success:
				return

			# Find the right name for the target document
			path = urlparse(ref).path
			if path[-1] == '/':
				target = 'Assets/extras/data%s.%s' % (self._index, extra_media_types[session.media_type])
				self._index += 1
			else:
				target = '%s' % path.split('/')[-1]

			# We can now copy the content into the final book.
			# Note that some of the media types are not to be compressed
			# TODO: This has to be finalized, skipping the copy for now
			#session.store_in_book(self.driver.book, target)

			# Add information about the new entry; this has to be added to the manifest file
			self._additional_resources.append((target, session.media_type))

			# Change the original reference
			element.set(attr, target)
		else:
			# return unchanged
			return

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
		"""Document type, ie, one of ``REC``, ``NOTE``, ``PR``, ``PER``, ``CR``, ``WD``"""
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
		# Get the title of the document
		for title_element in self.html.findall(".//title"):
			self._title = ""
			for t in title_element.itertext():
				self._title += t
			break

		# Properties, to be added to the manifest
		props = set()
		props.add("remote-resources")
		Utils.get_document_properties(self.html, props)
		if len(props) > 0:
			self._properties = reduce(lambda x, y: x + ' ' + y, props)

		# Short name of the document
		# Find the official short name of the document
		for aref in self.html.findall(".//a[@class='u-url']"):
			self._dated_uri = aref.get('href')
			dated_name = self._dated_uri[:-1] if self._dated_uri[-1] == '/' else self._dated_uri
			self._doc_type, self._short_name = Utils.create_shortname(dated_name.split('/')[-1])
			break

		# Date of the document, to be reused in the metadata
		self._date = Utils.retrieve_date(self.dated_uri)

		# Extract the editors
		editor_array = set()
		Utils.extract_editors(self.html, editor_array, self.short_name)
		if len(editor_array) == 0:
			self._editors = []
		elif len(editor_array) == 1:
			self._editors = list(editor_array)[0] + ", (ed.)"
		else:
			self._editors = reduce(lambda x, y: x + ', ' + y, editor_array) + ", (eds.)"

		# Extract the table of content
		Utils.extract_toc(self.html, self._toc, self.short_name)

		# Add the right subtitle to the cover page
		for issued in self.html.findall(".//h2[@property='dcterms:issued']"):
			self._issued_as = ""
			for t in issued.itertext():
				self._issued_as += t



"""
The :py:class:`Document` Class encapsulates the original source document, plus the various metadata that can and should be
extracted: short name, dated URI, editors, document type, etc. These data are extracted from the file,
usually trying to interpret the content of the file as well as the referenced CSS files. The metadata also includes information on whether there
is scripting, whether it contains svg or MathML: these should be added to the book's package file (per the specification of EPUB).

The class instance collects the various external references that must be, eventually, added to the final book
(images, CSS files, etc.).

Finally, the HTML content (ie, the DOM tree) is also modified on the fly: HTML namespace is added, some metadata
is changed a bit to fit the HTML5 requirements, the HTML is output in XHTML, etc.

The class is invoked (and "controlled") by a `:py:class:`.DocWrapper` instance.

.. :class::

Module content
--------------
"""


from urlparse import urlparse, urljoin
import json
import sys
import traceback
from xml.etree.ElementTree import SubElement
from StringIO import StringIO
from datetime import date, datetime

from .utils import HttpSession, Utils, Logger
from .cssurls import CSSList
from .config import TO_TRANSFER
import config


# Massage the core document
class Document(object):
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
		self._download_targets     = []

		self._title          = None
		self._properties     = None
		self._short_name     = None
		self._doc_type       = "base"
		self._dated_uri      = None
		self._date           = None
		# TODO: default should be arrays, not strings
		self._editors        = []
		self._authors        = []
		self._respec_config  = None
		self._toc		     = []
		self._nav_toc	     = []
		self._css_tr_version = 2015
		self._subtitle       = None
		self._get_document_metadata()

		css_list = self._collect_downloads()
		self._css_references       = css_list.get_download_list()
		self._css_change_patterns  = css_list.change_patterns


	@property
	def download_targets(self):
		"""Array of resources to be downloaded and added to the final book. Entries of the array are (:py:class:`xml.etree.ElementTree.Element`, attribute) pairs, referring to the element and the attribute that identifies the URL of the resources to be downloaded."""
		return self._download_targets

	@property
	def driver(self):
		"""The caller: a :py:class:`.doc2epub.DocToEpub` instance."""
		return self._driver

	@property
	def html(self):
		"""The parsed version of the top level HTML element; an :py:class:`xml.etree.ElementTree.Element` instance  """
		return self._driver.html

	@property
	def additional_resources(self):
		"""List of additional resources that must be added to the book eventually. A list of tuples, containing the internal
		reference to the resource and the media type. Built up during processing, it is used in when creating the manifest
		file of the book.
		"""
		return self._additional_resources

	def add_additional_resource(self, local_name, media_type):
		"""Add a pair of local name and media type to the list of additional resources. Appends to the :py:attr:`additional_resources` list.
		:param local_name: name of the resource within the final book
		:param media_type: media type (used when the resource is added to the package file)
		"""
		self._additional_resources.append((local_name, media_type))

	@property
	def css_references(self):
		"""Set of `(local_name, absolute_url)` pairs for resources gathered recursively from CSS files. These
		are CSS files themselves, or other media like logos, background images, etc, referred to via a `url` statement
		in CSS.
		"""
		return self._css_references

	@property
	def css_change_patterns(self):
		"""List if `(from, to)` pairs that must be used to replace strings in the CSS files on the fly. Typically
		used to adjust the values used in `url` statements.
		"""
		return self._css_change_patterns

	# noinspection PyPep8
	def extract_external_references(self):
		"""Handle the external references (images, etc) in the core file, and copy them to the book. If the content referred to is

		- has a URL is a relative one, begins with the same base, or refers to the `www.w3.org` domain (the latter is for official CSS files and logos)
		- is one of the 'accepted' media types for epub

		then the file is copied and stored in the book, the reference is changed in the document,
		and the resource is marked to be added to the manifest file. HTML files are copied as XHTML files, with a ``.xhtml`` suffix.
		"""

		def final_target_media(f_session, f_target):
			if f_session.media_type == 'text/html':
				return 'application/xhtml+xml', f_target.replace('.html', '.xhtml', 1)
			else:
				return f_session.media_type, f_target

		# Retrieve the value of the reference. By making a urljoin, relative URI-s are also turned into absolute one;
		# this simplifies the issue
		# Look at generic external references like images, and, possibly copy the content
		for (element, attr) in self._download_targets:
			attr_value = element.get(attr)
			# The TO_TRANSFER array collects the 'system' references collected in Assets. Although some
			# earlier manipulation on the DOM may have already set the external references to those, the
			# HTTPSession is unnecessary (and sometimes leads to 404 anyway)
			# Bottom line: those references must be filtered out
			if attr_value is not None and all(map(lambda x: x[1] != attr_value, TO_TRANSFER)):
				# Remove the possible fragment ID. This may happen if the document refers to a fragment of another
				# file locally, for example; that should not be relevant for what follows
				attr_value = attr_value.split('#')[0]

				# The following artifact is necessary to treat the WWW level, official URIs and local ones
				ref = urljoin(self.driver.base, attr_value)

				# In some cases, primarily in the case of editors' drafts, the reference is simply on the file
				# itself; that should be forgotten
				if ref == self.driver.top_uri or ref == self.driver.base:
					continue

				parsed_ref = urlparse(ref)
				# Genuine local, relative URI
				local = True if ref.startswith(self.driver.base) else False
				# Official WWW URI-s, mainly for style sheets or possibly javascript
				www_level = True if parsed_ref.netloc == "www.w3.org" else False
				if local or www_level:
					session = HttpSession(ref, check_media_type=True)
					if session.success:
						# Find/set the right name for the target document
						path = parsed_ref.path
						if path[-1] == '/':
							# This should not really happen, but may: relying on some WWW mechanism that we cannot
							# rely on in a a book
							target = 'Assets/extras/data%s.%s' % (self._index, config.ACCEPTED_MEDIA_TYPES[session.media_type])
							self._index += 1
						elif www_level:
							# This is, mainly, for official CSS files as well as W3C logos/icons; reproducing the same path as for W3C
							target = path if path[0] != '/' else path[1:]
						elif local:
							# This is for local references, reproducing the same path as in the origin
							# Removing a possible, though erroneous, first character, just to be on the safe side
							target = attr_value if attr_value[0] != '/' else attr_value[1:]
						else:
							# In fact, this should not happen...
							target = attr_value.split('/')[-1]

						# other complication: if the target is an html file, it will have to become xhtml :-(
						# this means that the target and the media types should receive a local name, to
						# be stored and used below
						final_media_type, final_target = final_target_media(session, target)

						# We can now copy the content into the final book.
						# Note that some of the media types are not to be compressed; this is taken care in the
						# "Book" instance
						self.driver.book.write_session(target, session, self.css_change_patterns)

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
							element.tag = "span"
							element.attrib.pop(attr)
							if element.get("rel") is not None:
								element.attrib.pop("rel")
							Logger.warning("Link to '%s' removed (non-existing local resource or of non acceptable type)" % ref)

	###################################################################################################
	# noinspection PyPep8
	def _collect_downloads(self):
		"""
		Process a document looking for (and possibly copying) external references and making some minor
		modifications on the fly. ``(Element, attribute)`` pairs are added on the fly to the internal array of downloads
		(see :py:attr:`download_targets`).

		:returns: a :py:class:`.cssurls.CSSList` instance, with all the CSS references
		"""
		# To collect the CSS references and data
		css_list = CSSList(self.driver.base)

		# Do the necessary massaging on the DOM tree to make the XHTML output o.k.
		Utils.html_to_xhtml(self.html)

		# Change the value of @about to the dated URI, which is what counts...
		self.html.set("about", self.dated_uri)

		# handle stylesheet references
		for lnk in self.html.findall(".//link[@rel='stylesheet']"):
			ref = lnk.get("href")
			if urlparse(ref).netloc == "www.w3.org":
				if not ref.endswith(".css"):
					lnk.set("href",ref + ".css")
			self._download_targets.append((lnk, 'href'))
			# The CSS reference should be stored as a possible source of further references
			css_list.add_css(lnk.get("href"))

		# Handle built-in style sheet statements; this should be added to the CSS handler, too
		for style in self.html.findall(".//style"):
			# there may be cases, though not probable, that that the type attribute is set to something different
			# then text/css
			if style.get("type") is not None and style.get("type") != "text/css":
				continue
			content = " ".join([k.strip() for k in style.itertext()]).strip()
			css_list.add_css(self.driver.base, is_file=False, content=content)

		head = self.html.find(".//head")
		book_css = SubElement(head, "link")
		book_css.set("rel", "stylesheet")
		book_css.set("href", "StyleSheets/TR/book.css")

		# This is an ugly issue which comes up very very rarely: the base element screws up things
		for element in self.html.findall(".//base"):
			head.remove(element)

		# Change the HTTP equivalent value
		Utils.set_html_meta(self.html, head)

		# change the DOM
		Utils.change_DOM(self.html)

		# Collect the additional download targets
		for (tag_name, attr) in config.EXTERNAL_REFERENCES:
			for element in self.html.findall(".//%s" % tag_name):
				self._download_targets.append((element, attr))

		# Extra care should be taken with <a> elements: only local, relative URI-s should be considered,
		# excluding the pure fragment id. Ie, it should refer to another file in the local package.
		# As a pathological case, the href == "." should also be excluded to avoid self-reference
		for element in self.html.findall(".//a[@href]"):
			ref  = element.get("href")
			pref = urlparse(ref)
			if len(pref.netloc) == 0 and len(pref.scheme) == 0 and len(pref.path) != 0 and ref != ".":
				self._download_targets.append((element, 'href'))

		return css_list

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
	def respec_config(self):
		"""The full respec configuration as a Python mapping type. This is available for newer releases
		of ReSpec, but not in older. And, of course, not available for Bikeshed sources. The value is None
		if was not made available.

		Note that the rest of the code retrieves some of the common properties (e.g., short_name), i.e.,
		the rest of the code does not make use of this property. But it may be used in the future.
		"""
		return self._respec_config

	@property
	def short_name(self):
		"""'Short Name', in W3C jargon"""
		return self._short_name if self._short_name is not None else "index"

	@property
	def dated_uri(self):
		"""'Dated URI', in the W3C jargon. As a fallback, this may be set to the top URI of the document if the
		dated uri has not been set """
		return self._dated_uri if self._dated_uri is not None else self.driver.top_uri

	@property
	def doc_type(self):
		"""Document type, eg, one of ``REC``, ``NOTE``, ``PR``, ``PER``, ``CR``, ``WD``, or ``ED``, or the values set in ReSpec"""
		return self._doc_type

	@property
	def doc_type_info(self):
		"""Structure reflecting the various aspects of documents by doc type. This is just a shorthand for
		``config.DOCTYPE_INFO[self.doc_type]``
		"""
		return config.DOCTYPE_INFO[self.doc_type] if self.doc_type is not None else None

	@property
	def date(self):
		"""Date of publication"""
		return self._date

	@property
	def editors(self):
		"""List of editors (name + affiliation per element)"""
		return self._editors

	@property
	def authors(self):
		"""List of authors (name + affiliation per element)"""
		return self._authors

	@property
	def toc(self):
		"""Table of content, an array of :py:class:`.utils.TOC_Item` instances. It is only the top level TOC structures;
		used for the old-school TOC file as well as for the EPUB3 navigation document in case the
		original document does not have the appropriate structures in its TOC."""
		return self._toc

	@property
	def nav_toc(self):
		"""Table of content extracted from a ``<nav>`` element (if any), that is copied almost verbatim into the
		EPUB3 navigation document. It may be empty, though, because the source does not contain the required TOC
		structure, in which case the simple TOC structure is (see :py:attr:`toc`)."""
		return self._nav_toc

	@property
	def css_tr_version(self):
		"""Version (as an integer number denoting the year) of the CSS TR version. The value is 2015 or higher"""
		return self._css_tr_version

	@property
	def subtitle(self):
		""" "W3C Note/Recommendation/Draft/ etc.": the text to be reused as a subtitle on the cover page. """
		return self._subtitle

	# noinspection PyPep8
	def _get_metadata_from_respec(self, dict_config):
		"""
		Extract metadata (date, title, editors, etc.) making use of the stored ReSpec configuration structure (this
		structure includes the data set by the user plus some data added by the ReSpec process itself).

		:returns: True or False, depending on whether the right keys are available or not
		"""
		def _get_people(key):
			def _get_person(person_struct):
				retval = person_struct["name"]
				return retval + (", %s" % person_struct["company"]) if "company" in person_struct else retval

			return [_get_person(p) for p in dict_config[key]]

		# store the full configuration for possible later reuse
		self._respec_config = dict_config

		if "specStatus" in dict_config :
			self._doc_type   = dict_config["specStatus"]
			self._short_name = dict_config["shortName"] if "shortName" in dict_config else None
			self._editors    = [] if "editors" not in dict_config else _get_people("editors")
			self._authors    = [] if "authors" not in dict_config else _get_people("authors")
			if "publishDate" in dict_config:
				self._date = datetime.strptime(dict_config["publishDate"], "%Y-%m-%d").date()
			else:
				self._date = date.today()

			aref = self.html.find(".//a[@class='u-url']")
			if aref is not None:
				self._dated_uri = aref.get('href')
			return True
		else:
			Logger.warning("Spec Status is not in the ReSpec config; falling back to generated content for metadata")
			return False

	# noinspection PyBroadException
	def _get_metadata_from_source(self):
		"""
		Extract metadata (date, title, editors, etc.) 'scraping' the source, i.e., by
		extracting the data based on class names, URI patterns, etc.

		:raises R2EError: if the content is not recognized as one of the W3C document types (WD, ED, CR, PR, PER, REC, Note, or ED)
		"""
		# Short name of the document
		# Find the official short name of the document
		for aref in self.html.findall(".//a[@class='u-url']"):
			self._dated_uri = aref.get('href')
			dated_name = self._dated_uri[:-1] if self._dated_uri[-1] == '/' else self._dated_uri
			self._doc_type, self._short_name = Utils.create_shortname(dated_name.split('/')[-1])
			break

		self._date = Utils.retrieve_date(self.dated_uri)

		# Extract the editors
		self._editors = Utils.extract_editors(self.html)

		# Add the right subtitle to the cover page
		for issued in self.html.findall(".//h2[@property='dcterms:issued']"):
			self._subtitle = ""
			for t in issued.itertext():
				self._subtitle += t

	# noinspection PyPep8Naming
	def _get_CSS_TR_version(self):
		"""
		Set the CSS TR version based on the document.
		Note: at the moment this is very ugly: the path of the CSS URL is checked for a date. Hopefully, there will
		be some more 'standard' way of doing this, eventually.
		"""
		self._css_tr_version = 2015

		for lnk in self.html.findall(".//link[@rel='stylesheet']"):
			ref_details = urlparse(lnk.get("href"))
			# TODO: THIS IS TEMPORARY, SHOULD BE FIXED WHEN THINGS BECOME FINAL!!!!
			if ref_details.netloc == "www.w3.org" and "2016" in ref_details.path:
				self._css_tr_version = 2016
				return
		return

	def _get_document_metadata(self):
		"""
		Extract metadata (date, title, editors, etc.)
		"""
		# noinspection PyBroadException
		def _retrieve_from_respec_config():
			"""
			:return: True or False, depending on whether the metadata could be extracted via the respec config or not
			"""
			head = self.html.find(".//head")
			respec_config_element = head.find(".//script[@id='initialUserConfig']")
			if respec_config_element is not None:
				try:
					respec_config = json.loads(" ".join([j for j in respec_config_element.itertext()]))
					# The respec config extracted from the file may have been overwritten on the URL
					for key in self.driver.url_respec_setting:
						respec_config[key] = self.driver.url_respec_setting[key]
				except:
					# The error message of the parse does not seem to be all to useful:-(
					# Logger.warning("Embedded ReSpec Configuration could not be parsed as JSON\n%s" % err.getvalue())
					# exc_type, exc_value, exc_traceback = sys.exc_info()
					# err = StringIO()
					# traceback.print_exception(exc_type, exc_value, exc_traceback, file=err)
					# err.close()
					# Logger.warning("Falling back to generated content for metadata")
					Logger.warning("Embedded ReSpec Configuration could not be parsed as JSON; Falling back to generated content for metadata")
					return False

				try:
					if self._get_metadata_from_respec(respec_config):
						head.remove(respec_config_element)
						Logger.info("Using the embedded ReSpec Configuration")
						return True
					else:
						return False
				except:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					err = StringIO()
					traceback.print_exception(exc_type, exc_value, exc_traceback, file=err)
					Logger.warning("Embedded ReSpec Configuration couldn't be handled due to an error \n%s" % err.getvalue())
					Logger.warning("Falling back to generated content for metadata")
					err.close()
					return False
			else:
				Logger.warning("No embedded ReSpec configuration; falling back to generated content for metadata")
				return False

		# Get the title of the document
		for title_element in self.html.findall(".//title"):
			self._title = ""
			for t in title_element.itertext():
				self._title += t
			break

		# Get the CSS version of the document
		self._get_CSS_TR_version()

		# Properties to be added to the manifest
		props = Utils.get_document_properties(self.html)
		props.add("remote-resources")
		if len(props) > 0:
			self._properties = reduce(lambda x, y: x + ' ' + y, props)

		# see if the embedded config is in the file, if so, retrieve it in the form of a directory, and then
		# remove the script from the DOM tree not to pollute the output unnecessarily
		if _retrieve_from_respec_config() is not True:
			self._get_metadata_from_source()

		# Get the 'issued_as' text that will be used as a subtitle
		self._subtitle = config.DOCTYPE_INFO[self._doc_type]["subtitle"] if self._doc_type in config.DOCTYPE_INFO else ""
		self._subtitle += ", " + self.date.strftime("%d %B, %Y")

		# Extract the table of content
		(self._toc, self._nav_toc) = Utils.extract_toc(self.html, self.short_name)



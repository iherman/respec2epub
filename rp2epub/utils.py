# -*- coding: utf-8 -*-
"""
Various utility classes and methods.


Module Content
--------------

"""

from urllib2 import urlopen
from StringIO import StringIO
from datetime import date
import re
import os
import os.path
import shutil
from xml.etree.ElementTree import SubElement, ElementTree
import zipfile
import html5lib
from .templates import meta_inf
from . import R2EError
import config

# These media types should be added to the zip file uncompressed
# noinspection PyPep8
_NO_COMPRESS = [
	"image/png",
	"image/jpeg",
	"image/gif",
	"audio/mpeg",
	"video/mp4",
	"video/webm",
	"video/ogg"
]

########################################## Table of content extraction ########################################
short_label_pattern = re.compile("^[1-9][0-9]*\. .*$")

# list of element pairs that lead to a table of content
# noinspection PyPep8
# structures for TOC elements in ReSpec or Bikeshed: element hierarchy and, if not None,
# the class name for the <li> element.
TOC_PAIRS = [
	("div[@id='toc']", "ul[@class='toc']", None),
	("div[@id='toc']", "ol[@class='toc']", None),
	("section[@id='toc']", "ul[@class='toc']", None),
	("section[@id='toc']", "ol[@class='toc']", None),
	("div[@class='toc']", "ul[@class='toc']", "tocline1"),
	("div[@data-fill-with='table-of-contents']", "ul[@class='toc']", None),
	("body", "ul[@class='toc']", None),
	("body", "ol[@class='toc']", None)
]


# noinspection PyPep8Naming
class TOC_Item(object):
	"""
	A single Table of Content (TOC) item.

	:param str href: reference in the TOC
	:param str label: long label, ie, including the chapter numbering
	:param str short_label: shotr label, ie, *without* the chapter numbering
	"""
	# noinspection PyPep8
	def __init__(self, href, label, short_label):
		self._href        = href
		self._label       = label
		self._short_label = short_label

	@property
	def href(self):
		return self._href

	@property
	def label(self):
		return self._label

	@property
	def short_label(self):
		return self._short_label


##################################################################################

class Utils(object):
	"""
	Generic utility functions to extract information from a W3C TR document.
	"""
	# noinspection PyUnusedLocal,PyPep8
	@staticmethod
	def get_document_properties(html):
		"""
			Find the extra manifest properties that must be added to the HTML resource in the opf file.

			See the `IDPF documentation <http://www.idpf.org/epub/30/spec/epub30-publications.html#sec-item-property-values>`_ for details

			:param html: the object for the whole document
			:type html: :py:class:`xml.etree.ElementTree.ElementTree`
			:return: set collecting all possible property values
			:rtype: set

		"""
		retval = set()
		# If <script> is used for Javascript, the 'scripted' property should be set
		for scr in html.findall(".//script"):
			if "type" not in scr.keys() or scr.get("type") == "application/javascript" or scr.get("type") == "text/javascript":
				# The script element is really used for scripting
				retval.add("scripted")
				# No reason to look further
				break

		# If an interactive form is used, the 'scripted' property should be set
		if html.find(".//form") is not None:
			retval.add("scripted")

		if html.find(".//{http://www.w3.org/2000/svg}svg") is not None:
			retval.add("svg")

		if html.find(".//{http://www.w3.org/1998/Math/MathML}math") is not None:
			retval.add("mathml")

		return retval
	# end _get_extra_properties

	# noinspection PyPep8
	@staticmethod
	def create_shortname(name):
		"""
		Create the short name, in W3C jargon, based on the dated name. Returns a tuple with the category of the
		publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, ``ED``, "RSCND", or ``PER``), and the short name itself.

		:param str name: dated name
		:return: tuple of with the category of the publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, ``ED``, "RSCND", or ``PER``), and the short name itself.
		:rtype: tuple
		"""
		# This is very W3C specific...
		for doc_type in config.DOCTYPE_INFO:
			doc_info = config.DOCTYPE_INFO[doc_type]
			if doc_info["uri_prefix"] is not None and name.startswith(doc_info["uri_prefix"] + "-"):
				name = name[len(doc_type)+1:]
				return doc_type, name[:-9]

		# If we get here, the name does not abide to any pattern; it is taken to be an ED
		return "base", name
	# end create_shortname

	@staticmethod
	def retrieve_date(duri):
		"""
		Retrieve the (publication) date from the dated URI.

		:param str duri: dated URI
		:return: date
		:rtype: :py:class:`datetype.date`
		:raises R2EError: the dated URI is not of an expected format
		"""
		# remove the last '/' if any
		try:
			d = duri[:-1] if duri[-1] == '/' else duri
			# Date in compact format:
			pdate = d[-8:]
			return date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))
		except:
			message = "dated URI is not of the expected format"
			if config.logger is not None:
				config.logger.error(message)
			raise R2EError(message)
	# end retrieve_date

	@staticmethod
	# noinspection PyBroadException
	def extract_editors(html):
		"""Extract the editors' names from a document, following the respec conventions
		(``@class=p-author`` for ``<dd>`` including ``<a>`` or ``<span>`` with ``@class=p-name``)

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:return: set of editors
		"""
		retval = set()

		for dd in html.findall(".//dd[@class]"):
			if dd.get('class').find('p-author') != -1:
				for a in dd.findall(".//a[@class]"):
					if a.get('class').find('p-name') != -1:
						retval.add(a.text)
						break
				for span in dd.findall(".//span[@class]"):
					if span.get('class').find('p-name') != -1:
						retval.add(span.text)
						break

		return retval

	# noinspection PyPep8,PyBroadException
	@staticmethod
	def set_html_meta(html, head):
		"""
		 Change the meta elements so that:

		 - any ``@http-equiv=content-type`` is removed
		 - there should be an extra meta setting the character set

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:param head: the object for the <head> element
		:type head: :py:class:`xml.etree.ElementTree.Element`
		"""
		for meta in html.findall(".//meta[@http-equiv='content-type']") + html.findall(".//meta[@http-equiv='Content-Type']"):
			try:
				head.remove(meta)
			except:
				pass
		SubElement(head, "meta", charset="utf-8")

	@staticmethod
	def html_to_xhtml(html):
		"""
		Make the minimum changes necessary in the DOM tree so that the XHTML output is valid and accepted
		by epub readers
		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:return: the input object
		"""
		# Set the xhtml namespace on the top, this is required by epub readers
		# noinspection PyUnresolvedReferences
		html.set("xmlns", "http://www.w3.org/1999/xhtml")

		# The script reference element should not be self-closed, but with a separate </script> instead. Just adding
		# an extra space to a possible link does the trick.
		for script in html.findall(".//script[@src]"):
			if script.text is None:
				script.text = " "
		return html

	# noinspection PyPep8Naming
	@staticmethod
	def change_DOM(html):
		"""
		 Changes on the DOM to ensure a proper interoperability of the display among EPUB readers. At the moment, the
		 following actions are done:

		 1. Due to the rigidity of the iBook reader, the DOM tree has to change: all children of the ``<body>`` should be
		 encapsulated into a top level block element (we use ``<div id="epubmain">``). This is because iBook imposes
		 a zero padding on the body element, and that cannot be controlled by the user; the introduction of the top level
		 block element allows for suitable CSS adjustments.

		 Note that using simply a "main" element is not a good approach, because some files (e.g., generated by
		 bikeshed) already use that element, and there can be only one...

		 2. For some unknown reasons, if a ``<pre>`` element has the class ``highlight``, the Readium extension to
		 Chrome goes wild. On the other hand, that class name is used only for an internal processing of ReSpec; it is
		 unused in the various, default CSS content. As a an emergency measure this is simply removed from the code, although,
		 clearly, this is not the optimal way of doing this:-( But hopefully this will disappear and this hack can be
		 removed, eventually.

		 **Note**: the second issue is an `acknowledged bug in Readium <https://github.com/readium/readium-shared-js/issues/203>`__.
		 When a newer release of Readium is deployed, this hack should be removed from the code.

		 3. Some readers *require* to have a ``type="text/css"`` on the the link element for a CSS; otherwise the CSS
		 is ignored.

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		"""

		# Hack #1
		body = html.find(".//body")

		if len(html.findall(".//div[@main='role']")) == 0:
			main = SubElement(body, "div")
			main.set("role", "main")

			# All children of body, except for main, should be re-parented to main and removed from body
			# Note: this is a workaround around what seems to be a bug in the html5parser. Indeed,
			# the direct creation of an Element object does not work; the SubElement method must be used
			# but this means that element should be avoided in the cycle below. Sigh...
			for child in [x for x in body.findall("*") if not (x.tag == "div" and x.get("role", None) == "main")]:
				main.append(child)
				body.remove(child)

		# Hack #2
		# Change the "highlight" class name
		# noinspection PyShadowingNames
		def _change_name(x):
			return x if x != "highlight" else "book_highlight"

		for pre in html.findall(".//pre[@class]"):
			# there may be several class names
			cl_names = pre.get("class").split()
			new_cl_names = map(_change_name, cl_names)
			pre.set("class", " ".join(new_cl_names))

		# Hack #3
		# Add the type="text/css" for stylesheet elements
		for lnk in html.findall(".//link[@rel='stylesheet']"):
			if "type" not in lnk.keys():
				lnk.set("type", "text/css")

	@staticmethod
	def extract_toc(html, short_name):
		"""
		Extract the table of content from the document. ``html`` is the Element object for the full document. ``toc_tuples``
		is an array of ``TOC_Item`` objects where the items should be put, ``short_name`` is the short name for the
		document as a whole (used in possible warnings).

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:param str short_name: short name of the document as a whole (used in possible warning)
		:return: array of :py:class:`.TOC_Item` instances
		"""
		retval = []

		def extract_toc_entry(parent, explicit_num=None):
			"""
			Extract the TOC entry and create a URI with the 'Overview' file. This does not work well if the
			document is cut into several documents, like the HTML5 spec...

			The result is added to the tuples as a TOC_Item entry.
			"""
			a = parent.find("a")

			ref = a.get("href")
			ref = "Overview.xhtml" + ref if ref[0] == '#' else ref.replace(".html", ".xhtml", 1)
			texts = [k.strip() for k in a.itertext()]
			label = " ".join(texts).strip()
			if explicit_num is None:
				short_label = label if len(texts) == 1 else " ".join(texts[1:]).strip()
			else:
				short_label = label
				label = ("%s. " % explicit_num) + short_label
			# The 'short label' is the title only, without an initial numbering. Unfortunately
			# some, non respec documents put the numbers there without structuring, and so it ends
			# up there regardless...
			# (hm. This may make the previous steps unnecessary. To be checked!)
			if short_label_pattern.match(short_label) is not None:
				short_label = " ".join(short_label.split(" ")[1:]).strip()

			retval.append(TOC_Item(ref, label, short_label))
		# end extract_toc_entry

		def toc_respec_or_bikeshed():
			"""
			Extract the TOC items following ReSpec or Bikeshed conventions. There are possible pairs (see the ``TOC_PAIRS``
			alternatives), yielding <li> elements with the toc entry.
			"""
			## respec version
			# We have to try two different versions, because, in some cases, respec uses 'div' and in other cases 'section'
			# probably depends on the output format requested (or the version of respec? or both?)
			# In all cases, the <a> element contains a section number and the chapter title
			for pairs in TOC_PAIRS:
				xpath = ".//{}/{}".format(pairs[0], pairs[1])
				toc = html.findall(xpath)
				if len(toc) > 0:
					for li in toc[0].findall("li"):
						if pairs[2] is not None and "class" in li.keys() and li.get('class').find(pairs[2]) == -1:
							continue
						extract_toc_entry(li)
					return True
			return False

		# Execute the various versions in order
		if toc_respec_or_bikeshed():
			# we are fine, found what is needed
			return retval
		else:
			# if we got here, something is wrong...
			if config.logger is not None:
				config.logger.warning("Could not extract a table of content from '%s'" % short_name)
			return []
	# end _extract_toc


###################################################################################
class HttpSession:
	# noinspection PyPep8
	"""
		Wrapper around an HTTP session; the returned media type is compared against accepted media
		types.

		:param str url: the URL to be retrieved
		:param boolean check_media_type: whether the media type should be checked against the media type of the resource to see if it is acceptable
		:param boolean raise_exception: whether an exception should be raised if the document cannot be retrieved (either because the HTTP return is not 200, or not of an acceptable media type)
		:raises R2EError: in case the file is not an of an acceptable media type, or the HTTP return is not 200
		"""
	# noinspection PyPep8,PyPep8
	def __init__(self, url, check_media_type=False, raise_exception=False):
		def handle_exception(message):
			if config.logger is not None:
				config.logger.error(message)
			if raise_exception:
				raise R2EError(message)

		self._success    = False
		self._media_type = ""
		self._data       = None
		self._url        = url

		# noinspection PyBroadException
		try:
			self._data = urlopen(url)
		except Exception:
			handle_exception("%s cannot be reached" % url)
			return

		if self._data.getcode() != '200' and self._data.getcode() != 200:
			handle_exception("Received a '%s' status code instead of '200'" % self._data.getcode())
			return

		self._media_type = self._data.info().gettype()
		if check_media_type and self._media_type not in config.ACCEPTED_MEDIA_TYPES:
			handle_exception("Received a file of type '%s', which is not defined as acceptable" % self._media_type)
			return

		self._success = True

	@property
	def success(self):
		"""
		True if the HTTP retrieval was successful, False otherwise
		"""
		return self._success

	@property
	def data(self):
		"""
		The returned resource, as a file-like object
		"""
		return self._data

	@property
	def url(self):
		"""
		The request URL for this session
		"""
		return self._url

	@property
	def media_type(self):
		"""
		Media type of the resource
		"""
		return self._media_type

#####################################################################################


# noinspection PyPep8
class Book(object):
	"""Abstraction for a book; it encapsulates a zip file as well as saving the content into a
	  directory.

	  :param book_name: file name of the book
	  :param folder_name: name of the directory
  	  :param package: whether a real zip file should be created or not
	  :param folder: whether the directory structure should be created separately or not
	"""
	def __init__(self, book_name, folder_name, package=True, folder=False):
		self._package       = package
		self._folder        = folder
		self._name          = folder_name
		self._zip           = None
		self.already_stored = []

		if self.folder:
			# To be sure the previous folder, if it exists, should be removed
			if os.path.exists(folder_name):
				shutil.rmtree(folder_name, ignore_errors=True)
			os.mkdir(folder_name)
		if self.package:
			self._zip = zipfile.ZipFile(book_name, 'w', zipfile.ZIP_DEFLATED)

		self.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
		self.writestr('META-INF/container.xml', meta_inf)

	@property
	def package(self):
		"""Flag whether an EPUB package should be generated or not"""
		return self._package

	@property
	def folder(self):
		"""Flag whether a folder should be generated or not"""
		return self._folder

	@property
	def name(self):
		"""Prefix that should be added to all names when storing a folder (set to the short name of the document)"""
		return self._name

	@property
	def zip(self):
		"""The package (book) file itself"""
		return self._zip

	def writestr(self, target, content, compress=zipfile.ZIP_DEFLATED):
		"""
		Write the content of a string. Care should be taken not to write "target" twice; the zipfile would really
		duplicate the content in the archive (as opposed to file writing that would simply overwrite the previous
		incarnation of the same file). This method takes care of that through the `already_stored` array.

		:param target: path for the target file
		:param content: string/bytes to be written on the file
		:param compress: either zipfile.ZIP_DEFLATED or zipfile.ZIP_STORED, whether the content should be compressed, resp. not compressed
		"""
		if target not in self.already_stored:
			self.already_stored.append(target)
			if self.folder:
				with open(self._path(target), "w") as f:
					f.write(content)
			if self.package:
				self.zip.writestr(target, content, compress)

	# noinspection PyUnresolvedReferences
	def write_element(self, target, element):
		"""
		An ElementTree object is added to the book.

		:param str target: path for the target file
		:param element: the XML tree to be stored
		:type element: :py:class:`xml.etree.ElementTree`
		"""
		content = StringIO()
		element.write(content, encoding="utf-8", xml_declaration=True, method="xml")
		self.writestr(target, content.getvalue())
		content.close()

	# noinspection PyTypeChecker
	def write_session(self, target, session):
		"""
		The returned content of an :py:class:`.HttpSession` is added to the book. If the content is an HTML file,
		it will be converted into XHTML on the fly.

		:param str target: path for the target file
		:param session: a :py:class:`.HttpSession` instance whose data must retrieved to be written into the book
		:boolean return: the value of session.success
		"""
		# Copy the content into the final book
		# Special care should be taken with html files. Those are supposed to become XHTML:-(
		if not session.success:
			config.logger.info("Unsuccessful HTTP session; did not store %s" % session.url)
		else:
			if session.media_type == 'text/html':
				# We have to
				# 1. parse the source with the html5 parser
				# 2. add the xhtml namespace to the top and take care of the stupid script issue (no self-closing scripts!)
				# 3. write the result as xhtml through the write_element method
				html = html5lib.parse(session.data, namespaceHTMLElements=False)
				Utils.html_to_xhtml(html)
				self.write_element(target.replace('.html', '.xhtml', 1), ElementTree(html))
			else:
				# Note that some of the media types are not to be compressed
				self.writestr(target, session.data.read(), zipfile.ZIP_STORED if session.media_type in _NO_COMPRESS else zipfile.ZIP_DEFLATED)
		return session.success

	# noinspection PyPep8Naming
	def write_HTTP(self, target, url):
		"""
		Retrieve the content of a URI and store it in the book. (This is a wrapper around the `write_session` method.)

		:param str target: path for the target file
		:param url: URL that has to be retrieved to be written into the book
		:boolean return: whether the HTTP session was successful or not
		"""
		# Copy the content into the final book.
		# Note that some of the media types are not to be compressed
		return self.write_session(target, HttpSession(url))

	def _path(self, path):
		"""
		Expand the path with the name of the package, check whether the resulting path (filename) includes intermediate
		directories and create those on the fly if necessary.

		:param path: path to be checked
		:return: expanded, full path
		"""
		full_path = os.path.join(self.name, path)
		(dirs, name) = os.path.split(full_path)
		if dirs != '' and not os.path.exists(dirs):
			os.makedirs(dirs)
		return full_path

	def close(self):
		"""
		Close the book (i.e., the archive).
		"""
		if self.package:
			self.zip.close()

	# The properties below are necessary to use the class in a "with ... as" python structure
	def __enter__(self):
		return self

	# noinspection PyUnusedLocal
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

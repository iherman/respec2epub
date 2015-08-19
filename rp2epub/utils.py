# -*- coding: utf-8 -*-
from urllib2 import urlopen, HTTPError
from StringIO import StringIO
from datetime import date
import re
import warnings
import os
import os.path
import shutil
from xml.etree.ElementTree import SubElement, ElementTree
import zipfile
import html5lib
from .templates import meta_inf
from . import R2EError

# These media types should be added to the zip file uncompressed
# noinspection PyPep8
_NO_COMPRESS = ["image/png",
				"image/jpeg",
				"image/jpeg",
				"image/gif",
				"audio/mpeg",
				"video/mp4",
				"video/webm",
				"video/ogg"]

########################################## Table of content extraction ########################################
short_label_pattern = re.compile("^[1-9][0-9]*\. .*$")
# list of element pairs that lead to a table of content
# noinspection PyPep8
# structures for TOC elements in respec: element hierarchy and, if not None, the class name for the <li> element.
TOC_PAIRS_RESPEC = [
	("div[@id='toc']", "ul[@class='toc']", None),
	("div[@id='toc']", "ol[@class='toc']", None),
	("section[@id='toc']", "ul[@class='toc']", None),
	("section[@id='toc']", "ol[@class='toc']", None),
	("div[@class='toc']", "ul[@class='toc']", "tocline1"),
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
		for f in html.findall(".//form"):
			retval.add("scripted")
			# one is enough:-)
			break

		# Inline SVG
		for f in html.findall(".//{http://www.w3.org/2000/svg}svg"):
			retval.add("svg")
			# one is enough:-)
			break

		# Inline MathML
		for f in html.findall(".//{http://www.w3.org/1998/Math/MathML}math"):
			retval.add("mathml")
			# one is enough:-)
			break
		return retval
	# end _get_extra_properties

	# noinspection PyPep8
	@staticmethod
	def create_shortname(name):
		"""
		Create the short name, in W3C jargon, based on the dated name. Returns a tuple with the category of the
		publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, ``ED``, or ``PER``), and the short name itself.

		:param str name: dated name
		:return: tuple of with the category of the publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, ``ED``, or ``PER``), and the short name itself.
		:rtype: tuple
		"""
		# This is very W3C specific...
		for cat in ["REC", "NOTE", "PR", "WD", "CR", "PER"]:
			if name.startswith(cat + "-"):
				name = name[len(cat)+1:]
				return cat, name[:-9]

		# If we get there, the name does not abide to any pattern; it is taken to be an ED
		return "ED", name
	# end create_shortname

	@staticmethod
	def retrieve_date(duri):
		"""
		Retrieve the (publication) date from the dated URI.

		:param str duri: dated URI
		:return: date
		:rtype: :py:class:`datetype.date`
		"""
		# remove the last '/' if any
		try:
			d = duri[:-1] if duri[-1] == '/' else duri
			# Date in compact format:
			pdate = d[-8:]
			return date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))
		except:
			R2EError("dated URI is not of the expected format")
	# end retrieve_date

	@staticmethod
	# noinspection PyBroadException
	def extract_editors(html):
		"""Extract the editors' names from a document, following the respec conventions
		(@class=p-author for <dd> including <a> or <span> with @class=p-name)

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
		 - any ``@http-equiv=content-type`` should be removed
		 - there should be an extra meta setting the character set

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:param head: the object for the <head> element
		:type head: :py:class:`xml.etree.ElementTree.Element`
		"""
		for meta in html.findall(".//meta[@http-equiv='content-type']"):
			try:
				head.remove(meta)
			except:
				pass
		for meta in html.findall(".//meta[@http-equiv='Content-Type']"):
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

		def toc_respec():
			"""
			Extract the TOC items following respec conventions. there are possible pairs (see the ``TOC_PAIRS``
			alternatives, they all appear in different respec generated documents...), yielding to <li> elements with
			the toc entry.
			"""
			## respec version
			# We have to try two different versions, because, in some cases, respec uses 'div' and in other cases 'section'
			# probably depends on the output format requested (or the version of respec? or both?)
			# In all cases, the <a> element contains a section number and the chapter title
			# To make it worse, some documents do even use any of those two...
			# Would be great if the xpath used allowed for alternatives:-(
			for pairs in TOC_PAIRS_RESPEC:
				xpath = ".//{}/{}".format(pairs[0], pairs[1])
				toc = html.findall(xpath)
				if len(toc) > 0:
					for li in toc[0].findall("li"):
						if pairs[2] is not None and "class" in li.keys() and li.get('class').find(pairs[2]) == -1:
							continue
						extract_toc_entry(li)
					return True
			return False

		def toc_xml_css(top_level, toc_entry):
			"""
			Generic TOC extraction: top_level defines the XPATH to get the TOC structure, and toc_entry the
			tag that has to be found containing the necessary <a> element
			"""
			toc = html.findall(top_level)
			num = 0
			if len(toc) > 0:
				for e in toc[0].findall(toc_entry):
					num += 1
					extract_toc_entry(e, explicit_num=num)
			return num > 0

		# Execute the various versions in order
		if toc_respec() or toc_xml_css(".//ul[@class='toc']", "li") or toc_xml_css(".//p[@class='toc']", "b"):
			# we are fine, found what is needed
			return retval
		else:
			# if we got here, something is wrong...
			warnings.warn("Could not extract a table of content from '%s'" % short_name)
			return []
	# end _extract_toc


###################################################################################
class HttpSession:
	# noinspection PyPep8
	"""
		Wrapper around an HTTP session; the returned media type is compared against accepted media
		types.

		:param str url: the URL to be retrieved
		:param list accepted_media_types: and array of media type strings giving a list of those that should be added to the book
		:param boolean raise_exception: whether an exception should be raised if the document cannot be retrieved (either because the HTTP return is not 200, or not of an acceptable media type)
		:raises Exception: in case the file is not an of an acceptable media type, or the HTTP return is not 200
		"""
	# noinspection PyPep8,PyPep8
	def __init__(self, url, accepted_media_types=None, raise_exception=False):
		self._success = False
		try:
			self._data = urlopen(url)
		except HTTPError:
			if raise_exception:
				raise R2EError("%s cannot be reached!" % url)
			return

		if self._data.getcode() != '200' and self._data.getcode() != 200:
			if raise_exception:
				raise R2EError("Received a '%s' status code instead of '200'" % self._data.getcode())
			return
		self._media_type = self._data.info().gettype()
		if accepted_media_types is not None and self._media_type not in accepted_media_types:
			if raise_exception:
				raise R2EError("Received a file of type '%s', which was not listed as acceptable" % self._media_type)
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
	def media_type(self):
		"""
		Media type of the resource
		"""
		return self._media_type

#####################################################################################


# noinspection PyPep8
class Book(object):
	"""Abstraction for a book; in real usage, it just encapsulates a zip file but, for debugging purposes,
		it just a wrapper around equivalent file output in the current directory.
	"""
	def __init__(self, book_name, folder_name, package=True, folder=False):
		"""
		:param name: name of the book (without the '.epub' extension)
		:param package: whether a real zip file should be created or not
		:param folder: whether the directory structure should be created separately or not
		:return:
		"""
		self._package       = package
		self._folder        = folder
		self._name          = folder_name
		self._zip           = None
		self.already_stored = []

		if self.folder:
			# To be sure, the previous folder, if it exists, should be removed
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
		"""The package files itself"""
		return self._zip

	def writestr(self, target, content, compress=zipfile.ZIP_DEFLATED):
		"""
		Write the content of a strong onto a file in the book.
		:param target: path for the target file
		:param content: string/bytes to be written on the file
		:param compress: either zipfile.ZIP_DEFLATED or zipfile.ZIP_STORED, whether the content should be compressed, resp. not compressed
		"""
		if target in self.already_stored:
			return
		else:
			self.already_stored.append(target)
		if self.folder:
			with open(self._path(target), "w") as f:
				f.write(content)
		if self.package:
			self.zip.writestr(target, content, compress)

	# noinspection PyUnresolvedReferences
	def write_element(self, target, element):
		"""
		An ElementTree object added to the book.

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
		Return content of an HTTP session added to the book.

		:param str target: path for the target file
		:param HttpSession session: session whose data must retrieved to be written into the book
		:return:
		"""
		# Copy the content into the final book
		# Special care should be taken with html files. Those are supposed to become XHTML:-(
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

	# noinspection PyPep8Naming
	def write_HTTP(self, target, url):
		"""
		Return content of an HTTP session added to the book.

		:param str target: path for the target file
		:param url: URL that has to be retrieved to be written into the book
		:return:
		"""
		# Copy the content into the final book.
		# Note that some of the media types are not to be compressed
		self.write_session(target, HttpSession(url))

	def _path(self, path):
		"""
		Expand the path with the name of the package, check if the resulting path (filename) includes intermediate
		directories and create those on the fly
		:param path: path to be checked
		:return: expanded, full path
		"""
		full_path = os.path.join(self.name,path)
		(dirs, name) = os.path.split(full_path)
		if dirs != '' and not os.path.exists(dirs):
			os.makedirs(dirs)
		return full_path

	def close(self):
		"""
		Closing the archive.
		"""
		if self.package:
			self.zip.close()

	# The properties below are necessary to use the class in a "with ... as" python structure
	def __enter__(self):
		return self

	# noinspection PyUnusedLocal
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

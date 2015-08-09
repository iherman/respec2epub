# -*- coding: utf-8 -*-
from urllib2 import urlopen, HTTPError
from StringIO import StringIO
from datetime import date
import re
import warnings
from xml.etree.ElementTree import SubElement
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import zipfile

# These media should be added to the zip file uncompressed
_NO_COMPRESS = ["image/png", "image/jpeg", "image/jpeg", "image/gif"]

# Generic utility functions to extract information from a W3C TR document...
# noinspection PyUnusedLocal,PyPep8
def get_document_properties(html, target):
	"""
		Find the extra manifest properties that must be added to the HTML resource in the opf file.

		See the `IDPF documentation <http://www.idpf.org/epub/30/spec/epub30-publications.html#sec-item-property-values>`_ for details

		:param html: the object for the whole document
		:type html: :py:class:`xml.etree.ElementTree.ElementTree`
		:param set target: set collecting all possible property values

	"""
	# If <script> is used for Javascript, the 'scripted' property should be set
	for scr in html.findall(".//script"):
		if "type" not in scr.keys() or scr.get("type") == "application/javascript":
			# The script element is really used for scripting
			target.add("scripted")
			# No reason to look further
			break

	# If an interactive form is used, the 'scripted' property should be set
	for f in html.findall(".//form"):
		target.add("scripted")
		# one is enough:-)
		break

	# Inline SVG
	for f in html.findall(".//{http://www.w3.org/2000/svg}svg"):
		target.add("svg")
		# one is enough:-)
		break

	# Inline MathML
	for f in html.findall(".//{http://www.w3.org/1998/Math/MathML}math"):
		target.add("mathml")
		# one is enough:-)
		break
# end _get_extra_properties

def create_shortname(name):
	"""
	Create the short name, in W3C jargon, based on the dated name. Returns a tuple with the category of the
	publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, or ``PER``), and the short name itself.

	:param str name: dated name
	:return: tuble of with the category of the publication (``REC``, ``NOTE``, ``PR``, ``WD``, ``CR``, or ``PER``), and the short name itself.
	:rtype: tuple

	"""
	# This is very W3C specific...
	for cat in ["REC", "NOTE", "PR", "WD", "CR", "PER"]:
		if name.startswith(cat + "-"):
			name = name[len(cat)+1:]
			return cat, name[:-9]
# end create_shortname

def retrieve_date(duri):
	"""
	Retrieve the (publication) date from the dated URI.

	:param str duri: dated URI
	:return: date
	:rtype: :py:class:`datetype.date`
	"""
	# remove the last '/' if any
	d = duri[:-1] if duri[-1] == '/' else duri
	# Date in compact format:
	pdate = d[-8:]
	return date(int(pdate[0:4]), int(pdate[4:6]), int(pdate[6:8]))
# end retrieve_date

# noinspection PyBroadException
def extract_editors(html, editors, short_name):
	"""Extract the editors' names from a document.

	:param html: the object for the whole document
	:type html: :py:class:`xml.etree.ElementTree.ElementTree`
	:param set editors: A set to which new editors (strings) should be added
	:param str short_name: short name of the original document
	"""

	def editors_respec():
		"""
		Extract the editors following the respec conventions (@class=p-author for <dd> including <a> or <span> with @class=p-name)

		The same structure also works for the CSS document series.
		"""
		# respec version
		retval = False
		for dd in html.findall(".//dd[@class]"):
			if dd.get('class').find('p-author') != -1:
				for a in dd.findall(".//a[@class]"):
					if a.get('class').find('p-name') != -1:
						editors.add(a.text)
						retval = True
						break
				for span in dd.findall(".//span[@class]"):
					if span.get('class').find('p-name') != -1:
						editors.add(span.text)
						retval = True
						break
		return retval

	if editors_respec():
		# we are fine, found whatever is needed
		return
	else:
		# if we got here, something is wrong...
		warnings.warn("Could not extract an editors' list from '%s'" % short_name)

	# end _extract_editors

# =====================================
# Class to hold a table of content item
# =====================================
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


def extract_toc(html, toc_tuples, short_name):
	"""
	Extract the table of content from the document. ``html`` is the Element object for the full document. ``toc_tuples``
	is an array of ``TOC_Item`` objects where the items should be put, ``short_name`` is the short name for the
	document as a whole (used in possible warnings).

	:param html: the object for the whole document
	:type html: :py:class:`xml.etree.ElementTree.ElementTree`
	:param array toc_tuples: array of :py:class:`.TOC_Item` instances
	:param str short_name: short name of the document as a whole (used in possible warning)

	"""
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

		toc_tuples.append(TOC_Item(ref, label, short_label))
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
		return
	else:
		# if we got here, something is wrong...
		warnings.warn("Could not extract a table of content from '%s'" % short_name)
# end _extract_toc


# noinspection PyPep8
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

	meta = SubElement(head, "meta")
	meta.set("charset", "utf-8")


###################################################################################
class HttpSession:
	"""
	Wrapper around an HTTP session; the returned media type is compared against accepted media
	types.

	:param str url: the URL to be retrieved
	:param array accepted_media_type: and array of media type strings giving a list of those that should be added to the book
	:param boolean raise_exception: whether an exception should be raised if the document cannot be retrieved (either because the HTTP return is not 200, or not of an acceptable media type)
	:raises Exception: in case the file is not an of an acceptable media type, or the HTTP return is not 200
	"""
	# noinspection PyPep8,PyPep8
	def __init__(self, url, accepted_media_types=None, raise_exception=False):
		self._success = False
		try:
			self._data = urlopen(url)
		except HTTPError:
			raise Exception("%s cannot be reached!" % url)

		if self._data.getcode() != '200' and self._data.getcode() != 200:
			if raise_exception:
				raise Exception("Received a '%s' status code instead of '200'" % self._data.getcode())
			return
		self._media_type = self._data.info().gettype()
		if accepted_media_types is not None and self._media_type not in accepted_media_types:
			if raise_exception:
				raise Exception("Received a file of type '%s', which was not listed as acceptable" % self._media_type)
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

	def store_in_book(self, book, target):
		"""
		Store the content in a book.

		:param zipfile.ZipFile book: the book itself
		:param str target: the name of the content whithin the book

		"""
		# Copy the content into the final book.
		# Note that some of the media types are not to be compressed
		compress = zipfile.ZIP_STORED if self.media_type in _NO_COMPRESS else zipfile.ZIP_DEFLATED
		book.writestr(target, self.data.read(), compress)


def et_to_book(xml_doc, doc_name, epub_file):
	"""
	An ElementTree object added to the book. ``xml_doc`` is the ElementTree, the ``doc_name`` is the
	name to be used within the book, and ``epub_file`` is the book itself (ie, an open ``zipfile`` instance).

	:param ElementTree.ElementTree xml_doc: the full XML tree to be stored
	:type xml_doc: :py:class:`xml.etree.ElementTree.Element`
	:param str doc_name: the name of the content whithin the book
	:param epub_file: the book itself
	:type epub_file: :py:class:`zipfile.ZipFile`
	"""
	target = StringIO()
	xml_doc.write(target, encoding="utf-8", xml_declaration=True, method="xml")
	epub_file.writestr(doc_name, target.getvalue())
	target.close()


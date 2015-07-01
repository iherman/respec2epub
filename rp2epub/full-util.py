# -*- coding: utf-8 -*-
"""
Various utility functions, also used in the simplifed version of the module.
"""
from datetime import date
import re
import warnings
from xml.etree.ElementTree import SubElement
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import zipfile

# These media should be added to the zip file uncompressed
_NO_COMPRESS = ["image/png", "image/jpeg", "image/jpeg", "image/gif"]


def create_epub_file(directory, resources):
	"""
	Creation of the epub file itself, ie, the zipped archive, following the specification in EPUB,

	:param str directory: name of the directory to be packaged
	:param resources: set of resources, other then the package file, the mimetype and the container, that has to be added
	:type resources: array of (name, media-type) tuples
	"""
	with zipfile.ZipFile(directory + '.epub', 'w', zipfile.ZIP_DEFLATED) as book:
		# First the regular files, generated for all ebooks
		book.write(directory + '/mimetype', 'mimetype', zipfile.ZIP_STORED)
		book.write(directory + '/META-INF/container.xml', 'META-INF/container.xml')
		book.write(directory + '/package.opf', 'package.opf')
		for (href, media_type) in resources:
			# These resources should be added to the zip file
			# Images should not be compressed, just stored
			compress = zipfile.ZIP_STORED if media_type in _NO_COMPRESS else zipfile.ZIP_DEFLATED
			book.write(directory + "/" + href, href, compress)


def package_epub_directory(directory):
	"""
	Package the directory as a zip file for epub. This utility is only used with the option to generate
	the file from the directory directly, without any preceding steps; it extracts the resources
	by parsing the package file. It then calls the :py:func:`.create_epub_file` function.

	:param str directory: name of the directory to be packaged

	"""
	# Find the directory package file; this relies on the particular structure created by the package
	packagefile = directory + "/package.opf"
	opf = ET.parse(packagefile)

	resources = []
	# Find the list of resources that must be put into the file
	for item in opf.findall(".//{http://www.idpf.org/2007/opf}item"):
		resources.append((item.get("href"), item.get("media-type")))

	create_epub_file(directory, resources)


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
		Extract the editors following the respec conventions (@class=p-author for <dd> inluding <a> or <span> with @class=p-name)

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

	# noinspection PyBroadException
	def editors_xmlspec():
		"""
		Extract the editors following the xmlspec conventions: <div> element with @class=head with a <dd>,
		that has <dt> for the term 'Editor' and the corresponding <dd> providing the name of the
		editors.
		"""
		retval = False
		# sigh, this is probably an xmlspec document, that part is much
		# messier:-(
		start = False
		for dl in html.findall(".//div[@class='head']/dl"):
			# there should be only one, in fact
			for el in dl:
				if el.tag == 'dt':
					start = el.text.find("Editor") != -1
				if start and el.tag == 'dd':
					# bingo, this is a genuine editor...
					# get all the text, it may be in subelements...
					retval = True
					name = ""
					for t in el.itertext():
						name += t
					# There are cases when the 'editor' is set to a whole working group; that should be removed
					try:
						editors.add(name.split(',')[0].strip())
					except:
						pass
		return retval

	if editors_respec() or editors_xmlspec():
		# we are fine, found whatever is needed
		return
	else:
		# if we got here, something is wrong...
		warnings.warn("Could not extract an editors' list from '%s'" % short_name)

	# end _extract_editors

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


# =====================================
# Class to hold a table of content item
# =====================================
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



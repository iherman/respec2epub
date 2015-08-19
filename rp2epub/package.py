# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, SubElement
from .templates import PACKAGE, TOC, NAV, COVER

# noinspection PyPep8
SUBTITLE = {
	'REC'  : "W3C Recommendation",
	'NOTE' : "W3C Note",
	"PR"   : "W3C Proposed Recommendation",
	"PER"  : "W3C Proposed Edited Recommendation",
	"CR"   : "W3C Candidate Recommendation",
	"WD"   : "W3C Working Draft",
	"ED"   : "W3C Editor's Draft"
}


# noinspection PyPep8
class Package:
	"""
	Methods to generate the manifest, TOC in different formats, and the cover pages

	:param driver: the caller
	:type driver: :py:class:`.DocWrapper`
	"""
	def __init__(self, driver):
		self._book     = driver.book
		self._document = driver.document

	@property
	def book(self):
		"""The target book; a :py:class:`.Book` instance"""
		return self._book

	@property
	def document(self):
		"""Wrapper around a document; a :py:class:`.Document` instance"""
		return self._document

	def process(self):
		"""Top level entry to execute the various internal methods"""
		self._create_opf()
		self._create_ncx()
		self._create_nav()
		self._create_cover()

	def _create_opf(self):
		"""
		Create the manifest file. Includes the list of resources, book metadata, and the spine. The manifest
		file is added to the book as ``package.opf``
		"""
		from .doc2epub import DEFAULT_FILES, CSS_LOGOS
		# Last step: the manifest file must be created
		# Parse the raw manifest file
		ET.register_namespace('', "http://www.idpf.org/2007/opf")
		opf = ElementTree(ET.fromstring(PACKAGE))

		# Add the 'main' file
		manifest = opf.findall(".//{http://www.idpf.org/2007/opf}manifest")[0]

		# Get the default resources first
		for (href, media_type, item_id, prop) in DEFAULT_FILES:
			# These resources should be added to the zip file
			# Images should not be compressed, just stored
			item = SubElement(manifest, "{http://www.idpf.org/2007/opf}item")
			item.set("id", item_id)
			item.set("href", href)
			item.set("media-type", media_type)
			if prop != "":
				item.set("properties", prop)
			item.tail = "\n    "

		# Add the type-specific logo
		if self.document.doc_type in CSS_LOGOS:
			item = SubElement(manifest, "{http://www.idpf.org/2007/opf}item")
			item.set("id", "css-logo")
			item.set("href", CSS_LOGOS[self.document.doc_type][1])
			item.set("media-type", "image/png")
			item.tail = "\n    "

		item = SubElement(manifest, "{http://www.idpf.org/2007/opf}item")
		item.set("id", "main")
		item.set("href", "Overview.xhtml")
		item.set("media-type", "application/xhtml+xml")
		if self.document.properties is not None:
			item.set("properties", self.document.properties)
		item.tail = "\n    "

		# Add the additional resources
		for resource_target, media_type in self.document.additional_resources:
			item = SubElement(manifest, "{http://www.idpf.org/2007/opf}item")
			item.set("href", resource_target)
			item.set("media-type", media_type)
			item.set("id", resource_target.replace('/', '-'))
			item.tail = "\n    "

		# Add the (only) spine element
		spine = opf.findall(".//{http://www.idpf.org/2007/opf}spine")[0]
		item = SubElement(spine, "{http://www.idpf.org/2007/opf}itemref")
		item.set("idref", "main")

		# Remove the unnecessary item in spine (from the general template)
		to_remove = opf.findall(".//{http://www.idpf.org/2007/opf}itemref[@idref='toc']")[0]
		spine.remove(to_remove)

		# Manifest metadata
		title = opf.findall(".//{http://purl.org/dc/elements/1.1/}title")[0]
		title.text = self.document.title
		identifier = opf.findall(".//{http://purl.org/dc/elements/1.1/}identifier")[0]
		identifier.text = self.document.dated_uri
		date = opf.findall(".//{http://www.idpf.org/2007/opf}meta[@property='dcterms:modified']")[0]
		date.text = self.document.date.strftime("%Y-%m-%dT%M:%S:00Z")
		date = opf.findall(".//{http://www.idpf.org/2007/opf}meta[@property='dcterms:date']")[0]
		date.text = self.document.date.strftime("%Y-%m-%dT%M:%S:00Z")
		creator = opf.findall(".//{http://purl.org/dc/elements/1.1/}creator")[0]
		creator.text = self.document.editors

		# Push the manifest file into the book, too
		self.book.write_element('package.opf', opf)

	#===================================================
	# Generate the old style table of content (ncx file)
	#===================================================
	# noinspection PyPep8,PyPep8Naming
	def _create_ncx(self):
		"""
		Create and old style TOC file ('ncx' file): ``toc.ncx``. To be used for reading systems that cannot
		handle EPUB3 specific TOC.
		"""
		# noinspection PyPep8Naming,PyPep8
		def set_nav_point(parent, href, label, the_index):
			the_navPoint = SubElement(parent, "{http://www.daisy.org/z3986/2005/ncx/}navPoint")
			the_navPoint.set("id", "nav%s" % the_index)
			the_navPoint.set("playOrder", "%s" % the_index)
			the_navPoint.set("class", "h1")

			the_navLabel = SubElement(the_navPoint, "{http://www.daisy.org/z3986/2005/ncx/}navLabel")
			the_txt      = SubElement(the_navLabel, "{http://www.daisy.org/z3986/2005/ncx/}text")
			the_txt.text = label

			content  = SubElement(the_navPoint, "{http://www.daisy.org/z3986/2005/ncx/}content")
			content.set("src", href)
			return the_navPoint

		# The doc title is also set in the TOC if exists
		ET.register_namespace('', "http://www.daisy.org/z3986/2005/ncx/")
		ncx = ElementTree(ET.fromstring(TOC))

		# Set the title
		title    = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}docTitle")[0]
		txt      = SubElement(title, "{http://www.daisy.org/z3986/2005/ncx/}text")
		txt.text = self.document.title

		# Set the authors
		authors    = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}docAuthor")[0]
		txt        = SubElement(authors, "{http://www.daisy.org/z3986/2005/ncx/}text")
		txt.text   = self.document.editors

		# Set the book ID
		meta_id = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}meta[@name='dtb:uid']")[0]
		meta_id.set('content', self.document.dated_uri)

		navMap = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}navMap")[0]

		# One element must be removed from the general template
		to_remove = ncx.findall(".//{http://www.daisy.org/z3986/2005/ncx/}navPoint[@id='toc']")[0]
		navMap.remove(to_remove)

		index = 2
		for toc_entry in self.document.toc:
			set_nav_point(navMap, toc_entry.href, toc_entry.label, index)
			index += 1

		self.book.write_element('toc.ncx', ncx)
	# end _create_ncx

	#===================================================
	# Generate the new style table of content (nav file)
	#===================================================
	# noinspection PyPep8Naming
	def _create_nav(self):
		"""
		Create a new style TOC file ('nav' file): ``nav.xhtml``.
		"""

		# Setting the default namespace; this is important when the file is generated
		ET.register_namespace('', "http://www.w3.org/1999/xhtml")
		ET.register_namespace('epub', "http://www.idpf.org/2007/ops")
		nav = ElementTree(ET.fromstring(NAV))

		# The style sheet's position is different in the simple case, so this has to be amended
		style = nav.findall(".//{http://www.w3.org/1999/xhtml}link[@rel='stylesheet']")[0]
		style.set("href", "Assets/base.css")

		# Set the title
		title = nav.findall(".//{http://www.w3.org/1999/xhtml}title")[0]
		title.text = self.document.title + " - Table of Contents"

		# Set the date
		date = nav.findall(".//{http://www.w3.org/1999/xhtml}meta[@name='date']")[0]
		date.set("content", self.document.date.strftime("%Y-%m-%dT%M:%S:00Z"))

		# The landmark part of the nav file has to be changed; there is no explicit cover page
		li_landmark = nav.findall(".//{http://www.w3.org/1999/xhtml}li[@href='cover.xhtml']")[0]
		li_landmark.set("href", "Overview.html")

		navMap = nav.findall(".//{http://www.w3.org/1999/xhtml}nav[@id='toc']")[0]

		h2 = SubElement(navMap, "{http://www.w3.org/1999/xhtml}h2")
		h2.text = "Table of Contents"

		ol = SubElement(navMap, "{http://www.w3.org/1999/xhtml}ol")
		li = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
		a = SubElement(li, "{http://www.w3.org/1999/xhtml}a")
		a.set("href", "cover.xhtml")
		a.text = "Cover"
		a.set("class", "toc")

		for toc_entry in self.document.toc:
			li = SubElement(ol, "{http://www.w3.org/1999/xhtml}li")
			a = SubElement(li, "{http://www.w3.org/1999/xhtml}a")
			a.set("href", toc_entry.href)
			a.text = toc_entry.short_label
			a.set("class", "toc")

		self.book.write_element('nav.xhtml', nav)
	# end _create_nav

	#========================
	# Generate the cover page
	#========================
	# noinspection PyPep8,PyPep8
	def _create_cover(self):
		"""
		Create a cover page: ``cover.xhtml``.
		"""
		# Setting the default namespace; this is important when the file is generated
		ET.register_namespace('', "http://www.w3.org/1999/xhtml")
		cover = ElementTree(ET.fromstring(COVER))

		# Set the title
		title      = cover.findall(".//{http://www.w3.org/1999/xhtml}title")[0]
		title.text = self.document.title

		# Set the authors in the meta
		editors      = cover.findall(".//{http://www.w3.org/1999/xhtml}meta[@name='author']")[0]
		editors.set("content", self.document.editors)

		# Set the title in the text
		title      = cover.findall(".//{http://www.w3.org/1999/xhtml}h1[@id='btitle']")[0]
		title.text = self.document.title

		# Set the subtitle in the text
		subtitle      = cover.findall(".//{http://www.w3.org/1999/xhtml}h2[@id='subtitle']")[0]
		subtitle.text = SUBTITLE[self.document.doc_type]

		# Set the editors
		editors      = cover.findall(".//{http://www.w3.org/1999/xhtml}p[@id='editors']")[0]
		editors.text = self.document.editors

		# Set a pointer to the original
		orig      = cover.findall(".//{http://www.w3.org/1999/xhtml}a[@id='ref_original']")[0]
		orig.set("href", self.document.dated_uri)

		# Set the subtitle
		if self.document.issued_as is not None:
			subtitle = cover.findall(".//{http://www.w3.org/1999/xhtml}h2[@id='subtitle']")[0]
			subtitle.text = self.document.issued_as

		# Set the correct copyright date
		span      = cover.findall(".//{http://www.w3.org/1999/xhtml}span[@id='cpdate']")[0]
		span.text = self.document.date.strftime("%Y")

		self.book.write_element('cover.xhtml', cover)




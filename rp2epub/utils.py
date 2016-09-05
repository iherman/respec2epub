# -*- coding: utf-8 -*-
"""
Various utility classes and methods.


Module Content
--------------

.. py:data:: logger

  A python logger instance (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance). Defaults to ``None``.

.. py:data:: TOC_PAIRS

  Array of tuples to help selecting the (top level) TOC entries; these are strings to be used in an XPath find. Because there
  has been several versions over the past, including Bikeshed and ReSpec versions, the array contains quite a number of
  variants. The tuple may contain a third string, denoting a specific class name on the target element that can be
  used to narrow the filter.

"""

from urllib2 import urlopen
from StringIO import StringIO
from datetime import date
import re
import os
import os.path
import shutil
from xml.etree.ElementTree import SubElement, ElementTree, tostring, fromstring
import zipfile
import html5lib

from .templates import meta_inf
from . import R2EError
import config

# logger (see the Python logging library for details). May be overwritten by the :py:class:`.DocWrapper` instance)
logger = None

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

#
# Table of content extraction
#
short_label_pattern = re.compile("^[1-9][0-9]*\. .*$")

# list of element pairs that lead to a table of content
# noinspection PyPep8
# structures for TOC elements in ReSpec or Bikeshed: element hierarchy and, if not None,
# the class name for the <li> element.
TOC_PAIRS = [
	("div[@id='toc']", "ul[@class='toc']", None),
	("div[@id='toc']", "ol[@class='toc']", None),
	("nav[@id='toc']", "ul[@class='toc']", None),
	("nav[@id='toc']", "ol[@class='toc']", None),
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

		# If we get here, the name does not abide to any pattern; it is taken to be a base document
		message = "Could not establish document type and/or short name from '%s' (remains \"base\")" % name
		Logger.warning(message)
		return "base", name
	# end create_shortname

	# noinspection PyBroadException
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
			Logger.error(message)
			return date.today()
	# end retrieve_date

	@staticmethod
	# noinspection PyBroadException
	def extract_editors(html):
		"""Extract the editors' names from a document, following the respec conventions
        (``@class=p-author`` for ``<dd>`` including ``<a>`` or ``<span>`` with ``@class=p-name``)

        Note that this is used only for older documents. Current respec reproduces the configuration in the target HTML file that can
        be used to extract the data directly.

        :param html: the object for the whole document
        :type html: :py:class:`xml.etree.ElementTree.ElementTree`
        :return: list of editors
        """
		retval = []

		for dd in html.findall(".//dd[@class]"):
			if dd.get('class').find('p-author') != -1:
				for a in dd.findall(".//a[@class]"):
					if a.get('class').find('p-name') != -1:
						if a.text not in retval:
							retval.append(a.text)
						break
				for span in dd.findall(".//span[@class]"):
					if span.get('class').find('p-name') != -1:
						if span.text not in retval:
							retval.append(span.text)
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
        Make the minimum changes necessary in the DOM tree so that the XHTML5 output is valid and accepted
        by epub readers. These are:

        1. The ``http://www.w3.org/1999/xhtml`` namespace is *required* in EPUB, but not generated by the
        XML serialization of Python's ElementTree (or the ``HTML5Lib`` implementation thereof?). It is therefore added explicitly.

        2. XHTML5 does not work with ``<script src="..."/>``, ie, with a self-closing element.
        Such elements are modified by adding a space to the content of the element.

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
         Changes on the DOM to ensure a proper interoperability of the display among EPUB readers. At the moment, the following actions are done:

         1. Due to the rigidity of the iBook reader, the DOM tree has to change: all children of the ``<body>`` should be
         encapsulated into a top level block element (we use ``<div role="main">``). This is because iBook imposes
         a zero padding on the body element, and that cannot be controlled by the user; the introduction of the top level
         block element allows for suitable CSS adjustments.

         The CSS adjustment is done as follows: the :py:data:`.templates.BOOK_CSS` is completed with the exact
         padding values; these are retrieved (depending on the TR version and the document) from the
         See the :py:data:`.config.PADDING_NEW_STYLE` and, if applicable, the :py:data:`.config.PADDING_OLD_STYLE`
         dictionaries. The expansion of :py:data:`.templates.BOOK_CSS` itself happens in the
         :py:meth:`.doc2epub.DocWrapper.process` method.

         Note that using simply a "main" element as a top level encapsulation is not a good approach, because some files
         (e.g., generated by Bikeshed) already use that element, and there can be only one of those…

         2. If a ``<pre>`` element has the class name ``highlight``, the Readium extension to
         Chrome goes wild. However, that class name is used only for an internal processing of ReSpec though it is
         unused in the various, default CSS content. As a an emergency measure this class name is simply removed from the code, although,
         clearly, this is not the optimal way:-( But hopefully this bug will disappear from Readium and this hack can be
         removed, eventually.

         **Note**: this is an `acknowledged bug in Readium <https://github.com/readium/readium-shared-js/issues/203>`__.
         When a newer release of Readium is deployed, this hack should be removed from the code.

         3. Some readers *require* to have a ``type="text/css"`` on the the link element for a CSS; otherwise the CSS
         is ignored. It is added (though not needed in HTML5, it doesn't do any harm either…)

         4. Add to the class of the ``body`` element the ``toc-inline`` value, to ensure that the TOC stays inline and
         is not floated on the left hand side. In reality, this is needed only for the post-2016 versions
         of the TR documents, but it does not harm for earlier versions. I.e., this step is not made more
         complicated by a check of the document’s TR version.

         5. Also like 4., remove the reference to the fixup.js script (which sets some initial values to the sidebar
         handling which is to be removed altogether anyway...)

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

		# Hack #4
		# Add 'toc-inline' to the body class, to avoid a floating TOC on the left
		bclass = body.get("class", None)
		if bclass is None:
			body.set("class", "toc-inline")
		else:
			classes = bclass.split()
			if "toc-inline" not in classes:
				classes.append("toc-inline")
			body.set("class", " ".join([c for c in classes if c != "toc-sidebar"]))

		# Hack #5
		for script in html.findall(".//script[@src]"):
			if script.get("src").endswith("fixup.js"):
				# The ElementTree.Element interface makes it difficult to locate the parent
				# which would be necessary to remove this element (why????)
				# The hack simply removes the fixup.js reference by just issuing a reset to the element itself
				script.clear()
				script.text = " "

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

            :param parent: the parent element for the TOC entry
            :type parent: :py:class:`xml.etree.ElementTree.Element`
            :param explicit_num: whether the first element of the TOC line is a numbering that should be removed
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
            Extract the TOC items following ReSpec or Bikeshed conventions. There are
            possible pairs (see the ``TOC_PAIRS``
            alternatives), yielding <li> elements with the toc entry.
            """
			# respec version
			# We have to try two different versions, because, in some cases, respec
			# uses 'div' and in other cases 'section'
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

		def toc_extract_nav():
			"""
            Extract a full hierarchy of navigation element, to be reused for the new style, ie, EPUB3, navigation,
            if possible. That relies on a restricted set of toc pairs that the original document may contain
            :return: array of elements, cloned version of the top level ``<li>`` elements in the original source. The array is empty if the TOC structure is inadequate
            """
			top_levels = []

			# See if the new style nav/ul access works
			xpath = ".//nav[@id='toc']/ul[@class='toc']"
			toc = html.findall(xpath)
			if len(toc) > 0:
				for li in toc[0].findall("li"):
					li_in_string = tostring(li, encoding="utf-8", method="xml")
					# making some changes for the nav element and then turn it back to an Element tree
					cloned_li = fromstring(li_in_string.replace('<ul','<ol').replace('</ul>','</ol>'))
					for a in cloned_li.findall(".//a"):
						ref = a.get("href")
						ref = "Overview.xhtml" + ref if ref[0] == '#' else ref.replace(".html", ".xhtml", 1)
						a.set("href", ref)
					top_levels.append(cloned_li)

			return top_levels

		# Execute the various versions in order
		if toc_respec_or_bikeshed():
			# we are fine, found what is needed
			return retval, toc_extract_nav()
		else:
			# if we got here, something is wrong...
			Logger.warning("Could not extract a table of content from '%s'" % short_name)
			return [], []

	@staticmethod
	def editors_to_string(names, editor = True):
		"""
        Return a string of names generated from a list of names, with correct punctuation, and a suffix denoting whether these are editors or authors

        :param names: list of strings, each entry a name to be used in the final output
        :keyword editor: if True, the string '(editor)' or '(editors)' is appended to the list (depending on cardinality), '(author)', resp. '(authors)' otherwise
        :return: a string that can be used as a final display for the names of editors/authors.
        """
		if len(names) == 0:
			return ""
		elif len(names) == 1:
			return names[0] + (" (Editor)" if editor else " (Author)")
		elif len(names) == 2:
			return names[0] + " and " + names[1] + (" (Editors)" if editor else " (Authors)")
		else:
			return "; ".join(names[:-1]) + "; and " + names[-1] + (" (Editors)" if editor else " (Authors)")


###################################################################################
class HttpSession(object):
	# noinspection PyPep8
	"""
    Wrapper around an HTTP session; the returned media type is compared against accepted media types.

    :param str url: the URL to be retrieved
    :param boolean check_media_type: whether the media type should be checked against the media type of the resource to see if it is acceptable
    :param boolean raise_exception: whether an exception should be raised if the document cannot be retrieved (either because the HTTP return is not 200, or not of an acceptable media type)
    :param boolean is_respec: if True, the URL is a callout to the spec generator service; if so, and there is a problem, the corresponding error message is different
    :raises R2EError: in case the file is not an of an acceptable media type, or the HTTP return is not 200
    """
	# noinspection PyPep8,PyPep8
	def __init__(self, url, check_media_type=False, raise_exception=False, is_respec=False):
		def handle_exception(message):
			Logger.error(message)
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
			if is_respec:
				handle_exception("There seems to be a problem with the spec generator service ('%s' should be tested separately)" % url)
			else:
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
	"""Abstraction for a book; it encapsulates a zip file as well as saving the content into a directory.

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
        Write the content of a string.

        :param target: path for the target file
        :param content: string/bytes to be written on the file
        :param compress: either ``zipfile.ZIP_DEFLATED`` or ``zipfile.ZIP_STORED``, whether the content should be compressed, resp. not compressed
         """
		# Care should be taken not to write the "target" twice; the zipfile would really
		# duplicate the content in the archive (as opposed to file writing that would simply overwrite the previous
		# incarnation of the same file). This method takes care of that through the `already_stored` array.
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
	def write_session(self, target, session, css_change_patterns = None):
		"""
        The returned content of an :py:class:`.HttpSession` is added to the book. If the content is an HTML file, it will be converted into XHTML on the fly.

        :param str target: path for the target file
        :param session: a :py:class:`.HttpSession` instance whose data must retrieved to be written into the book
        :param css_change_patterns: a list of ``(from,to)`` replace patterns to be applied on CSS files before storage
        :return boolean: the value of session.success
        """
		if css_change_patterns is None :
			css_change_patterns = []

		# Copy the content into the final book
		# Special care should be taken with html files. Those are supposed to become XHTML:-(
		if not session.success:
			Logger.info("Unsuccessful HTTP session; did not store %s" % session.url)
		else:
			if session.media_type == 'text/html':
				# We have to
				# 1. parse the source with the html5 parser
				# 2. add the xhtml namespace to the top and take care of the stupid script issue (no self-closing scripts!)
				# 3. write the result as xhtml through the write_element method
				html = html5lib.parse(session.data, namespaceHTMLElements=False)
				Utils.html_to_xhtml(html)
				self.write_element(target.replace('.html', '.xhtml', 1), ElementTree(html))
			elif session.media_type == 'text/css':
				# We have to make a series of string replacements, as defined in the `css_change_patterns`
				# parameter.
				content = session.data.read()
				for (c_from, c_to) in css_change_patterns:
					content = content.replace(c_from, c_to)
				self.writestr(target, content)
			else:
				# Note that some of the media types are not to be compressed
				self.writestr(target, session.data.read(), zipfile.ZIP_STORED if session.media_type in _NO_COMPRESS else zipfile.ZIP_DEFLATED)
		return session.success

	# noinspection PyPep8Naming
	def write_HTTP(self, target, url):
		"""
        Retrieve the content of a URI and store it in the book. (This is a wrapper around the `write_session` method.)

        :param str target: path for the target file, this is always a relative URI
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

	# The methods below are necessary to use the class in a "with ... as" python structure
	def __enter__(self):
		return self

	# noinspection PyUnusedLocal
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

#####################################################################################


# noinspection PyPep8
class Logger(object):
	"""
    Wrapper around the logger calls, simply checking whether the logger in the configuration file has been
    set to a real value or whether it is None (in the latter case nothing happens). Saves a repeated
    set of checks elsewhere in the code.
    """

	@staticmethod
	def warning(message):
		if logger is not None:
			logger.warning(message)

	@staticmethod
	def error(message):
		if logger is not None:
			logger.error(message)

	@staticmethod
	def info(message):
		if logger is not None:
			logger.info(message)

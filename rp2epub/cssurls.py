"""
Handling information referred to in CSS files or `<style>` elements.

The :py:class:`CSSList` encapsulates a collection of external references that are extracted from CSS files, references
that are supposed to be downloaded and added to the final book, as well as added to the package file. Typically, this
means handling the CSS import statements (i.e., importing other CSS files) as well as various uri references, e.g., when
setting the content or the background of an element using an image.

Note: content negotiation may not work: if, say, a `url(figureref)` relies on content negotiations, it may not generate
the right statements (not sure whether reading systems would work without the proper file extensions, for example).
Doing this safely would be to add the suffix to the downloaded file name for the local name, and modify the CSS files.
This is not done at the moment (the `tinycss` library is not prepared, afaik, to write CSS files, only to read and
parse them).

.. :class::

Module content
--------------
"""

# TODO: documentation

from urlparse import urljoin, urlparse
import tinycss
from .utils import HttpSession, Logger
import sys


class _URLPair:
	"""
	Just a simple wrapper around a pair of (absolute) url, and a local name. Instead of being a pair, the
	values can then be accessed via property names (and not via array/dictionary syntax).

	:param str url: Absolute URL of the resource
	:param str name: Local name of the resource
	"""
	# noinspection PyPep8
	def __init__(self, url, name):
		self._url  = url
		self._name = name

	@property
	def url(self):
		"""The absolute URL of the resource"""
		return self._url

	@property
	def name(self):
		"""The local name of the resource"""
		return self._name

	def __repr__(self):
		return "(" + self.name + ", " + self.url + ")"


# noinspection PyPep8
class CSSReference:
	"""
	Wrapper around the information necessary in one CSS reference.

	:param str base: Base URI of the overall book. Important to generate proper local name for a resource when retrieved
	:param str url: URL of the CSS file (if any, otherwise value is ignored). This is an absolute URL; in practice can be using the overall book URL or www.w3.org
	:param boolean is_file: whether the CSS is to be retrieved via the URL or whether it was embedded
	:param str content: in case the CSS was embedded, the full content of the CSS as retrieved from the DOM
	"""
	# noinspection PyPep8
	def __init__(self, base, url, is_file = True, content = None):
		self._origin_url = url
		self._base       = base
		if is_file:
			session = HttpSession(url, check_media_type=True)
			if session.success:
				self._content = session.data.read()
			else:
				self._content = ""
		else:
			self._content = content
		self._collect_imports()

	@property
	def empty(self):
		"""A boolean value whether the content is empty (in which case it can be ignored) or not"""
		return self._content is None or len(self._content) == 0

	@property
	def import_css(self):
		"""Set of URL-s for additional CSS files, ie, values of ``@import`` rules"""
		return self._import_css

	@property
	def import_misc(self):
		"""Set of :py:class:`_URLPair` instances for resources that were found in the CSS content"""
		return self._import_misc

	def _collect_imports(self):
		"""Collect the resources to be imported. The CSS content is parsed, and the :py:attr:`import_css`
		and :py:attr:`import_misc` sets are filled with content. This method is called at initialization time.
		"""
		def add_item_to_import(url_orig, css=False):
			# The urls-s are relative to the CSS file's
			url = urljoin(self._origin_url, url_orig)
			# The final name, to be used when the content is added to the book, should be relative to the
			# base of the whole input; that will then be used to add the downloaded
			# content to the book

			# The style sheets may be on the www.w3.org domain. Those should be separated for the generation of the
			# local name...
			if urlparse(url).netloc == "www.w3.org":
				path = urlparse(url).path
				name = path if path[0] != '/' else path[1:]
			else:
				name = url.replace(self._base, '', 1)

			self._import_misc.add(_URLPair(url, name))
			if css:
				self._import_css.add(url)

		def handle_one_css_ruleset(ruleset):
			# This is a basic CSS set of declarations. Each declaration has, potentially, a set of values;
			# the values themselves may be numbers, strings, etc, and also URI-s
			# Only the URI-s are of interest at this point.
			if ruleset.at_keyword is None:
				for d in ruleset.declarations:
					for i in [item for item in d.value if item.type == "URI"]:
						add_item_to_import(i.value)


		self._import_css  = set()
		self._import_misc = set()
		parser = tinycss.make_parser("page3")

		if self._content is not None:
			stylesheet = parser.parse_stylesheet(self._content)
			# Log if there is an error in the stylesheet
			if stylesheet.errors is not None and len(stylesheet.errors) > 0:
				Logger.warning("The tinycss parser found some CSS errors in %s" % self._origin_url)

			# Go through all the individual rules of the style sheet
			for rule in stylesheet.rules:
				# Only the @import and @media rules are of interest; most of the others, like @print, are ignored
				if rule.at_keyword == "@import":
					add_item_to_import(rule.uri, css=True)

				elif rule.at_keyword == "@media":
					for ruleset in rule.rules:
						handle_one_css_ruleset(ruleset)

				elif rule.at_keyword is None:
					handle_one_css_ruleset(rule)

	def __repr__(self):
		return self._origin_url + ': ' + `self.import_css` + "," + `self.import_misc`


# noinspection PyPep8
class CSSList:
	"""
	List of :py:class:`CSSReference` instances. This is, initially, built up from the :py:class:`.document.Document` class; when
	the final information is requested, a recursion is done on the collected CSS file references to collect all
	outstanding resources.

	:param str base: the base URL for the whole book
	"""
	def __init__(self, base):
		self._css_list = []
		self._base     = base

	def add_css(self, origin_url, is_file=True, content=None):
		"""Add a new CSS, ie, add a new :py:class:`CSSReference` to the internal array of references
		:param str origin_url: URL of the CSS file (if any, otherwise value is ignored)
		:param boolean is_file: whether the CSS is to be retrieved via the URL or whether it was embedded
		:param str content: in case the CSS was embedded, the full content of the CSS
		"""
		css_ref = CSSReference(self._base, urljoin(self._base, origin_url), is_file, content)
		if not css_ref.empty:
			self._css_list.append(css_ref)

	def get_download_list(self):
		"""Return all the list of resources. These include those explicitly added previously, plus those retrieved
		recursively.

		:return: Array of ``(local_name, absolute_url)`` pairs.
		"""
		self._gather_all_stylesheets()
		final_download_list = set()
		for c in self._css_list:
			for d in c.import_misc:
				final_download_list.add((d.name, d.url))
		return list(final_download_list)

	def _gather_all_stylesheets(self):
		def one_level(css_references):
			"""
			Recursive step to gather all resources to be downloaded: goes through the list of css references and tries to
			access the next level of css references for further inclusion.

			@param css_references: an array of :py:class:`CSSReference` instances.
			"""
			next_level = []
			for css in css_references:
				for url in css.import_css:
					new_css_ref = CSSReference(self._base, urljoin(self._base, url))
					if not new_css_ref.empty:
						next_level.append(new_css_ref)
			if len(next_level) != 0:
				next_level += one_level(next_level)
			return next_level
		self._css_list += one_level(self._css_list)

	def __repr__(self):
		retval = ""
		for c in self._css_list:
			retval += c.__repr__() + '\n'
		return retval
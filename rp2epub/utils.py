# -*- coding: utf-8 -*-
from urllib2 import urlopen, HTTPError
from StringIO import StringIO
import zipfile
from ..utils import _NO_COMPRESS


###################################################################################
class HttpSession:
	"""
	Wrapper around an HTTP session; the returned media type is compared against accepted media
	types.

	:param str url: the URL to be retrieved
	:param array accepted_media_type: and array of media type strings giving a list of those that should be added to the book
	:param boolean raise_exception: whether an exception should be raised if the document cannot be retrieved (either because the HTTP return is not 200, or not of an acceptable media type)
	:raises Exception: in case the file is not an HTML file, or the HTTP return is not 200
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
				raise Exception("Received a '%s' file, not HTML" % self._media_type)
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


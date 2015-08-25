# -*- coding: utf-8 -*-
"""
Get an HTML document in `ReSpec <http://www.w3.org/respec/>`_, or an HTML document generated by `ReSpec <http://www.w3.org/respec/>`_,
and generate an EPUB3 file for off-line reading. For further details on respec, see also the
`ReSpec User guide <http://www.w3.org/respec/guide.html>`_. If the source is in ReSpec, the file is ran through
the `Spec Generator service at W3C <https://labs.w3.org/spec-generator/>`_

Stylesheets and images are downloaded and included in the book, provided they are on the same Web domain as the
original file (i.e., in Python's URL library speak, if the URL-s of those resources have the same net location,
i.e., ``netloc``).

The result is an EPUB3 in, by default, the same folder, whose name is the last part of the URI, expanded with
the ``.epub`` suffix.

There is a possibility to generate the EPUB3 content in expanded form (i.e., in a directory instead of an EPUB file),
or both. This may be useful for debugging, but also to inspect and possibly adapt the EPUB3 file before
distribution.

The program depends on the html5lib library for HTML parsing.

"""
__version__ = "0.8"
# noinspection PyPep8
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>'


class R2EError(Exception):
	"""
	rp2epub specific Exception class
	"""
	pass

from .doc2epub import DocWrapper

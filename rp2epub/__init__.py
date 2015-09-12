# -*- coding: utf-8 -*-
__version__ = "1.1"
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

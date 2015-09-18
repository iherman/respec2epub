# -*- coding: utf-8 -*-

__version__ = "1.1"
# noinspection PyPep8
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>'

class R2EError(Exception):
	"""
	rp2epub specific Exception class; used to wrap normal exceptions, without adding any functionality.
	"""
	pass

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

from .doc2epub import DocWrapper

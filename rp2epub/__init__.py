# -*- coding: utf-8 -*-
import locale

__version__ = "1.3"
# noinspection PyPep8
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/copyright-software>'


class R2EError(Exception):
	"""
	rp2epub specific Exception class; used to wrap normal exceptions, without adding any functionality.
	"""
	pass

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

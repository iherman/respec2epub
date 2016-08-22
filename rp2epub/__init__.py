# -*- coding: utf-8 -*-
import locale

__version__ = "1.4"
# noinspection PyPep8
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/copyright-software>'


class R2EError(Exception):
	"""
	rp2epub specific Exception class; used to wrap normal exceptions, without adding any real functionality, just storing the value.
	"""
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

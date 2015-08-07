# -*- coding: utf-8 -*-
__version__ = "0.5"
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>'

from .doc2epub import DocToEpub
import warnings
warnings.formatwarning = lambda message, category, filename, lineno, line: "%s: %s\n" % (category.__name__, message)

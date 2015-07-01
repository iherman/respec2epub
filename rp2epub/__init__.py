# -*- coding: utf-8 -*-
__version__ = "1.5"
__author__  = 'Ivan Herman, W3C'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C SOFTWARE NOTICE AND LICENSE <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>'

import argparse
from .doc2epub import DocToEpub
import warnings
warnings.formatwarning = lambda message, category, filename, lineno, line: "%s: %s\n" % (category.__name__, message)


def process():
	"""
	Command line intereface; only one argument is used, ie, the URI for the document
	"""
	parser = argparse.ArgumentParser(description="Generate an EPUB3 file from a Web Page")
	parser.add_argument("URI", help="URI of the resources to be retrieved. Must be a reference to an HTML file")
	args = parser.parse_args()
	DocToEpub(args.URI).process()


#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import urllib
import datetime
import traceback

# To ensure the right format for the dates
import locale
locale.setlocale(locale.LC_ALL, 'en_us')

##########################################
# Global boolean flag to decide whether this is a CGI script or not (the non-cgi case is for debugging)
# If it is not cgi, then an artificial environment is created for debugging.
cgi = 'HTTP_USER_AGENT' in os.environ
# noinspection PyPep8
if cgi is not True:
	# noinspection PyPep8
	os.environ['QUERY_STRING'] = 'type=html&url=http://localhost:8001/LocalData/github/csvw/publishing-snapshots/CR-csv2json/Overview.html'
	# os.environ['QUERY_STRING'] = 'type=respec&url=http://w3c.github.io/csvw/csv2rdf/?publishDate=2015-07-16;specStatus=CR'

##########################################
# If it is a cgi script then the python distribution may not include what is needed for import... Then import the
# generator library
# noinspection PyPep8
if cgi:
	# The import path should include the place where my library resides
	# Depending on settings and environments, this may have to be adapted to various situations...
	if os.environ['HTTP_HOST'] == 'localhost:8001':
		# this is my local machine
		sys.path.insert(0, "/Users/ivan/Library/Python")

import rp2epub

##########################################
# Set up a logger. This may be useful if something goes wrong with the server...
# However, the failing to set up the logger should not interrupt to program in general, hence all this in an exception
# noinspection PyBroadException,PyPep8
try:
	import logging
	import logging.handlers
	# Set the logger part
	logger = logging.getLogger("Epub generator")
	logger.setLevel(logging.DEBUG)

	# Set the handler; this handler provides a way to limit the file size, and also gives a rollover
	# TODO: when going for a real deployment, the maxBytes argument should be set to, say, 100000 (or more?) and backupCount to 10
	handler = logging.handlers.RotatingFileHandler(filename="/tmp/logs/epub_generator.log", maxBytes=3000, backupCount=2)
	handler.setLevel(logging.DEBUG)

	# create and add a formatter
	# noinspection PyPep8
	handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))

	# done...
	logger.addHandler(handler)
except:
	logger = None


##########################################
# Various utility functions

def now():
	"""
	Return the current date and time in the format required by HTTP headers
	:return: string of current date and time
	"""
	return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def respond(wrapper, modified):
	"""
	Generate the full HTTP response
	:param wrapper: Wrapper around the document conversion; a :py:class:`rp2epub.DocWrapper` instance
	:param modified: time stamp to be added to the response, through the 'Last-Modified' header response field
	:return:
	"""
	if cgi:
		print "Content-type: application/epub+zip"
		print "Last-Modified: %s" % modified
		print "Expires: %s" % now()
		print "Content-Length: %s" % os.stat(wrapper.book_file_name).st_size
		print "Content-Disposition: attachment; filename=%s" % wrapper.document.short_name + ".epub"
		print
		with open(wrapper.book_file_name) as book:
			print book.read()
		if cgi and logger is not None:
			logger.info("%s generated and returned" % (wrapper.document.short_name + ".epub"))
	else:
		print wrapper.book_file_name


class Generator:
	# noinspection PyPep8
	def __init__(self):
		"""
		Extract the query string value of interest. Note that the usual Python FieldStorage class cannot be used,
		because the url argument may be a query string by itself (this is due to the peculiarities of respec, ie,
		the fact that one can use URLs with query string to override the respec config data).
		"""
		self.args = {
			'url'   : "",
			'respec': False
		}
		if 'QUERY_STRING' in os.environ:
			call_args = {}
			for arg in os.environ['QUERY_STRING'].split('&'):
				current = arg.split('=', 1)
				if len(current) > 1:
					call_args[current[0]] = current[1]

			if 'type' in call_args:
				self.args['respec'] = True if call_args['type'].lower() == 'respec' else False

			if 'url' in call_args:
				self.args['url'] = urllib.unquote(call_args['url'])
			elif 'uri' in call_args:
				self.args['url'] = urllib.unquote(call_args['uri'])

		if cgi and logger is not None:
			logger.info("respec:%s; url=%s" % (self.args['respec'], self.args['url']))

	def generate_ebook(self):
		"""
		Interface to the real ebook generation; test setup for now
		:return: file name for the final book
		"""
		# Generate the EPUB in the external library
		# noinspection PyPep8
		return rp2epub.DocWrapper(self.args['url'], is_respec=self.args['respec'], package=True, folder=False, temporary=True).process()

	def process(self):
		"""
		Full process of EPUB generation
		"""

		# Start of EPUB generation, this will set the 'last modified' header field in the response
		modified = now()

		# The real 'meat': EPUB generation
		wrapper = self.generate_ebook()

		# Return the HTTP result
		respond(wrapper, modified)

		# The file must be removed...
		if cgi and os.path.exists(wrapper.book_file_name):
			os.remove(wrapper.book_file_name)


########################
# noinspection PyBroadException
try:
	# GO!
	Generator().process()
except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	if cgi:
		if logger is not None:
			# The error should be logged...
			from StringIO import StringIO
			err = StringIO()
			traceback.print_exception(exc_type, exc_value, exc_traceback, file=err)
			logger.critical("Exception has been raised:\n" + err.getvalue())
			err.close()

		# ...and returned
		print 'Status: 500'
		print 'Content-Type: text/html; charset=utf-8'
		print
		print "<html>"
		print "<head>"
		print "<title>Epub Generator Exception</title>"
		print "</head><body>"
		print "<h1>Epub Generator Exception</h1>"
		print "<pre>"
		traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
		print "</pre>"
		print "</body></html>"
	else:
		traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)



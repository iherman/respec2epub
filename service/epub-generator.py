#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, os.path
import urllib
import tempfile
import zipfile
import datetime

# To ensure the right format for the dates
import locale
locale.setlocale(locale.LC_ALL, 'en_us')

# Global boolean flag to decide whether this is a CGI script or not; for debugging
cgi = 'HTTP_USER_AGENT' in os.environ
if not cgi:
	os.environ['QUERY_STRING'] = 'type=respec&url=http://w3c.github.io/csvw/csv2rdf/?publishDate=2015-07-16;specStatus=CR'


def now():
	"""
	Return the current date and time in the format required by HTTP headers
	:return: string of current date and time
	"""
	return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def getargs():
	"""
	Extract the query string value of interest. Note that the usual Python FieldStorage class cannot be used,
	because the url argument may be a query string by itself (this is due to the peculiarities of respec, ie,
	the fact that one can use URLs with query string to override the respec config data).

	:return: a directory containing the 'respec' and 'url' fields.
	"""
	retval = {
		'url'    : "",
		'respec' : False
	}
	if 'QUERY_STRING' in os.environ:
		args = {}
		for arg in os.environ['QUERY_STRING'].split('&'):
			current = arg.split('=', 1)
			if len(current) > 1:
				args[current[0]] = current[1]

		if 'type' in args:
			val = args['type'].lower()
			retval['respec'] = True if val == 'respec' else False

		if 'url' in args:
			retval['url'] = urllib.unquote(args['url'])
		elif 'uri' in args:
			retval['url'] = urllib.unquote(args['uri'])
	return retval


def respond(file_name, modified):
	"""
	Generate the full HTTP response
	:param file_name: name where the EPUB3 can be found
	:param modified: time stamp to be added to the response, through the 'Last-Modified' header response field
	:return:
	"""
	if cgi:
		print "Content-type: application/epub+zip"
		print "Last-Modified: %s" % modified
		print "Expires: %s" % now()
		print "Content-Length: %s" % os.stat(file_name).st_size
		print
		with open(file_name) as book:
			print book.read()
	else:
		print file_name


def generate_ebook(args):
	"""
	Interface to the real ebook generation; test setup for now
	:return: file name for the final book
	"""
	# Generate the EPUB in the external library
	# Testing the temporary file creation and return...
	# Create a temporary file that will be used for the epub file
	file_name = tempfile.mkstemp(suffix="_testbook.epub")[1]

	# Fake EPUB generation
	zip = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
	zip.writestr("f1.txt", 'namivan')
	zip.writestr("f2.txt", 'ez van')
	zip.close()
	#######

	# FAKE!!!!!!!
	return '/Users/ivan/W3C/WWW/LocalData/test/csv2json.epub'


def process():
	"""
	Full process of EPUB generation
	"""
	# Get the call arguments
	args = getargs()

	# Start of EPUB generation, this will set the 'last modified' header field in the response
	modified  = now()
	file_name = generate_ebook(args)

	# Return the HTTP result
	respond(file_name, modified)

	# The file must be removed...
	if os.path.exists(file_name):
		pass
		#os.remove(file_name)


########################
# GO!
process()
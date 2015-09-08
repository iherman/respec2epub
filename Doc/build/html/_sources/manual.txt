.. Respec to EPUB documentation master file, created by
   sphinx-quickstart on Wed Aug 12 15:42:46 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Command line tool manual
========================


When using the command line tool, the result is an EPUB3 file in, by default, the same folder, and whose name is the
short name of the document expanded with the ``.epub`` suffix.

There is a possibility to generate the EPUB3 content in expanded form (i.e., in a directory instead of an EPUB file),
or both. This may be useful for debugging, but also to inspect and possibly adapt the EPUB3 file before
distribution.


This script that can be invoked from the command as follows::

    usage: rp2epub [-h] [-r] [-b] [-f] [-t] url

    Generate EPUB3 for a single W3C TR document, either in respec format (default)
    or generated from respec.

    positional arguments:
        url           URL of the input; if this is in respec, it will passed on to
                      the spec generator verbatim

    optional arguments:
      -h, --help      show this help message and exit
      -r, --respec    The source is a ReSpec file, transform it before processing
      -b, --book      Create an EPUB3 package
      -f, --folder    Create a folder with the book content
      -t, --tempfile  Create a one-time, temporary name for the EPUB3 file
      -l, --logging   Log events in the local file 'log'


(The last two optional arguments are of a real interest for debugging only.)


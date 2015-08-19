.. Respec to EPUB documentation master file, created by
   sphinx-quickstart on Wed Aug 12 15:42:46 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Command line tool manual
========================

This is a simple script that can be invoked from the command line. Usage of the command is::

    usage: rp2epub [-h] [-r] [-b] [-f] [-t] url

    Generate EPUB3 for a single W3C TR document, either in respec format (default)
    or generated from respec.

    positional arguments:
        url           URL of the input; if this is in respec, it will passed on to
                      the spec generator verbatim

    optional arguments:
      -h, --help      show this help message and exit
      -r, --respec    The source is a respec file, transform it before processing
      -b, --book      Create an EPUB3 package
      -f, --folder    Create a folder with the book content
      -t, --tempfile  Create a one-time, temporary name for the EPUB3 file



Miscellaneous issues, to-do items
=================================

Note on the handling of CSS files
---------------------------------

A minor complication arises when handling official CSS files for documents. The current CSS file structure relies on
document type specific CSS files; these (usually) include a common CSS file (``base.css``) and set the background
image to the “logo”, ie, the vertical, coloured bar on the upper left hand corner of the document. Following the same
structure would have required the script to parse CSS files to locate the various ``url`` statements, modify them and, to
download the corresponding logos into the book. Instead, the script relies on directly linking to (a local copy of)
``base.css``, and establishing the document status from the document itself. Using that status information, plus
a per-document-status mapping (see :py:data:`.config.DOCTYPE_INFO`), the corresponding logo files can be found.

This mechanism is a little bit fragile, because it relies on establishing the document status (which is not always obvious, see
issue below). However, it avoided having a separate CSS parser. Time will tell whether this was a wise choice…


Bikeshed issues
---------------

The core of the code has been developed with ReSpec in mind, although attempts have been made to work with
`Bikeshed <https://wiki.csswg.org/tools/bikeshed>`_, too. There, however, cases where this does not work properly. The
most notable issue is to establish the “dated URI” of the document, which can be used to retrieve the document status
(``ED``, ``WD``, etc.) which is then used to download the right logo for the background, for example. In the case of ReSpec
this information can either be found in the ReSpec configuration data that is added to the output of ReSpec processing (for
later versions of ReSpec) or can be located by looking for a ``<a>`` element with class name ``u-url``. This is consistent
with ReSpec and the class name based approach also works with *some* documents produced by Bikeshed. However, only some,
and not all; there are documents where the relevant URI is not annotated with any specific class (or alternatives). A finer
analysis of the source may be used to locate that value, but this version of the script does not do that.

To Do-s
-------

- Do a better job with Bikeshed

- Multi-file documents: some W3C documents are a collection of files. Examples are the `HTML5 <http://www.w3.org/TR/2014/REC-html5-20141028/>`_ or `SVG <http://www.w3.org/TR/2011/REC-SVG11-20110816/>`_ SVG specifications. These are not handled by the current script. This may require a more thorough review of the code, but would also require a “standard” way of denoting the order of the files (e.g., a systematic usage of the ``rel=next`` attribute in the header).



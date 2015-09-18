Miscellaneous issues, to-do items
=================================

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



# -*- coding: utf-8 -*-
"""
Templates, i.e., "scaffold" XML/CSS content; these are finalized, and then added to the book,
by the :py:class:`.Package` instance.

.. py:data:: meta_inf

  XML code for the Manifest file

.. py:data:: NAV

  XHTML code for the new type EPUB3 table of content file

.. py:data:: TOC

  XML code for the old type EPUB2 table of content file

.. py:data:: PACKAGE

  XML code for the package file (``opf`` file)

.. py:data:: COVER

  XHTML code for the cover page

.. py:data:: BOOK_CSS

  Content of the ``book.css`` file, adding some page-breaking statements to the overall styling.

**Source code:** `utils.py <https://github.com/iherman/respec2epub/blob/master/rp2epub/templates.py>`_

"""

#######################################################################################################
meta_inf = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
	<rootfiles>
		<rootfile full-path="package.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
"""

NAV = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
        <title>
            Contents
        </title>
        <meta name="date" />
        <link rel="stylesheet" type="text/css" href="StyleSheets/TR/base.css" />
        <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type" />
        <style>
            ol {
                counter-reset: section;
                list-style-type: none;
            }
            li:before {
                counter-increment: section;
                content: counters(section, ".") " ";
            }
        </style>
    </head>
    <body>
        <nav epub:type="toc" id="toc">
        </nav>
        <nav epub:type="landmarks" id="landmarks">
          <ol epub:type="list">
            <li epub:type="bodymatter" href="cover.xhtml">Begin reading</li>
            <li epub:type="toc" href="toc.xhtml">Table of Contents</li>
          </ol>
        </nav>
    </body>
</html>
"""

TOC = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
	<head>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
		<meta name="dtb:uid" />
	</head>
	<docTitle></docTitle>
  <docAuthor></docAuthor>
  <navMap>
    <navPoint class="h1" id="cover" playOrder="1">
      <navLabel><text>Cover</text></navLabel>
      <content src="cover.xhtml"/>
    </navPoint>
    <navPoint class="h1" id="toc" playOrder="2">
      <navLabel><text>Table of Contents</text></navLabel>
      <content src="toc.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
"""

# noinspection PyPep8
PACKAGE = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" xml:lang="en" unique-identifier="pub-id" prefix="cc: http://creativecommons.org/ns#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title id="title" />
    <meta refines="#title" property="title-type">main</meta>
    <dc:creator id="creator"></dc:creator>
    <dc:identifier id="pub-id" />
    <dc:language>en-US</dc:language>
    <meta property="dcterms:modified" />
    <dc:publisher>World Wide Web Consortium</dc:publisher>
    <meta property="dcterms:date" />
    <dc:rights>http://www.w3.org/Consortium/Legal/2002/ipr-notice-20021231#Copyright</dc:rights>
    <link rel="cc:license" href="http://www.w3.org/Consortium/Legal/2002/ipr-notice-20021231#Copyright"/>
    <meta property="cc:attributionURL">http://www.w3.org</meta>
  </metadata>
  <manifest>
  </manifest>
  <spine  toc="ncx">
        <itemref idref="start"/>
        <itemref idref="toc" />
  </spine>
</package>
"""

# noinspection PyPep8
COVER = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html lang="en-us" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <title></title>
    <meta name="author" content="" />
    <link type="text/css" rel="stylesheet" href="Assets/base.css" />
    <style type="text/css">
	  body {
		padding: 0 0 0 0 !important;
	  }

	  div[role~="main"] {
		padding: 2em 2em 2em 2em;
	  }
      h1 {
        text-align: center !important;
        font-size: 250%;
      }
      h2 {
        text-align: center !important;
        font-size: 140%;
        font-style: italic;
      }
      h3 {
        text-align: center !important;
        font-size: 140%;
        font-style: italic;
      }
      p.larger {
        font-size: 120%;
      }
      div#title {
        text-align: center;
        margin-top: 3em;
      }
      p.logo {margin-top:2em; text-align:center}
      p.disclaimer {
        font-style:italic;
      }
      ol { text-align: left !important;}
      a { text-decoration: none !important}

    </style>
  </head>
  <body>
    <div id="title" role="main">
      <h1 id="btitle"></h1>
      <h2 id="subtitle"></h2>
      <p class="larger" id="editors"></p>
      <p class="larger" id="authors"></p>
      <p class="logo"><a href="http://www.w3.org/"><img alt="W3C main logo" src="Assets/w3c_main.png"/></a></p>
      <p class="disclaimer">Note: this EPUB edition does <em>not</em> represent the authoritative text of the specification; please consult the <a id="ref_original">original document</a> on the W3C Web Site.</p>
      <p class="copyright"><a href="http://www.w3.org/Consortium/Legal/ipr-notice#Copyright">Copyright</a>
      © of the original documents: <span id="cpdate"></span> W3C<sup>®</sup> (<a href="http://www.mit.edu">MIT</a>, <a href="http://www.ercim.eu/">ERCIM</a>,
      <a href="http://www.keio.ac.jp/">Keio</a>, <a href="http://ev.buaa.edu.cn/">Beihang</a>).<br/>
      All right reserved. W3C <a href="http://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer">liability</a>,
      <a href="http://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks">trademark</a>,
      and <a href="http://www.w3.org/Consortium/Legal/copyright-documents">document use</a> rules apply.</p>
    </div>
  </body>
</html>
"""

BOOK_CSS = """
  body {
    %s
    padding: 0 0 0 0 !important;
  }

  div[role~="main"] {
    padding: %s
  }

  h2 {
    page-break-before: always;
    page-break-inside: avoid;
    page-break-after: avoid;
  }

  div.head h2 {
    page-break-before: auto;
    page-break-inside: avoid;
    page-break-after: avoid;
  }

  h3, h4, h5 {
    page-break-after: avoid;
  }

  dl dt {
    page-break-after: avoid;
  }

  dl dd {
    page-break-before: avoid;
  }

  div.example, div.note, pre.idl, .warning, table.parameters, table.exceptions {
    page-break-inside: avoid;
  }

  p {
    orphans: 4;
    widows: 2;
  }
"""
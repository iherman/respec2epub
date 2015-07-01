# -*- coding: utf-8 -*-
"""
Templates, i.e., "scaffold" XML/CSS content; these are finalized, and then added to the book,
by the :py:class:`.Package` instance.

.. py:data:: meta_inf

  XML code for the Manifest file

.. py:data:: COVER

  XHTML scaffolding code for the cover page

.. py:data:: BOOK_CSS

  Content of the ``book.css`` file, adding some page-breaking statements to the overall styling.

"""

#######################################################################################################
meta_inf = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
	<rootfiles>
		<rootfile full-path="package.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
"""


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
        padding: 2em 2em 2em 2em !important;
      }
      h1 {
        text-align: center !important;
        font-size: 250%;
      }
      h2 {
        text-align: center !important;
        font-size: 180%;
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
      h3 {
         page-break-before:always;
         margin-top:4em;
         text-align: left !important;
      }
      ol { text-align: left !important;}
      a { text-decoration: none !important}

    </style>
  </head>
  <body>
    <div id="title">
      <h1 id="btitle"></h1>
      <h2 id="subtitle">W3C Recommendation</h2>
      <p class="larger" id="editors"></p>
      <p class="larger">World Wide Web Consortium (W3C)</p>
      <p class="logo"><a href="http://www.w3.org/"><img alt="W3C main logo" src="Assets/w3c_main.png"/></a></p>
      <p class="disclaimer">Note: this ePub edition does <em>not</em> represent the authoritative text of the specification; please consult the <a id="ref_original">original document</a> on the W3C Web Site.</p>
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
	h2 {
	  page-break-before: always;
	  break-before: always;
	}

	div.head h2 {
	  page-break-before: auto;
	  break-before: auto;
	}

	body {
	  background-image: url(%s);
	}
"""
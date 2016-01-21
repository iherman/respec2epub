document.py: 
- After collect downloads call a separate function to get the css resources. This would include the change information. These are stored in a local list
- The same request would also store a list of change pairs
- The extract references method should also forward the change pairs to the book, which would have to do some chagne on the fly
- The document2book gets the information from the document's pre-fetched array instead of calling the funciton itself.




---

How to do this: does a display none works with a @pages output? Probably not…

The bottomline seems to be: touching the old approach may not be worth the trouble, due to the
* handling of the margins that require changes anyway
* the problem with the ``html5lib`` bug
* the approach of making the TOC invisible anyway...

An alternative is to wait and see whether there will be a possibility to choose between the old version and the new. It may very well be that the new setting would work without further ado (just referring to a different ``base.css``) and with an additional trick of removing the TOC. The real question will be
* Is it possible to see if the document should be processed with the new or the old style sheet, or
* The new style sheet will be the only one that counts

To ask…
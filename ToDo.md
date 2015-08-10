# Functional todo-s

## Current code

### Questions

#### html vs. document

* `DocToEpub.html` : output of html5parse
* `DocToEpub.document` : element tree of html.

Is there a need for `document`?


### The dated URI should be extracted from the document, rather than from the URI

### Remove the usage of ASSETS for resources retrieved from the document; instead, mirror the structure

### (Maybe) change the term ASSETS to something else (W3C_ASSETS?)

## Additional 

These are mainly for the service part:

* Web interface, with minimal API (should the non-respec reflected there? maybe through a different URI, i.e., entry point?)
* How to return, through HTTP, an ebook


# Quality todo-s

* Try to make it more functional, maybe (like editors should be returned from the function rather than added directly like now)
* The Session should not include references to zip and book creation

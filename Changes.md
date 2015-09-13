# Version 1.1

* Added a hack to add a ``type="text/css`` to link elements referring to stylesheets. Not necessary per HTML, but some reading systems require it
* Added an ``("area","href")`` pair to the list of external references that should be checked and act upon.
* Changed the hack of wrapping all content into a ``<div>``: instead of using ``@id`` with a phony value, using ``@role=main`` itself. A check has also been added to avoid doing that if there is already such a wrapper (this is a feature that may be added to ReSpec).


Plus some minor bug and documentation improvements.

# Version 1.0

First "official" release
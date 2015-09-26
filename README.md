ReSpec (and Bikeshed output) to EPUB
====================================

Python script to assist in turning W3C ReSpec documents into EPUB; it can also convert HTML documents that were originally produced by ReSpec or Bikeshed into EPUB. The script does **not** aim at being a generic HTML->EPUB solution, it is indeed tailored at W3C TR documents based on ReSpec and Bikeshed. 

Note that the project includes:

- a command line tool to generate an EPUB 3 version of a spec, whether in ReSpec or generated from ReSpec/Bikeshed
- a wrapper around the tool to provide a web service; the service is installed at [`https://labs.w3.org/epub-generator/`](https://labs.w3.org/epub-generator/)
- extension of ReSpec to call out to that service, 

A [documentation in HTML](https://rawgit.com/iherman/respec2epub/master/Doc/build/html/index.html) is also available, giving more details.

Installation
------------

You can either run 

```
python -install setup.py
```

or

```
pip -e install
```

Both of these should be run in the directory of your local copy of the github repository. In case you do not want to download this, you can also use

```
pip install git+https://github.com/iherman/respec2epub.git
```

Note that the ``pip`` command should also install the ``html5lib`` in case you do not have it installed. If you use direct install, you should install ``html5lib`` manually. See [the ``pypi`` entry for ``html5lib``](https://pypi.python.org/pypi/html5lib).




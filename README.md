# ReSpec (and Bikeshed output) to EPUB

Python script to assist in turning W3C ReSpec documents into EPUB; it can also convert HTML documents that were originally produced by ReSpec or Bikeshed into EPUB. The script does **not** aim at being a generic HTML->EPUB solution, it is indeed tailored at W3C TR documents based on ReSpec and Bikeshed. 

Note that the project includes:

- a command line tool to generate an EPUB 3 version of a spec, whether in ReSpec or generated from ReSpec/Bikeshed
- a wrapper around the tool to provide a web service; the service is installed at [`https://labs.w3.org/epub-generator/`](https://labs.w3.org/epub-generator/)
- extension of ReSpec to call out to that service, 

A [documentation in HTML](https://rawgit.com/iherman/respec2epub/master/Doc/build/html/index.html) is also available, giving more details.

## Installation

### End User

If you just want to use the package, the simplest is to run 

```
pip install git+https://github.com/iherman/respec2epub.git
```

This will install the necessary modules and the command line tool. Its [manual page is online](https://rawgit.com/iherman/respec2epub/master/Doc/build/html/manual.html)

### Developer

If you are a developer, you can clone the repository, install it from there, and off you go with your possible improvements

```
$ git clone  https://github.com/iherman/respec2epub.git
$ cd respec2epub
$ pip -e .  # this will run setup.py automatically
```

You can of course choose the "pedestrian" way to clone the repository and point your ``PYTHONPATH`` variable to the ``rp2epub`` module. In that case you should install ``html5lib`` manually (see [the ``pypi`` entry for ``html5lib``](https://pypi.python.org/pypi/html5lib))

The documentation is in HTML, and can be started up locally in your browser pointing at ``PATHTOREPO/Doc/html/index.html``




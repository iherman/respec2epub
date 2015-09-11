ReSpec (and Bikeshed output) to EPUB
====================================

[![Join the chat at https://gitter.im/iherman/respec2epub](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/iherman/respec2epub?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Python script to assist in turning W3C ReSpec documents into EPUB; it can also convert HTML documents that were originally produced by ReSpec or Bikeshed into EPUB. The script does **not** aim at being a generic HTML->EPUB solution, it is indeed tailored at W3C TR documents based on ReSpec and Bikeshed. 

Note that the project includes:

- a command line tool to generate an EPUB 3 version of a spec, whether in ReSpec or generated from ReSpec/Bikeshed
- a wrapper around the tool to provide a web service; the service is installed at [`https://labs.w3.org/epub-generator/`](https://labs.w3.org/epub-generator/)
- extension of ReSpec to call out to that service, 

A [documentation in HTML](https://rawgit.com/iherman/respec2epub/master/Doc/build/html/index.html) is also available, giving more details.




# To-Dos

* Utils.py contains the `change_DOM` method that implements a hack around a Readium bug. When the newer version of Readium is deployed, that hack should be removed.
* Add a possibility to read a file locally instead of relying solely on a URL; useful for the command line.
* If ReSpec produces the configuration data as part of an embedded JSON, the code should recognize that. 
	* Caveat: the current approach should also remain in the code for older documents... 


# Possible improvements (mainly if there is demand)
* Multi-file documents; essentially, taking over some of the features from [tr2epub](https://github.com/iherman/tr2epub)
* Is it possible to combine it with the bikeshed process?


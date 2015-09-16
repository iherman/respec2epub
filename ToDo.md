# To-Dos

* Utils.py contains the `change_DOM` method that implements a hack around a Readium bug. When the newer version of Readium is deployed, that hack should be removed.
* In the respec specification version, business and community group reports need some more care... The style sheet is not copied locally (it comes from a different W3C directory), neither do the logo. The margins are also different
* If ReSpec comes with its own ``<div role=main>``, this should be checked before the wrapping is done. Also, it has to be checked whether the appendices are part of the wrap and the css part may have to be adjusted, too


# Possible improvements (mainly if there is demand)
* Multi-file documents; essentially, taking over some of the features from [tr2epub](https://github.com/iherman/tr2epub)
* Is it possible to combine it with the bikeshed process?


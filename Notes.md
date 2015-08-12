The folder option in books has to operate with the paths to make the write proper. It seems to work with the ``os.path`` module, though:

```
17:43 tmp> python
Python 2.7.9 (v2.7.9:648dcafa7e5f, Dec 10 2014, 10:10:46) 
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> a = "namivan"
>>> b = "ezvan"
>>> import os.path
>>> os.path.join(a,b)
'namivan/ezvan'
>>> c = 'a/b/c/d/e'
>>> os.path.split(c)
('a/b/c/d', 'e')
>>> 
```
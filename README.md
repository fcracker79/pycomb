[![Build Status](https://travis-ci.org/fcracker79/pycomb.svg?branch=master)](https://travis-ci.org/fcracker79/pycomb)

PyComb
======


[Tcomb](http://www.github.com/tcomb) port for Python 3

Installation
------------

```sh
pip install pycomb
```

**Usage examples**

```python

from pycomb import combinators

MyStringType = c.String
s1 = c.String('hello')  # This IS a 'str' object
s2 = c.String(10)  # This will fail


ListOfStrings = combinators.list(combinators.String)
l1 = ListOfStrings(['1', '2', '3'])  # This IS a native list
l1 = ListOfStrings(['1', '2', 3])  # This will fail



```


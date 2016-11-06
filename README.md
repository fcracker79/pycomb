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

# A simple string
MyStringType = c.String
s1 = combinators.String('hello')  # This IS a 'str' object
s2 = combinators.String(10)  # This will fail

# A list that contains only strings
ListOfStrings = combinators.list(combinators.String)
l1 = ListOfStrings(['1', '2', '3'])  # This IS a native tuple
l1 = ListOfStrings(['1', '2', 3])  # This will fail

# Structured data
User = combinators.struct({'name': combinators.String, 'age': combinators.Int, 'city': combinators.maybe(combinators.String)})
my_user = User({'name': 'John Burns', 'age': 30})  # This IS a dict
my_user2 = User({'name': 'John Burns', 'age': '30'})  # This will fail
my_user3 = User({'name': 'John Burns', 'age': 30, 'city': 'New York'})  # This IS a dict


```


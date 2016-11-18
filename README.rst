PyComb
======

`Tcomb <http://www.github.com/gcanti/tcomb>`__ port for Python 3. It
provides a means to apply runtime type checking.

Installation
------------

.. code:: sh

    pip install pycomb

Basic examples
--------------

.. code:: python


    from pycomb import combinators

    # A simple string
    MyStringType = combinators.String
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

    # Subtypes
    SmallString = c.subtype(c.String, lambda d: len(d) <= 10)  # Strings shorter than 11 characters
    SmallString('12345678901')  # This will fail
    SmallString('12345')  # This IS a 'str' object

Validation context
------------------

The validation procedure runs within a context that controls:

1. The behavior in case of error
2. The production mode: if active, no such error is raised during
   validation

**Context Examples**

.. code:: python


    from pycomb import combinators, context

    # Example of production mode
    ListOfNumbers = combinators.list(combinators.Number, 'ListOfNumbers')
    production_ctx = context.create(production_mode=True)
    numbers = ListOfNumbers([1, 2, 'hello'], ctx=production_ctx)  # This will NOT fail


    # Example of custom behavior in case of error
    class MyObserver(context.ValidationErrorObserver):
        def on_error(self, ctx, expected_type, found_type):
            print('Expected {}, got {}'.format(expected_type, found_type))

    ListOfNumbers = combinators.list(combinators.Number, 'ListOfNumbers')
    notification_ctx = context.create(validation_error_observer=MyObserver())
    numbers = ListOfNumbers([1, 2, 'hello'], ctx=production_ctx)  # This will NOT fail
    # Expected output:
    # > Expected Int or Float, got <class 'str'>

Decorators
----------

It is possible to wrap functions in order to protect the input
parameters, or ensure the type of its return value

**Decorators example**

.. code:: python


    from pycomb import combinators

    # Example of input parameters check
    @combinators.function(
        combinators.String, combinators.Int,
        c=combinators.Float, d=combinators.list(combinators.Int))
    def f(a, b, c=None, d=None):
        pass
    f('John', 1, c=1.0, d=[3, 4])  # OK
    f(1, 1, c=1.0, d=[3, 4])  # This will fail

    # Example of output check
    @returning(cmb.subtype(cmb.String, lambda d: len(d) < 10))
    def f(n):
        return ' ' * n

    f(3)  # OK
    f(10)  # This will fail

More types are supported, such as:

-  Unions
-  Intersections
-  Functions
-  Enums
-  ...

Please read the test code to find more examples.

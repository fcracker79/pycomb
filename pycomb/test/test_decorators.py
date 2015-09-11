from unittest import TestCase
from pycomb import combinators as c
from pycomb.decorators import returning


class TestDecorators(TestCase):
    def test(self):
        @c.function(c.String, c.Int, c=c.Float, d=c.list(c.Int))
        def f(a, b, c=None, d=None):
            pass

        f('John', 1, c=1.0, d=[3, 4])

        with(self.assertRaises(ValueError)):
            f(1, 1, c=1.0, d=[3, 4])

        with(self.assertRaises(ValueError)):
            f('John', 1, c=1.0, d=['3', 4])

    def test_returning(self):
        @returning(c.subtype(c.String, lambda d: len(d) < 10))
        def f(n):
            return ' ' * n

        self.assertEqual('   ', f(3))

        with(self.assertRaises(ValueError)):
            f(10)

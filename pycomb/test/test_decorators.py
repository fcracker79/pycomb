from unittest import TestCase
from pycomb import combinators as cmb, exceptions
from pycomb.decorators import returning


class TestDecorators(TestCase):
    def test(self):
        # noinspection PyUnusedLocal
        @cmb.function(cmb.String, cmb.Int, c=cmb.Float, d=cmb.list(cmb.Int))
        def f(a, b, c=None, d=None):
            pass

        f('John', 1, c=1.0, d=[3, 4])

        with(self.assertRaises(exceptions.PyCombValidationError)):
            f(1, 1, c=1.0, d=[3, 4])

        with(self.assertRaises(exceptions.PyCombValidationError)):
            f('John', 1, c=1.0, d=['3', 4])

    def test_returning(self):
        @returning(cmb.subtype(cmb.String, lambda d: len(d) < 10))
        def f(n):
            return ' ' * n

        self.assertEqual('   ', f(3))

        with(self.assertRaises(exceptions.PyCombValidationError)):
            f(10)

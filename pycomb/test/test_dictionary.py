import unittest

from pycomb import combinators, context
from pycomb.combinators import dictionary
from pycomb.test import util


class TestDictionary(unittest.TestCase):
    def test_ok(self):
        d = {
            1: 'hello',
            2: 'Hello',
            3: 4
        }

        sut = dictionary(combinators.Int, combinators.union(combinators.String, combinators.Int))
        sut(d)

    def test_values(self):
        d = {
            1: 'hello',
            2: 'Hello',
            3: 4
        }
        sut = dictionary(combinators.Int, combinators.String)
        with util.throws_with_message('Error on dictionary(Int: String)[3]: expected String but was int'):
            sut(d)

    def test_keys(self):
        d = {
            'hello': 1,
            1: 2,
            4: 3
        }
        sut = dictionary(combinators.Int, combinators.Int)
        with util.throws_with_message('Error on dictionary(Int: Int).hello: expected Int but was str'):
            sut(d)

    def test_values_with_name(self):
        d = {
            1: 'hello',
            2: 'Hello',
            3: 4
        }
        sut = dictionary(combinators.Int, combinators.String, name='IntStringDict')
        with util.throws_with_message('Error on IntStringDict[3]: expected String but was int'):
            sut(d)

    def test_keys_with_name(self):
        d = {
            'hello': 1,
            1: 2,
            4: 3
        }
        sut = dictionary(combinators.Int, combinators.Int, name='IntIntDict')
        with util.throws_with_message('Error on IntIntDict.hello: expected Int but was str'):
            sut(d)

    def test_no_dict(self):
        d = object()

        sut = dictionary(combinators.Int, combinators.Int)
        with util.throws_with_message('Error on dictionary(Int: Int): expected dictionary(Int: Int) but was object'):
            sut(d)

        sut = dictionary(combinators.Int, combinators.Int, name='ADict')
        with util.throws_with_message('Error on ADict: expected ADict but was object'):
            sut(d)

    def test_production_mode(self):
        ctx = context.create(production_mode=True)
        d = {
            1: 'hello',
            2: 'Hello',
            3: 4
        }
        sut = dictionary(combinators.Int, combinators.String)
        self.assertIs(d, sut(d, ctx=ctx))

        d = {
            'hello': 1,
            1: 2,
            4: 3
        }
        sut = dictionary(combinators.Int, combinators.Int)
        self.assertIs(d, sut(d, ctx=ctx))

        d = object()

        sut = dictionary(combinators.Int, combinators.Int)
        self.assertIs(d, sut(d, ctx=ctx))


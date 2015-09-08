from unittest import TestCase
from pycomb import combinators as c
from pycomb.predicates import StructType


class TestCombinators(TestCase):
    def test(self):

        with(self.assertRaises(ValueError)):
            c.String(1)

        s = c.String('hello')

        self.assertEqual(str, type(s))

    def test_list_2(self):
        List = c.list(c.Int)

        l = List([1, 2, 3])
        l2 = List(l)

        self.assertTrue(l is l2)

    def test_list(self):
        with(self.assertRaises(ValueError)):
            c.list(c.String)('hello')

        with(self.assertRaises(ValueError)):
            c.list(c.String)([1, 2, 3])

        l = c.list(c.String)(['a', 'b'])
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])

    def test_tuple(self):
        with(self.assertRaises(ValueError)):
            c.list(c.String)('hello')

        with(self.assertRaises(ValueError)):
            c.list(c.String)((1, 2, 3))

        l = c.list(c.String)(('a', 'b'))
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])

    def test_struct(self):
        d = {'name': c.String, 'value': c.Int}
        with(self.assertRaises(ValueError)):
            c.struct(d)('hello')

        with(self.assertRaises(ValueError)):
            c.struct(d)({'name': 0, 'value': 1})

        result = c.struct(d)({'name': 'myName', 'value': 1})
        self.assertEqual('myName', result.name)

        with(self.assertRaises(TypeError)):
            result.name = 'anotherName'

    def test_struct_list(self):
        r = c.list(c.struct({'name': c.String}))([{'name': 'John'}])
        self.assertEqual(1, len(r))

        self.assertEqual(StructType, type(r[0]))

    def test_struct_maybe(self):
        r = c.maybe(c.struct({'name': c.String}))({'name': 'John'})

        self.assertEqual(StructType, type(r))

    def test_maybe(self):
        with(self.assertRaises(ValueError)):
            c.String(None)

        self.assertIsNone(c.maybe(c.String)(None))

        self.assertEqual('hello', c.maybe(c.String)('hello'))

    def test_subtype(self):
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10)

        with(self.assertRaises(ValueError)):
            SmallString('12345678901')

        self.assertEqual('12345', SmallString('12345'))

    def test_union(self):
        Number = c.union(c.Int, c.Float)

        self.assertEqual(1.0, Number(1.0))
        self.assertEqual(2, Number(2))

        with(self.assertRaises(ValueError)):
            Number('hello')

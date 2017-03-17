import unittest
from pycomb import combinators as c


class TestExamples(unittest.TestCase):
    def test_irreducible(self):
        self.assertEqual(-11235, c.Int.example)
        self.assertEqual('Lorem 1p$um', c.String.example)
        self.assertEqual(-0.12345, c.Float.example)
        self.assertEqual(-11235, c.Number.example)

    def test_list(self):
        l = c.list(c.Int)
        self.assertEqual([-11235, -11235, -11235], l.example)

    def test_struct(self):
        s = c.struct({'a': c.Int, 'b': c.String})
        self.assertEqual({'a': -11235, 'b': 'Lorem 1p$um'}, s.example)

    def test_union(self):
        u = c.union(c.String, c.Int)
        self.assertEqual(u.example, 'Lorem 1p$um')
        u = c.union(c.constant(None), c.Int)
        self.assertEqual(u.example, -11235)
        u = c.union(c.constant(None), c.constant(None))
        self.assertIsNone(u.example)

    def test_subtype(self):
        s = c.subtype(c.String, lambda: True, example='Hello World')
        self.assertEqual('Hello World', s.example)

    def test_intersection(self):
        i = c.intersection(c.Float, c.Int, example=12)
        self.assertEqual(12, i.example)

    def test_generic_object(self):
        class MyObject:
            def __init__(self):
                self.a = None
                self.b = None

        o = c.generic_object({'a': c.Int, 'b': c.String}, MyObject)
        self.assertTrue(isinstance(o.example, MyObject))
        self.assertEqual(-11235, o.example.a)
        self.assertEqual('Lorem 1p$um', o.example.b)

        expected_example = MyObject()
        expected_example.a = 12
        expected_example.b = 'Hello'
        o = c.generic_object({'a': c.Int, 'b': c.String}, MyObject, example=expected_example)
        self.assertEqual(expected_example, o.example)
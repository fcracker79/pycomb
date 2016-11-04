from unittest import TestCase
from unittest.mock import Mock
from pycomb import combinators as c
from pycomb.combinators import generic_object, Int
from pycomb.predicates import StructType
from pycomb.test import util

class TestCombinators(TestCase):
    def test(self):

        with(self.assertRaises(ValueError)):
            c.String(1)

        s = c.String('hello')

        self.assertEqual(str, type(s))

    def test_list(self):
        c.list(c.String)('hello')

        with(self.assertRaises(ValueError)):
            c.list(c.String)([1, 2, 3])

        e = None

        try:
            c.list(c.String)(['1', 2, '3'])
        except Exception as ex:
            e = ex

        self.assertIsInstance(e, ValueError)

        expected = 'Error on List(String)[1]: expected String but was int'
        self.assertEquals(expected, e.args[0])

        l = c.list(c.String)(['a', 'b'])
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])

    def test_tuple(self):
        c.list(c.String)('hello')

        with(self.assertRaises(ValueError)):
            c.list(c.String)((1, 2, 3))

        l = c.list(c.String)(['a', 'b'])
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])

    def test_struct(self):
        d = {'name': c.String, 'value': c.Int}
        with(self.assertRaises(ValueError)):
            c.struct(d)('hello')

        e = None
        try:
            c.struct(d)({'name': 0, 'value': 1})
        except ValueError as ex:
            e = ex

        self.assertTrue(
            e.args[0] in
            ('Error on Struct{name: String, value: Int}[name]: expected String but was int',
             'Error on Struct{value: Int, name: String}[name]: expected String but was int'),
            msg=e.args[0])

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

    def test_struct_of_struct(self):
        r = c.struct({'name': c.String, 'data': c.struct({'age': c.Int})})({'name': 'Mirko', 'data': {'age': 36}})

        self.assertEqual('Mirko', r.name)
        self.assertEqual(36, r.data.age)

        util
        exception = None
        try:
            c.struct({'name': c.String, 'data': c.struct({'age': c.Int})})({'name': 'Mirko', 'data': {'age': '36'}})
        except ValueError as e:
            exception = e

        self.assertTrue(
            exception.args[0] in (
                'Error on Struct{data: Struct{age: Int}, name: String}[data][age]: expected Int but was str',
                'Error on Struct{name: String, data: Struct{age: Int}}[data][age]: expected Int but was str',
            ),
            msg=exception.args[0])

    def test_maybe(self):
        with(self.assertRaises(ValueError)):
            c.String(None)

        self.assertIsNone(c.maybe(c.String)(None))

        self.assertEqual('hello', c.maybe(c.String)('hello'))

    def test_subtype(self):
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10)

        e = None
        try:
            SmallString('12345678901')
        except ValueError as ex:
            e = ex

        self.assertEqual('Error on Subtype(String): expected Subtype(String) but was str', e.args[0])

        self.assertEqual('12345', SmallString('12345'))

    def test_union(self):
        Number = c.union(c.Int, c.Float)

        self.assertEqual(1.0, Number(1.0))
        self.assertEqual(2, Number(2))

        e = None
        try:
            Number('hello')
        except ValueError as ex:
            e = ex

        self.assertEqual('Error on Union(Int, Float): expected Int or Float but was str', e.args[0])

    def test_intersection(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type)

        d = my_type({'name': 'mirko', 'age': 36})
        self.assertEqual('mirko', d.name)

        e = None
        try:
            my_type({'name': 'mirko', 'age': '36'})
        except ValueError as ex:
            e = ex

        self.assertEqual(
            'Error on Intersection(Struct{name: String}, Struct{age: Int}): '
            'expected Struct{name: String} or Struct{age: Int} but was dict',
            e.args[0])

    def test_enums(self):
        Enum = c.enum({'V1': '1', 'V2': '2', 'V3': '3'})

        self.assertEqual('1', Enum.V1)
        self.assertEqual('2', Enum.V2)
        self.assertEqual('3', Enum.V3)

        e = Enum('V1')
        self.assertEqual('1', e)

        e = None
        try:
            Enum('V4')
        except ValueError as ex:
            e = ex

        self.assertEqual('Error on Enum(V1: 1, V2: 2, V3: 3): expected V1 or V2 or V3 but was V4', e.args[0])

    def test_enums_list(self):
        # noinspection PyUnresolvedReferences
        Enum = c.enum.of(['a', 'b', 'c'])

        self.assertEqual('a', Enum('a'))
        self.assertEqual('b', Enum('b'))
        self.assertEqual('c', Enum('c'))

        self.assertEqual('a', Enum.a)
        self.assertEqual('b', Enum.b)
        self.assertEqual('c', Enum.c)

        e = None
        try:
            Enum('V4')
        except ValueError as ex:
            e = ex

        self.assertEqual('Error on Enum(a: a, b: b, c: c): expected a or b or c but was V4', e.args[0])

    def test_function(self):
        # noinspection PyUnresolvedReferences
        Fun = c.function(c.String, c.Int, a=c.Float, b=c.enum.of(['X', 'Y', 'Z']))

        f = Mock()

        new_f = Fun(f)
        self.assertTrue(callable(new_f))

        e = None
        try:
            new_f()
        except ValueError as ex:
            e = ex

        self.assertTrue(
            e.args[0] in (
                'Error on Function(String, Int, a=Float, b=Enum(X: X, Y: Y, Z: Z)): '
                'expected 2 arguments but was 0 arguments',
                'Error on Function(String, Int, b=Enum(X: X, Y: Y, Z: Z), a=Float): '
                'expected 2 arguments but was 0 arguments'
            )
        )

        e = None
        try:
            Fun('Hello')
        except ValueError as ex:
            e = ex

        self.assertTrue(e.args[0] in (
            'Error on Function(String, Int, b=Enum(X: X, Y: Y, Z: Z), a=Float): '
            'expected Function(String, Int, b=Enum(X: X, Y: Y, Z: Z), a=Float) but was str',
            'Error on Function(String, Int, a=Float, b=Enum(X: X, Y: Y, Z: Z)): '
            'expected Function(String, Int, a=Float, b=Enum(X: X, Y: Y, Z: Z)) but was str'
        ))

        # noinspection PyUnusedLocal
        def f(x1, x2, a=None, b=None):
            pass

        g = Fun(f)

        self.assertIsNot(f, g)

        g2 = Fun(g)

        self.assertIs(g, g2)

    def test_object(self):
        class TestClass(object):
            def __init__(self, f1, f2):
                self.f1 = f1
                self.f2 = f2

        t = TestClass('hello', 10)

        type1 = generic_object({'f1': Int, 'f2': Int}, TestClass)

        e = None
        try:
            type1(t)
        except ValueError as ex:
            e = ex

        self.assertEqual(
            'Error on TestClass.f1: expected Int but was str',
            e.args[0])

        t = TestClass(20, 3.5)

        e = None
        try:
            type1(t)
        except ValueError as ex:
            e = ex

        self.assertEqual(
            'Error on TestClass.f2: expected Int but was float',
            e.args[0])

        t = TestClass(20, 3)

        type1(t)

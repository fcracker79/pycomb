from unittest import TestCase
try:
    from unittest import mock
    from unittest.mock import Mock
except ImportError:
    import mock
    from mock import Mock

from pycomb import combinators as c, exceptions, context
from pycomb.combinators import generic_object, Int
from pycomb.predicates import StructType


class _AnyContext(context.ValidationContext):
    @property
    def empty(self):
        raise ValueError

    def append(self, path_element):
        raise ValueError

    def path(self):
        raise ValueError

    @property
    def production_mode(self):
        raise ValueError

    def notify_error(self, expected_type, found_type):
        raise ValueError

    def add_error_observer(self, error_observer):
        raise ValueError

    def __eq__(self, other):
        return isinstance(other, context.ValidationContext)


_ANY_CONTEXT = _AnyContext()


class TestCombinators(TestCase):
    def test(self):

        with(self.assertRaises(exceptions.PyCombValidationError)):
            c.String(1)

        s = c.String('hello')

        self.assertEqual(str, type(s))

    def test_list(self):
        c.list(c.String)('hello')
        with(self.assertRaises(exceptions.PyCombValidationError)):
            c.list(c.String)([1, 2, 3])
        self.assertFalse(c.list(c.String).is_type([1, 2, 3]))

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            c.list(c.String)(['1', 2, '3'])
        e = e.exception
        expected = 'Error on List(String)[1]: expected String but was int'
        self.assertEqual(expected, e.args[0])
        l = c.list(c.String)(['a', 'b'])
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])
        self.assertTrue(c.list(c.String).is_type(['a', 'b']))

    def test_list_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        c.list(c.String)('hello', ctx=ctx)
        self.assertEqual(0, observer.on_error.call_count)
        c.list(c.String)([1, 2, 3], ctx=ctx)
        observer.on_error.assert_has_calls(
            [
                mock.call(_ANY_CONTEXT, 'String', int),
                mock.call(_ANY_CONTEXT, 'String', int),
                mock.call(_ANY_CONTEXT, 'String', int)
            ])
        self.assertFalse(c.list(c.String).is_type([1, 2, 3]))
        observer.reset_mock()
        c.list(c.String)(['1', 2, '3'], ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'String', int)
        observer.reset_mock()
        self.assertIsNone(
            c.list(c.String)(None, ctx=ctx)
        )
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'List', type(None))

    def test_list_production(self):
        self.assertEqual(
            [1, 2, 3],
            c.list(c.String)([1, 2, 3], ctx=context.create(production_mode=True))
        )
        self.assertIsNone(
            c.list(c.String)(None, ctx=context.create(production_mode=True))
        )

    def test_tuple(self):
        c.list(c.String)('hello')

        with(self.assertRaises(exceptions.PyCombValidationError)):
            c.list(c.String)((1, 2, 3))

        l = c.list(c.String)(['a', 'b'])
        self.assertEqual(tuple, type(l))
        self.assertEqual(2, len(l))
        self.assertEqual('a', l[0])
        self.assertEqual('b', l[1])

    def test_tuple_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        c.list(c.String)('hello')

        c.list(c.String)((1, 2, 3), ctx=ctx)
        observer.on_error.assert_has_calls(
            [
                mock.call(_ANY_CONTEXT, 'String', int),
                mock.call(_ANY_CONTEXT, 'String', int),
                mock.call(_ANY_CONTEXT, 'String', int)
            ]
        )

    def test_struct(self):
        d = {'name': c.String, 'value': c.Int}
        with(self.assertRaises(exceptions.PyCombValidationError)):
            c.struct(d)('hello')

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            c.struct(d)({'name': 0, 'value': 1})

        e = e.exception
        self.assertTrue(
            e.args[0] in
            ('Error on Struct{name: String, value: Int}[name]: expected String but was int',
             'Error on Struct{value: Int, name: String}[name]: expected String but was int'),
            msg=e.args[0])

        result = c.struct(d)({'name': 'myName', 'value': 1})
        self.assertEqual('myName', result.name)

        with(self.assertRaises(TypeError)):
            result.name = 'anotherName'

    def test_struct_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        d = {'name': c.String, 'value': c.Int}
        c.struct(d)('hello', ctx=ctx)
        call = observer.on_error.call_args_list
        self.assertEqual(1, len(call))
        call = call[0]
        self.assertTrue(
            call == mock.call(_ANY_CONTEXT, 'Struct{value: Int, name: String}', str) or \
            call == mock.call(_ANY_CONTEXT, 'Struct{name: String, value: Int}', str),
            msg=str(call)
        )

    def test_struct_maybe_field(self):
        User = c.struct({'name': c.String, 'age': c.Int, 'city': c.maybe(c.String)})
        User({'name': 'John Burns', 'age': 30})

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

        with self.assertRaises(exceptions.PyCombValidationError) as exception:
            c.struct({'name': c.String, 'data': c.struct({'age': c.Int})})({'name': 'Mirko', 'data': {'age': '36'}})
        exception = exception.exception
        self.assertTrue(
            exception.args[0] in (
                'Error on Struct{data: Struct{age: Int}, name: String}[data][age]: expected Int but was str',
                'Error on Struct{name: String, data: Struct{age: Int}}[data][age]: expected Int but was str',
            ),
            msg=exception.args[0])

    def test_maybe(self):
        with(self.assertRaises(exceptions.PyCombValidationError)):
            c.String(None)
        self.assertIsNone(c.maybe(c.String)(None))
        my_maybe = c.maybe(c.String)
        self.assertEqual('hello', my_maybe('hello'))
        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_maybe(1)
        self.assertEqual(
            'Error on Maybe (String): expected None or String but was int',
            e.exception.args[0])

    def test_named_maybe(self):
        my_maybe = c.maybe(c.String, name='MyMaybe')
        self.assertIsNone(my_maybe(None))
        self.assertEqual('hello', my_maybe('hello'))
        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_maybe(1)
        self.assertEqual(
            'Error on MyMaybe: expected None or String but was int',
            e.exception.args[0])

    def test_subtype(self):
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            SmallString('12345678901')
        e = e.exception
        self.assertEqual('Error on Subtype(String): expected Subtype(String) but was str', e.args[0])
        self.assertEqual('12345', SmallString('12345'))

    def test_subtype_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10)
        SmallString('12345678901', ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'Subtype(String)', str)

    def test_named_subtype(self):
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10, name='SmallString')

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            SmallString('12345678901')
        e = e.exception
        self.assertEqual('Error on SmallString: expected SmallString but was str', e.args[0])
        self.assertEqual('12345', SmallString('12345'))

    def test_union(self):
        Number = c.union(c.Int, c.Float)

        self.assertEqual(1.0, Number(1.0))
        self.assertEqual(2, Number(2))

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Number('hello')
        e = e.exception
        self.assertEqual('Error on Union(Int, Float): expected Int or Float but was str', e.args[0])

    def test_union_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        Number = c.union(c.Int, c.Float)
        Number('hello', ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'Int or Float', str)

    def test_union_dispatcher(self):
        Number = c.union(c.Int, c.Float, dispatcher=lambda _: c.Float)

        self.assertEqual(1.0, Number(1.0))
        with self.assertRaises(exceptions.PyCombValidationError) as e:
            self.assertEqual(2, Number(2))
        self.assertEqual(
            'Error on Union(Int, Float): expected Float but was int',
            e.exception.args[0])

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Number('hello')
        e = e.exception
        self.assertEqual('Error on Union(Int, Float): expected Int or Float but was str', e.args[0])

    def test_intersection(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type)

        d = my_type({'name': 'mirko', 'age': 36})
        self.assertEqual('mirko', d.name)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_type({'name': 'mirko', 'age': '36'})
        e = e.exception
        self.assertEqual(
            'Error on Intersection(Struct{name: String}, Struct{age: Int}): '
            'expected Struct{name: String} or Struct{age: Int} but was dict',
            e.args[0])

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_type('Hello')
        e = e.exception
        self.assertEqual(
            'Error on Intersection(Struct{name: String}, Struct{age: Int}): '
            'expected Struct{name: String} or Struct{age: Int} but was str',
            e.args[0])

    def test_intersection_custom_error(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type)
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        my_type({'name': 'mirko', 'age': '36'}, ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'Struct{name: String} or Struct{age: Int}', dict)

    def test_intersection_dispatcher(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type, dispatcher=lambda x: age_type)

        d = my_type({'name': 'mirko', 'age': 36})
        self.assertEqual(36, d.age)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_type({'name': 'mirko', 'age': '36'})
        e = e.exception
        self.assertEqual(
            'Error on Intersection(Struct{name: String}, Struct{age: Int}): '
            'expected Struct{name: String} or Struct{age: Int} but was dict',
            e.args[0])

    def test_named_intersection(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type, name='MyType')

        d = my_type({'name': 'mirko', 'age': 36})
        self.assertEqual('mirko', d.name)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_type({'name': 'mirko', 'age': '36'})
        e = e.exception
        self.assertEqual(
            'Error on MyType: '
            'expected Struct{name: String} or Struct{age: Int} but was dict',
            e.args[0])

    def test_enums(self):
        Enum = c.enum({'V1': '1', 'V2': '2', 'V3': '3'})

        self.assertEqual('1', Enum.V1)
        self.assertEqual('2', Enum.V2)
        self.assertEqual('3', Enum.V3)

        e = Enum('V1')
        self.assertEqual('1', e)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Enum('V4')
        e = e.exception
        self.assertEqual('Error on Enum(V1: 1, V2: 2, V3: 3): expected V1 or V2 or V3 but was V4', e.args[0])

    def test_enums_custom_error(self):
        Enum = c.enum({'V1': '1', 'V2': '2', 'V3': '3'})

        observer = Mock()
        ctx = context.create(validation_error_observer=observer)
        Enum('V4', ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'V1 or V2 or V3', 'V4')

    def test_named_enums(self):
        Enum = c.enum({'V1': '1', 'V2': '2', 'V3': '3'}, name='MyEnum')

        self.assertEqual('1', Enum.V1)
        self.assertEqual('2', Enum.V2)
        self.assertEqual('3', Enum.V3)

        e = Enum('V1')
        self.assertEqual('1', e)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Enum('V4')
        e = e.exception
        self.assertEqual('Error on MyEnum: expected V1 or V2 or V3 but was V4', e.args[0])

    def test_enums_list(self):
        # noinspection PyUnresolvedReferences
        Enum = c.enum.of(['a', 'b', 'c'])

        self.assertEqual('a', Enum('a'))
        self.assertEqual('b', Enum('b'))
        self.assertEqual('c', Enum('c'))

        self.assertEqual('a', Enum.a)
        self.assertEqual('b', Enum.b)
        self.assertEqual('c', Enum.c)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Enum('V4')
        e = e.exception
        self.assertEqual('Error on Enum(a: a, b: b, c: c): expected a or b or c but was V4', e.args[0])

    def test_function(self):
        # noinspection PyUnresolvedReferences
        Fun = c.function(c.String, c.Int, a=c.Float, b=c.enum.of(['X', 'Y', 'Z']))

        f = Mock()

        new_f = Fun(f)
        self.assertTrue(callable(new_f))

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            new_f()
        e = e.exception
        self.assertTrue(
            e.args[0] in (
                'Error on Function(String, Int, a=Float, b=Enum(X: X, Y: Y, Z: Z)): '
                'expected 2 arguments but was 0 arguments',
                'Error on Function(String, Int, b=Enum(X: X, Y: Y, Z: Z), a=Float): '
                'expected 2 arguments but was 0 arguments'
            )
        )

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            Fun('Hello')
        e = e.exception
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

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            type1(t)
        e = e.exception
        self.assertEqual(
            'Error on TestClass.f1: expected Int but was str',
            e.args[0])
        self.assertFalse(type1.is_type(t))
        t = TestClass(20, 3.5)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            type1(t)
        e = e.exception
        self.assertEqual(
            'Error on TestClass.f2: expected Int but was float',
            e.args[0])
        self.assertFalse(type1.is_type(t))
        with self.assertRaises(exceptions.PyCombValidationError) as e:
            type1('hello')
        e = e.exception
        self.assertEqual(
            'Error on TestClass: expected TestClass but was str',
            e.args[0])
        self.assertFalse(type1.is_type(t))
        t = TestClass(20, 3)

        type1(t)
        self.assertTrue(type1.is_type(t))

    def test_object_custom_error(self):
        observer = Mock()
        ctx = context.create(validation_error_observer=observer)

        class TestClass(object):
            def __init__(self, f1, f2):
                self.f1 = f1
                self.f2 = f2

        t = TestClass('hello', 10)

        type1 = generic_object({'f1': Int, 'f2': Int}, TestClass)
        type1(t, ctx=ctx)
        observer.on_error.assert_called_once_with(_ANY_CONTEXT, 'Int', str)

    def test_object_with_custom_name(self):
        class TestClass(object):
            def __init__(self, f1, f2):
                self.f1 = f1
                self.f2 = f2

        t = TestClass('hello', 10)

        type1 = generic_object({'f1': Int, 'f2': Int}, TestClass, name='MyTestClass')

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            type1(t)
        e = e.exception
        self.assertEqual(
            'Error on MyTestClass.f1: expected Int but was str',
            e.args[0])

    def test_int_production(self):
        my_int = c.Int('hello', ctx=context.create(production_mode=True))
        self.assertEqual('hello', my_int)

    def test_struct_production(self):
        my_struct = c.struct({
            'a': c.Int, 'b': c.String
        })
        base_dict = {'a': 'hello', 'b': 'world'}
        s = my_struct(base_dict, ctx=context.create(production_mode=True))
        self.assertEqual(base_dict, s)

    def test_union_production(self):
        Number = c.union(c.Int, c.Float)
        self.assertEqual('hello', Number('hello', ctx=context.create(production_mode=True)))

    def test_intersection_production(self):
        name_type = c.struct({'name': c.String})
        age_type = c.struct({'age': c.Int})
        my_type = c.intersection(name_type, age_type)

        base_dict = {'name': 'mirko', 'age': '36'}
        self.assertEqual(base_dict, my_type(base_dict, ctx=context.create(production_mode=True)))

    def test_subtype_production(self):
        SmallString = c.subtype(c.String, lambda d: len(d) <= 10)
        self.assertEqual('12345678901', SmallString('12345678901', ctx=context.create(production_mode=True)))

    def test_enums_production(self):
        Enum = c.enum({'V1': '1', 'V2': '2', 'V3': '3'})
        self.assertEqual('V4', Enum('V4', ctx=context.create(production_mode=True)))

    def test_function_production(self):
        # noinspection PyUnresolvedReferences
        Fun = c.function(c.String, c.Int, a=c.Float, b=c.enum.of(['X', 'Y', 'Z']))
        new_f = Fun(lambda: None, ctx=context.create(production_mode=True))
        new_f()

    def test_object_production(self):
        class TestClass(object):
            def __init__(self, f1, f2):
                self.f1 = f1
                self.f2 = f2
        t = TestClass('hello', 10)
        type1 = generic_object({'f1': Int, 'f2': Int}, TestClass)
        self.assertEqual(t, type1(t, ctx=context.create(production_mode=True)))

    def test_maybe_production(self):
        my_maybe = c.maybe(c.String)
        self.assertEqual(1, my_maybe(1, ctx=context.create(production_mode=True)))

    def test_struct_of_list(self):
        my_struct = c.struct(
            {
                'l': c.list(c.String)
            }
        )

        my_struct({'l': ['1', '2', '3']})
        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_struct({'l': ['1', '2', 3]})
        self.assertEqual(
            'Error on Struct{l: List(String)}[l][2]: expected String but was int',
            e.exception.args[0])

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            my_struct({'w': ['1', '2', '3']})
        self.assertEqual(
            'Error on Struct{l: List(String)}[l]: expected List but was NoneType',
            e.exception.args[0])

    def test_regexp(self):
        self._test_regexp('John 32', True, True, '')

    def test_regexp_error_name(self):
        self._test_regexp(
            'John 32', False, True,
            'Error on RegexpGroup((\w+) +([0-9]+))[0]: expected Name but was str')

    def test_regexp_error_age(self):
        self._test_regexp(
            'John 32', True, False,
            'Error on RegexpGroup((\w+) +([0-9]+))[1]: expected Age but was str')

    def test_regexp_error(self):
        self._test_regexp(
            'John32', True, True,
            'Error on RegexpGroup((\w+) +([0-9]+)): expected RegexpGroup((\w+) +([0-9]+)) but was str',
            suberror=False)

    def _test_regexp(self, value, valid_name: bool, valid_age: bool, exp_msg: str, suberror: bool=True):
        name_condition = mock.Mock()
        name_condition.return_value = valid_name
        age_condition = mock.Mock()
        age_condition.return_value = valid_age
        name = c.subtype(c.String, name_condition, name='Name')
        age = c.subtype(c.String, age_condition, name='Age')
        name_age = c.regexp_group('(\w+) +([0-9]+)', name, age)
        if not exp_msg:
            name_age(value)
        else:
            with self.assertRaises(exceptions.PyCombValidationError) as e:
                name_age(value)
            self.assertEqual(
                exp_msg, e.exception.args[0],
                msg='Got {}'.format(e.exception.args[0]))

        if suberror:
            name_condition.assert_called_once_with(value.split(' ')[0])
            valid_name and age_condition.assert_called_once_with(value.split(' ')[1])

    def test_regexp_named_comb(self):
        self._test_regexp_named_comb('John 32', True, True, '')

    def test_regexp_error_name_named_comb(self):
        self._test_regexp_named_comb(
            'John 32', False, True,
            'Error on NameAgeType[0]: expected Name but was str')

    def test_regexp_error_age_named_comb(self):
        self._test_regexp_named_comb(
            'John 32', True, False,
            'Error on NameAgeType[1]: expected Age but was str')

    def test_regexp_error_named_comb(self):
        self._test_regexp_named_comb(
            'John32', True, True,
            'Error on NameAgeType: expected NameAgeType but was str',
            suberror=False)

    def _test_regexp_named_comb(self, value, valid_name: bool, valid_age: bool, exp_msg: str, suberror: bool = True):
        name_condition = mock.Mock()
        name_condition.return_value = valid_name
        age_condition = mock.Mock()
        age_condition.return_value = valid_age
        name = c.subtype(c.String, name_condition, name='Name')
        age = c.subtype(c.String, age_condition, name='Age')
        name_age = c.regexp_group('(\w+) +([0-9]+)', name, age, name='NameAgeType')
        if not exp_msg:
            name_age(value)
        else:
            with self.assertRaises(exceptions.PyCombValidationError) as e:
                name_age(value)
            self.assertEqual(
                exp_msg, e.exception.args[0],
                msg='Got {}'.format(e.exception.args[0]))

        if suberror:
            name_condition.assert_called_once_with(value.split(' ')[0])
            valid_name and age_condition.assert_called_once_with(value.split(' ')[1])

    def test_constant(self):
        John = c.constant(
            {
                'name': 'John', 'surname': 'Burns'
            },
            name='JohnConstant')
        John({
            'name': 'John', 'surname': 'Burns'
        })

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            John(
                {
                    'name': 'Jack', 'surname': 'Burns'
                }
            )
        self.assertEqual(
            'Error on JohnConstant: expected JohnConstant but was dict',
            e.exception.args[0])

        John = c.constant(
            {
                'name': 'John'
            })
        John({
            'name': 'John'
        })

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            John(
                {
                    'name': 'Jack'
                }
            )
        self.assertEqual(
            'Error on Constant({\'name\': \'John\'}): expected Constant({\'name\': \'John\'}) but was dict',
            e.exception.args[0])

    def test_bool(self):
        c.Boolean(True)
        c.Boolean(False)

        with self.assertRaises(exceptions.PyCombValidationError) as e:
            c.Boolean(32)
        self.assertEqual('Error on Boolean: expected Boolean but was int', e.exception.args[0])

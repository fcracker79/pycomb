import re
from functools import wraps

from pycomb import examples
from pycomb import predicates as p, context

_orig_list = list


def get_type_name(type_obj):
    return type_obj.meta['name']


def assert_type(guard, ctx, expected=None, found_type=None):
    if not guard and not ctx.production_mode:
        ctx.notify_error(expected, found_type)


def irreducible(predicate, example, name='Irreducible'):
    def _irreducible(value, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return value

        if new_ctx.empty:
            new_ctx.append(name)

        assert_type(_irreducible.is_type(value), ctx=new_ctx, expected=name, found_type=type(value))

        return value

    _irreducible.is_type = predicate

    _irreducible.meta = {
        'name': name
    }

    _irreducible.example = example

    return _irreducible


Int = irreducible(p.is_int, examples.Int, name='Int')
Float = irreducible(p.is_float, examples.Float, name='Float')
String = irreducible(p.is_string, examples.String, name='String')
Boolean = irreducible(p.is_bool, True, name='Boolean')


def constant(value, name=None):
    return irreducible(lambda d: d == value, value, name=name or 'Constant({})'.format(value))


# noinspection PyShadowingBuiltins
def list(combinator_element, name=None):
    if not name:
        name = 'List({})'.format(get_type_name(combinator_element))

    def _list(x, ctx=None):
        new_ctx_list = context.create(ctx)
        if new_ctx_list.production_mode:
            return x

        if new_ctx_list.empty:
            new_ctx_list.append(name)

        assert_type(x is not None, ctx=new_ctx_list, expected=name, found_type=type(None))
        if not x:
            return None
        
        result = []
        i = 0

        for d in x:
            new_ctx = context.create(new_ctx_list)
            new_ctx.append('[{}]'.format(i), separator='')

            result.append(combinator_element(d, ctx=new_ctx))
            i += 1

        return tuple(result)

    def _is_type(d):
        if not type(d) in (_orig_list, tuple):
            return False

        for x in d:
            if not combinator_element.is_type(x):
                return False

        return True

    _list.is_type = _is_type
    _list.meta = {
        'name': name
    }
    _list.example = [combinator_element.example for _ in range(examples.ListSize)]
    return _list


# noinspection PyShadowingBuiltins
def sequence(combinator_element, name=None):
    if not name:
        name = 'Sequence({})'.format(get_type_name(combinator_element))

    def _sequence(x, ctx=None):
        new_ctx_sequence = context.create(ctx)
        if new_ctx_sequence.production_mode:
            return x

        if new_ctx_sequence.empty:
            new_ctx_sequence.append(name)

        assert_type(x is not None, ctx=new_ctx_sequence, expected=name, found_type=type(None))
        if not x:
            return None

        assert_type(
            hasattr(x, '__getitem__') and hasattr(x, '__len__'),
            ctx=new_ctx_sequence, expected=name, found_type=type(x))

        result = []
        i = 0

        for d in x:
            new_ctx = context.create(new_ctx_sequence)
            new_ctx.append('[{}]'.format(i), separator='')

            result.append(combinator_element(d, ctx=new_ctx))
            i += 1

        return tuple(result)

    def _is_type(d):
        if not hasattr(d, '__getitem__') or not hasattr(d, '__len__'):
            return False

        for x in d:
            if not combinator_element.is_type(x):
                return False

        return True

    _sequence.is_type = _is_type
    _sequence.meta = {
        'name': name
    }
    _sequence.example = [combinator_element.example for _ in range(examples.ListSize)]
    return _sequence


def struct(combinators, name: str=None, strict: bool=False):
    if not name:
        base_name = strict and 'StrictStruct' or 'Struct'
        name = '{}{{{}}}'.format(base_name, ''.join(
            ', '.join(map(lambda k: '{}: {}'.format(k, get_type_name(combinators[k])), combinators))))
        if strict:
            name = '{}'.format(name)

    def _struct(x, ctx=None):
        ctx = context.create(ctx)
        if ctx.production_mode:
            return x

        if ctx.empty:
            ctx.append(name)

        is_type = _struct.is_type(x) or (type(x) is dict and (not strict or all(k in combinators for k in x.keys())))
        assert_type(is_type, ctx=ctx, expected=name, found_type=type(x))

        # Cannot proceed, this is not even a struct.
        if not is_type:
            return x

        if type(x) == p.StructType:
            return x

        new_dict = {}
        for k in combinators:
            new_ctx = context.create(ctx)
            new_ctx.append('[{}]'.format(k), separator='')
            new_dict[k] = combinators[k](x.get(k), ctx=new_ctx)
        return p.StructType(new_dict)

    def _is_type(d):
        result = p.is_struct_of(d, combinators) or \
                               type(d) == dict and all(combinators[k].is_type(d.get(k)) for k in combinators)
        return result and (not strict or all(k in combinators for k in d.keys()))

    _struct.is_type = _is_type

    _struct.meta = {
        'name': name
    }
    _struct.example = {x: v.example for x, v in combinators.items()}
    return _struct


def maybe(combinator, name=None):
    if not name:
        name = 'Maybe ({})'.format(get_type_name(combinator))

    def _maybe(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        new_ctx.append(name)
        assert_type(
            _maybe.is_type(x), ctx=new_ctx,
            found_type=type(x), expected='None or {}'.format(get_type_name(combinator)))

        return combinator(x, new_ctx) if x else None

    _maybe.is_type = lambda d: d is None or combinator.is_type(d)

    _maybe.meta = {
        'name': name
    }
    _maybe.example = combinator.example
    return _maybe


def _default_composite_dispatcher(x, combinators):
    for combinator in combinators:
        if combinator.is_type(x):
            return combinator

    return None


def union(*combinators, name=None, dispatcher=None):
    if not name:
        name = 'Union({})'.format(', '.join(map(lambda d: get_type_name(d), combinators)))

    def _union(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        if new_ctx.empty:
            new_ctx.append(name)
        assert_type(_union.is_type(x), ctx=new_ctx,
                    expected=' or '.join(map(lambda d: get_type_name(d), combinators)), found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator = _default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=new_ctx) if default_combinator else None

    _union.is_type = lambda d: any(combinator.is_type(d) for combinator in combinators)

    _union.meta = {
        'name': name
    }

    _union.example = None
    for x in combinators:
        if x.example is not None:
            _union.example = x.example
            break

    return _union


def intersection(*combinators, example=None, name=None, dispatcher=None):
    if not name:
        name = 'Intersection({})'.format(
            ', '.join(map(lambda d: get_type_name(d), combinators)))

    def _intersection(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        new_ctx.append(name)
        assert_type(_intersection.is_type(x), ctx=new_ctx,
                    expected=' or '.join(map(lambda d: get_type_name(d), combinators)),
                    found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator = _default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=new_ctx)

    _intersection.meta = {
        'name': name
    }
    _intersection.is_type = lambda d: all(combinator.is_type(d) for combinator in combinators)
    _intersection.example = example

    return _intersection


def subtype(combinator, condition, example=None, name=None):
    if not name:
        name = 'Subtype({})'.format(get_type_name(combinator))

    def _subtype(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        if new_ctx.empty:
            new_ctx.append(name)
        combinator(x, new_ctx)
        assert_type(condition(x), ctx=new_ctx, expected=name, found_type=type(x))

        return combinator(x, new_ctx)

    _subtype.is_type = lambda d: combinator.is_type(d) and condition(d)

    _subtype.meta = {
        'name': name
    }
    _subtype.example = example or combinator.example

    return _subtype


def enum(values, name=None):
    sorted_enums = _orig_list(values.keys())
    sorted_enums.sort()

    if not name:
        name = 'Enum({})'.format(', '.join(map(lambda k: '{}: {}'.format(k, values[k]), sorted_enums)))

    def _enum(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        if new_ctx.empty:
            new_ctx.append(name)

        is_type = _enum.is_type(x)
        assert_type(
            is_type, ctx=new_ctx,
            expected=' or '.join(sorted_enums),
            found_type=str(x))

        if not is_type:
            return None
        return values[x]

    _enum.is_type = lambda d: d in values
    _enum.meta = {
        'name': name,
        map: values
    }

    enum_dict = {}
    enum_dict.update(_enum.__dict__)
    enum_dict.update(values)
    _enum.__dict__ = enum_dict
    _enum.example = _orig_list(values.keys())[0]
    return _enum

enum.of = lambda l, name=None: enum({k: k for k in l}, name=name)


def _typedef(args, kwargs, ctx=None):
    def wrapper(fun):
        @wraps(fun)
        def f(*inner_args, **inner_kwargs):
            assert_type(
                len(args) == len(inner_args), ctx=ctx, expected='{} arguments'.format(len(args)),
                found_type='{} arguments'.format(len(inner_args)))

            for i in range(len(args)):
                args[i](inner_args[i])

            for k in kwargs:
                kwargs[k](inner_kwargs.get(k))

            typesafe_args = (args[i](inner_args[i]) for i in range(len(args)))
            typesafe_kwargs = {k: kwargs[k](inner_kwargs[k]) for k in kwargs}
            return fun(*typesafe_args, **typesafe_kwargs)

        f.__pycomb__meta__ = {
            'args': args,
            'kwargs': kwargs
        }

        return f

    return wrapper


def function(*args, **kwargs):
    name = 'Function({})'.format(', '.join(
        _orig_list(map(lambda k: '{}'.format(get_type_name(k)), args)) +
        _orig_list(map(lambda k: '{}={}'.format(k, get_type_name(kwargs[k])), kwargs))))

    def _function(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        new_ctx.append(name)

        assert_type(_function.is_type(x), ctx=new_ctx, expected=name, found_type=type(x))

        return x if '__pycomb__meta__' in dir(x) else _typedef(args, kwargs, ctx=new_ctx)(x)

    _function.is_type = lambda d: callable(d)
    _function.meta = {
        'name': name,
        'args': args,
        'kwargs': kwargs
    }
    # TODO I should declare a function based on the combinators.
    _function.example = lambda *a, **kw: None
    return _function

Number = union(Int, Float, name='Number')


def generic_object(fields_combinators: dict, object_type, example=None, name=None):
    name = name or object_type.__name__

    def _object(x, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return x

        if new_ctx.empty:
            new_ctx.append(name)

        assert_type(type(x) == object_type, ctx=new_ctx, expected=name, found_type=type(x))

        for field in fields_combinators:
            cur_field_combinator = fields_combinators[field]

            field_new_ctx = context.create(new_ctx)
            field_new_ctx.append(field)
            cur_field_combinator(getattr(x, field), ctx=field_new_ctx)

        return x

    def _is_type(d):
        return type(d) == object_type and \
                               all(fields_combinators[k].is_type(getattr(d, k)) for k in fields_combinators)

    def _build_example():
        try:
            result = object_type()
            for field_name, field_combinator in fields_combinators.items():
                setattr(result, field_name, field_combinator.example)
        except:
            result = None
        return result

    _object.is_type = _is_type
    _object.example = example or _build_example()
    _object.meta = {
        'name': name
    }

    return _object


def regexp_group(pattern: str, *combinators, example=None, name=None):
    name = name or 'RegexpGroup({})'.format(pattern)
    if not pattern or not isinstance(pattern, str):
        raise ValueError

    pattern = '^' + pattern if pattern[0] != '^' else pattern
    pattern = pattern + '$' if pattern[-1] != '$' else pattern
    pattern = re.compile(pattern)
    if pattern.groups != len(combinators):
        raise ValueError

    def _regexp_group(value, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.production_mode:
            return value

        if new_ctx.empty:
            new_ctx.append(name)

        if not isinstance(value, str):
            assert_type(False, ctx=new_ctx, expected=name, found_type=type(value))
        matcher = pattern.match(value)
        if not matcher:
            assert_type(False, ctx=new_ctx, expected=name, found_type=type(value))
        idx = 0
        for x in zip(combinators, matcher.groups()):
            sub_ctx = context.create(new_ctx)
            sub_ctx.append('[{}]'.format(idx), separator='')
            combinator = x[0]
            group = x[1]
            combinator(group, ctx=sub_ctx)
            idx += 1
        return value

    def _is_type(d):
        if not isinstance(d, str):
            return False
        matcher = pattern.match(d)
        if not matcher:
            return False
        groups = matcher.groups()

        return all(
            (x[0].is_type(x[1]) for x in zip(combinators, groups))
        )

    _regexp_group.is_type = _is_type

    _regexp_group.meta = {
        'name': name
    }
    _regexp_group.example = example
    return _regexp_group

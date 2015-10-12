from pycomb import predicates as p
from pycomb.base import _get_type_name, _get_path, _setup_paths_and_contexts


def _default_element_serializer(combinators, _, __):
    return _get_type_name(combinators)

def _assert_msg(guard, msg, ctx=None):
    path = _get_path(ctx)
    if not guard:
        if len(path) == 1:
            raise ValueError('Error on {}: {}'.format(path[0], msg))
        raise ValueError('Error on {}: {}'.format(''.join(path[:-1]) + ': ' + path[-1], msg))

def _assert(guard, ctx=None, expected=None, found_type=None):
    path = _get_path(ctx)
    if not guard:
        found_type = found_type if type(found_type) is str else found_type.__name__
        if len(path) == 1:
            raise ValueError('Error on {}: expected {} but was {}'.format(path[0], expected, found_type))
        raise ValueError('Error on {}: expected {} but was {}'.format(''.join(path[:-1]) + ': ' + path[-1], expected, found_type))

def irreducible(predicate, name='Irreducible'):
    def Irreducible(value, ctx=None):
        new_ctx = _setup_paths_and_contexts(Irreducible, ctx, '' if _get_path(ctx) else name)

        _assert(Irreducible.is_type(value), ctx=new_ctx, expected=name, found_type=type(value))

        return value

    Irreducible.is_type = predicate

    Irreducible.meta = {
        'name': name
    }
    return Irreducible


Int = irreducible(p.is_int, name='Int')
Float = irreducible(p.is_float, name='Float')
String = irreducible(p.is_string, name='String')


def list(combinator_element, name=None):
    if name and type(name) != str:
        raise ValueError('Invalid name supplied to {}: expected str for \'name\''
                         .format('List({})'.format(_get_type_name(combinator_element))))
    if not name:
        name = 'List({})'.format(_get_type_name(combinator_element))

    def List(*x, ctx=None):
        new_ctx_list = _setup_paths_and_contexts(List, ctx, '' if _get_path(ctx) else name)

        _assert_msg(x, 'missing 1 required positional argument: \'x\'', ctx=new_ctx_list)
        _assert(lambda d: type(d) in (__builtins__['list'], tuple), ctx=new_ctx_list, found_type=type(x))

        result = []
        i = 0

        for d in x:
            new_ctx = _setup_paths_and_contexts(List, new_ctx_list, '[{}]'.format(i) if _get_path(new_ctx_list) else name)
            result.append(combinator_element(d, ctx=new_ctx))
            i += 1

        return tuple(result)

    def _is_type(d):
        if not type(d) in (__builtins__['list'], tuple):
            return False

        for x in d:
            if not combinator_element.is_type(x):
                return False

        return True

    List.is_type = _is_type
    List.meta = {
        'name': name
    }
    return List

def struct(combinators, name=None):
    if not name:
        name = 'Struct{{{}}}'.format(''.join(
            ', '.join(map(lambda k: '{}: {}'.format(k, _get_type_name(combinators[k])), combinators))))

    def Struct(x, ctx=None):
        _assert(Struct.is_type(x) or type(x) is dict, ctx=ctx, expected=name, found_type=type(x))

        if type(x) == p.StructType:
            return x

        new_dict = {}
        for k in combinators:
            selector = '[{}]'.format(k) if _get_path(ctx) else '{}[{}]'.format(name, k)
            new_ctx = _setup_paths_and_contexts(Struct, ctx, selector)
            new_dict[k] = combinators[k](x[k], ctx=new_ctx)
        return p.StructType(new_dict)

    Struct.is_type = lambda d: p.is_struct_of(d, combinators) or \
                               type(d) == dict and all(combinators[k].is_type(d[k]) for k in combinators)

    Struct.meta = {
        'name': name
    }
    return Struct

def maybe(combinator, name=None):
    if not name:
        name = 'Maybe ({})'.format(_get_type_name(combinator))

    def Maybe(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Maybe, ctx, name)
        _assert(Maybe.is_type(x), ctx=new_ctx, found_type=type(x))

        return combinator(x, new_ctx) if x else None

    Maybe.is_type = lambda d: d is None or combinator.is_type(d)

    Maybe.meta = {
        'name': name
    }
    return Maybe

def _default_composite_dispatcher(x, combinators):
    for combinator in combinators:
        if combinator.is_type(x):
            return combinator

    return None

def union(*combinators, name=None, dispatcher=None):
    if not name:
        name = 'Union({})'.format(', '.join(map(lambda d: _get_type_name(d), combinators)))

    def Union(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Union, ctx, name)
        _assert(Union.is_type(x), ctx=new_ctx,
                expected=' or '.join(map(lambda d: _get_type_name(d), combinators)), found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator = _default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=new_ctx)

    Union.is_type = lambda d: any(combinator.is_type(d) for combinator in combinators)

    Union.meta = {
        'name': name
    }

    return Union

def intersection(*combinators, name=None, dispatcher=None):
    if not name:
        name = 'Intersection({})'.format(
            ', '.join(map(lambda d: _get_type_name(d), combinators)))

    def Intersection(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Intersection, ctx, name)
        _assert(Intersection.is_type(x), ctx=new_ctx,
                expected=' or '.join(map(lambda d: _get_type_name(d), combinators)),
                found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator =_default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=ctx)

    Intersection.meta = {
        'name': name
    }
    Intersection.is_type = lambda d: all(combinator.is_type(d) for combinator in combinators)

    return Intersection

def subtype(combinator, condition, name=None):
    if not name:
        name = 'Subtype({})'.format(_get_type_name(combinator))

    def Subtype(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Subtype, ctx, name)
        _assert(Subtype.is_type(x), ctx=new_ctx, expected=name, found_type=type(x))

        return combinator(x, new_ctx)

    Subtype.is_type = lambda d: combinator.is_type(d) and condition(d)

    Subtype.meta = {
        'name': name
    }

    return Subtype

def enum(values, name=None):
    sorted_enums = __builtins__['list'](values.keys())
    sorted_enums.sort()

    if not name:
        name = 'Enum({})'.format(', '.join(map(lambda k: '{}: {}'.format(k, values[k]), sorted_enums)))

    def Enum(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Enum, ctx, name)

        _assert(Enum.is_type(x), ctx=new_ctx,
                expected=' or '.join(sorted_enums),
                found_type=str(x))

        return values[x]

    Enum.is_type = lambda d: d in values
    Enum.meta = {
        'name': name,
        map: values
    }

    enum_dict = {}
    enum_dict.update(Enum.__dict__)
    enum_dict.update(values)
    Enum.__dict__ = enum_dict

    return Enum

enum.of = lambda l, name=None: enum({k: k for k in l}, name=name)

def _typedef(args, kwargs, ctx=None):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            _assert(len(args) == len(inner_args), ctx=ctx, expected='{} arguments'.format(len(args)),
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
        __builtins__['list'](map(lambda k: '{}'.format(_get_type_name(k)), args)) +
        __builtins__['list'](map(lambda k: '{}={}'.format(k, _get_type_name(kwargs[k])), kwargs))))

    def Function(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Function, ctx, name)

        _assert(Function.is_type(x), ctx=new_ctx, expected=name, found_type=type(x))

        return x if '__pycomb__meta__' in dir(x) else _typedef(args, kwargs, ctx=new_ctx)(x)

    Function.is_type = lambda d: callable(d)
    Function.meta = {
        'name': name,
        'args': args,
        'kwargs': kwargs
    }

    return Function

Number = union(Int, Float, name='Number')

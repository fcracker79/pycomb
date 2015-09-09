from pycomb.predicates import is_int, is_float, is_string, is_list_of, is_struct_of, StructType

def _get_type_name(type):
    return type.meta['name']

def _get_path(ctx):
    return ctx['path']

def _new_ctx():
    return {'path': []}

def _setup_paths_and_contexts(type, ctx, name):
    path = _get_path(ctx) + [name] if ctx else [name]
    type.Meta = {'path': path}

    return {'path': path}

def _get_derivated_name(base_name, *combinators):
    if type(combinators) is dict:
        combinators_str = map(lambda k: '{}: {}'.format(k, _get_type_name(combinators[k])), combinators)
    elif type(combinators) is list or type(combinators) is tuple:
        combinators_str = map(lambda c: _get_type_name(c), combinators)
    else:
        combinators_str = _get_type_name(*combinators)

    return '{} ({})'.format(
        base_name,
        combinators_str)


def _assert(guard, ctx=None, found_type=None):
    path = _get_path(ctx)
    if not guard:
        if len(path):
            expected = path[-1]
            raise ValueError('Error on {}: expected {} but was {}'.format(path, expected, found_type))
        else:
            raise ValueError('Error on {}:  was {}'.format(path, found_type))

def irreducible(predicate, name='Irreducible'):
    def Irreducible(value, ctx=None):
        new_ctx = _setup_paths_and_contexts(Irreducible, ctx, name)

        _assert(Irreducible.is_type(value), ctx=new_ctx, found_type=type(value))

        return value

    Irreducible.is_type = predicate

    Irreducible.meta = {
        'name': name
    }
    return Irreducible


Int = irreducible(is_int, name='Int')
Float = irreducible(is_float, name='Float')
String = irreducible(is_string, name='String')


def list(combinator_element, name=None):
    if not name:
        name = _get_derivated_name('List', combinator_element)

    def List(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(List, ctx, name)
        _assert(List.is_type(x), ctx=new_ctx, found_type=type(x))

        if type(x) == tuple:
            return x

        result = ()
        for d in x:
            result += (combinator_element(d, ctx=new_ctx), )
        return result

    List.is_type = lambda d: is_list_of(d, combinator_element)
    List.meta = {
        'name': name
    }
    return List

def struct(combinators, name=None):
    if not name:
        name = _get_derivated_name('Struct', combinators)

    def Struct(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Struct, ctx, name)
        _assert(Struct.is_type(x), ctx=new_ctx, found_type=type(x))

        if type(x) == StructType:
            return x

        return StructType({k: combinators[k](x[k], ctx=new_ctx) for k in combinators})

    Struct.is_type = lambda d: is_struct_of(d, combinators) or \
                               type(d) == dict and all(combinators[k].is_type(d[k]) for k in combinators)

    Struct.meta = {
        'name': name
    }
    return Struct

def maybe(combinator, name=None):
    if not name:
        name = _get_derivated_name('Maybe', combinator)

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
        name = _get_derivated_name('Union', combinators)

    def Union(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Union, ctx, name)
        _assert(Union.is_type(x), ctx=new_ctx, found_type=type(x))

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
        name = _get_derivated_name('Union', combinators)

    def Intersection(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Intersection, ctx, name)
        _assert(Intersection.is_type(x), ctx=new_ctx, found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator =_default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=new_ctx)

        return x

    Intersection.meta = {
        'name': name
    }
    Intersection.is_type = lambda d: all(combinator.is_type(d) for combinator in combinators)

def subtype(combinator, condition, name='Subtype'):
    def Subtype(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Subtype, ctx, name)
        _assert(Subtype.is_type(x), ctx=new_ctx, found_type=type(x))

        return combinator(x, new_ctx)

    Subtype.is_type = lambda d: combinator.is_type(d) and condition(d)

    Subtype.meta = {
        'name': name
    }

    return Subtype

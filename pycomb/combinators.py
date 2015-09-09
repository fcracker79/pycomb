from pycomb import predicates as p

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

def _dict_serializer(combinators, base_name, get_name_function):
    if type(combinators) == dict:
        map_result = ', '.join(map(lambda k: '{}: {}'.format(k, get_name_function(combinators[k])), combinators))
        return '{} {{{}}}'.format(base_name, map_result)

    return None

def _list_serializer(combinators, base_name, get_name_function):
    if type(combinators) in (list, tuple):
        list_result = ', '.join(map(lambda x: get_name_function(x), combinators))
        return '{} [{}]'.format(base_name, list_result)

    return None

def _default_element_serializer(combinators, _, __):
    return _get_type_name(combinators)

ELEMENTS_SERIALIZERS = (_dict_serializer, _list_serializer, _default_element_serializer)

def _get_derivated_name(base_name, combinators):
    result = None
    for serializer in ELEMENTS_SERIALIZERS:
        result = serializer(combinators, base_name, lambda d: _get_derivated_name(_get_type_name(d), d))
        if result:
            break

    assert result is not None

    return result

def _assert(guard, ctx=None, found_type=None):
    path = _get_path(ctx)
    if not guard:
        if len(path):
            expected = path[-1]
            raise ValueError('Error on {}: expected {} but was {}'.format(path, expected, found_type.__name__))
        else:
            raise ValueError('Error on {}:  was {}'.format(path, found_type.__name__))

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


Int = irreducible(p.is_int, name='Int')
Float = irreducible(p.is_float, name='Float')
String = irreducible(p.is_string, name='String')


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

    List.is_type = lambda d: p.is_list_of(d, combinator_element)
    List.meta = {
        'name': name
    }
    return List

def struct(combinators, name=None):
    if not name:
        name = _get_derivated_name('Struct', combinators)

    def Struct(x, ctx=None):
        new_ctx = _setup_paths_and_contexts(Struct, ctx, name)

        _assert(Struct.is_type(x) or type(x) is dict, ctx=new_ctx, found_type=type(x))

        if type(x) == p.StructType:
            return x

        return p.StructType({k: combinators[k](x[k], ctx=new_ctx) for k in combinators})

    Struct.is_type = lambda d: p.is_struct_of(d, combinators) or \
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

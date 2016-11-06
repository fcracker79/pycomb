from pycomb import predicates as p, context

_orig_list = list


def get_type_name(type_obj):
    return type_obj.meta['name']


def _assert(guard, ctx, expected=None, found_type=None):
    if not guard:
        ctx.notify_error(expected, found_type)


def irreducible(predicate, name='Irreducible'):
    def _irreducible(value, ctx=None):
        new_ctx = context.create(ctx)
        if new_ctx.empty:
            new_ctx.append(name)

        _assert(_irreducible.is_type(value), ctx=new_ctx, expected=name, found_type=type(value))

        return value

    _irreducible.is_type = predicate

    _irreducible.meta = {
        'name': name
    }
    return _irreducible


Int = irreducible(p.is_int, name='Int')
Float = irreducible(p.is_float, name='Float')
String = irreducible(p.is_string, name='String')


# noinspection PyShadowingBuiltins
def list(combinator_element, name=None):
    if not name:
        name = 'List({})'.format(get_type_name(combinator_element))

    def _list(x, ctx=None):
        new_ctx_list = context.create(ctx)
        if new_ctx_list.empty:
            new_ctx_list.append(name)

        if not x:
            raise ValueError('Error on {}: missing 1 required positional argument: \'x\''.format(new_ctx_list.path))

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
    return _list


def struct(combinators, name=None):
    if not name:
        name = 'Struct{{{}}}'.format(''.join(
            ', '.join(map(lambda k: '{}: {}'.format(k, get_type_name(combinators[k])), combinators))))

    def _struct(x, ctx=None):
        ctx = context.create(ctx)
        if ctx.empty:
            ctx.append(name)

        _assert(_struct.is_type(x) or type(x) is dict, ctx=ctx, expected=name, found_type=type(x))

        if type(x) == p.StructType:
            return x

        new_dict = {}
        for k in combinators:
            new_ctx = context.create(ctx)
            new_ctx.append('[{}]'.format(k), separator='')
            new_dict[k] = combinators[k](x[k], ctx=new_ctx)
        return p.StructType(new_dict)

    def _is_type(d):
        return p.is_struct_of(d, combinators) or \
                               type(d) == dict and all(combinators[k].is_type(d[k]) for k in combinators)

    _struct.is_type = _is_type

    _struct.meta = {
        'name': name
    }
    return _struct


def maybe(combinator, name=None):
    if not name:
        name = 'Maybe ({})'.format(get_type_name(combinator))

    def _maybe(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)
        _assert(
            _maybe.is_type(x), ctx=new_ctx,
            found_type=type(x), expected='None or {}'.format(get_type_name(combinator)))

        return combinator(x, new_ctx) if x else None

    _maybe.is_type = lambda d: d is None or combinator.is_type(d)

    _maybe.meta = {
        'name': name
    }
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
        if new_ctx.empty:
            new_ctx.append(name)
        _assert(_union.is_type(x), ctx=new_ctx,
                expected=' or '.join(map(lambda d: get_type_name(d), combinators)), found_type=type(x))

        if dispatcher:
            default_combinator = dispatcher(x)
            assert default_combinator in combinators
        else:
            default_combinator = _default_composite_dispatcher(x, combinators)

        return default_combinator(x, ctx=new_ctx)

    _union.is_type = lambda d: any(combinator.is_type(d) for combinator in combinators)

    _union.meta = {
        'name': name
    }

    return _union


def intersection(*combinators, name=None, dispatcher=None):
    if not name:
        name = 'Intersection({})'.format(
            ', '.join(map(lambda d: get_type_name(d), combinators)))

    def _intersection(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)
        _assert(_intersection.is_type(x), ctx=new_ctx,
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

    return _intersection


def subtype(combinator, condition, name=None):
    if not name:
        name = 'Subtype({})'.format(get_type_name(combinator))

    def _subtype(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)
        _assert(_subtype.is_type(x), ctx=new_ctx, expected=name, found_type=type(x))

        return combinator(x, new_ctx)

    _subtype.is_type = lambda d: combinator.is_type(d) and condition(d)

    _subtype.meta = {
        'name': name
    }

    return _subtype


def enum(values, name=None):
    sorted_enums = _orig_list(values.keys())
    sorted_enums.sort()

    if not name:
        name = 'Enum({})'.format(', '.join(map(lambda k: '{}: {}'.format(k, values[k]), sorted_enums)))

    def _enum(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)

        _assert(_enum.is_type(x), ctx=new_ctx,
                expected=' or '.join(sorted_enums),
                found_type=str(x))

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

    return _enum

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
        _orig_list(map(lambda k: '{}'.format(get_type_name(k)), args)) +
        _orig_list(map(lambda k: '{}={}'.format(k, get_type_name(kwargs[k])), kwargs))))

    def _function(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)

        _assert(_function.is_type(x), ctx=new_ctx, expected=name, found_type=type(x))

        return x if '__pycomb__meta__' in dir(x) else _typedef(args, kwargs, ctx=new_ctx)(x)

    _function.is_type = lambda d: callable(d)
    _function.meta = {
        'name': name,
        'args': args,
        'kwargs': kwargs
    }

    return _function

Number = union(Int, Float, name='Number')


def generic_object(fields_combinators: dict, object_type):
    name = object_type.__name__

    def _object(x, ctx=None):
        new_ctx = context.create(ctx)
        new_ctx.append(name)

        _assert(type(x) == object_type, ctx=new_ctx, expected=name, found_type=type(x))

        for field in fields_combinators:
            cur_field_combinator = fields_combinators[field]

            field_new_ctx = context.create(new_ctx)
            field_new_ctx.append(field)
            cur_field_combinator(getattr(x, field), ctx=field_new_ctx)

        return x

    def _is_type(d):
        return type(d) == object_type and \
                               all(fields_combinators[k].is_type(getattr(d, k)) for k in fields_combinators)
    _object.is_type = _is_type

    _object.meta = {
        'name': name
    }

    return _object

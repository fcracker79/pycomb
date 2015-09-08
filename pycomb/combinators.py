from pycomb.predicates import is_int, is_float, is_string, is_list_of, is_struct_of, StructType


def _assert(guard):
    if not guard:
        raise ValueError


def irreducible(name, predicate):
    def Irreducible(value):
        _assert(Irreducible.is_type(value))

        return value

    Irreducible.is_type = predicate
    return Irreducible


Int = irreducible('Int', is_int)
Float = irreducible('Float', is_float)
String = irreducible('String', is_string)


def list(combinator_element):
    def List(x):
        _assert(List.is_type(x))

        result = ()
        for d in x:
            result += (combinator_element(d), )
        return result

    List.is_type = lambda d: is_list_of(d, combinator_element)

    return List

def struct(combinators):
    def Struct(x):
        _assert(Struct.is_type(x))

        return x if type(x) == StructType else StructType(x)

    Struct.is_type = lambda d: is_struct_of(d, combinators) or \
                               type(d) == dict and all(combinators[k].is_type(d[k]) for k in combinators)

    return Struct

def maybe(combinator):
    def Maybe(x):
        _assert(Maybe.is_type(x))

        return combinator(x) if x else None

    Maybe.is_type = lambda d: d is None or combinator.is_type(d)

    return Maybe

def union(*combinators):
    def Union(x):
        _assert(Union.is_type(x))

        return x

    Union.is_type = lambda d: any(combinator.is_type(d) for combinator in combinators)

    return Union

def intersection(*combinators):
    def Intersection(x):
        _assert(Intersection.is_type(x))

        return x

    Intersection.is_type = lambda d: all(combinator.is_type(d) for combinator in combinators)

def subtype(combinator, condition):
    def Subtype(x):
        _assert(Subtype.is_type(x))

        return x

    Subtype.is_type = lambda d: combinator.is_type(d) and condition(d)

    return Subtype

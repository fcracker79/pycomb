def is_int(x):
    return type(x) == int


def is_float(x):
    return type(x) == float


def is_string(x):
    return type(x) == str


def is_bool(x):
    return type(x) == bool


def is_list_of(d, combinator_element):
    return type(d) in (list, tuple) and all(combinator_element.is_type(element) for element in d)


class StructType:
        def __init__(self, x):
            super.__setattr__(self, 'x', x)

        def __getattr__(self, item):
            return self.x[item]

        def __setattr__(self, key, value):
            raise TypeError


def is_struct_of(d, combinators):
    return type(d) == StructType

from pycomb.base import _new_ctx


def returning(combinator):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            result = fun(*inner_args, **inner_kwargs)

            return combinator(result, ctx=_new_ctx())
        return f

    return wrapper
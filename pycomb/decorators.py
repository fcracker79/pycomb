from pycomb.base import new_ctx


def returning(combinator):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            result = fun(*inner_args, **inner_kwargs)

            return combinator(result, ctx=new_ctx())
        return f

    return wrapper
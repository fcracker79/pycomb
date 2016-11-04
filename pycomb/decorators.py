from pycomb import context


def returning(combinator):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            result = fun(*inner_args, **inner_kwargs)

            return combinator(result, ctx=context.create())
        return f

    return wrapper

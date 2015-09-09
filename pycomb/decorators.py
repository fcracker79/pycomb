from pycomb.combinators import _new_ctx


def typedef(*args, **kwargs):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            for i in range(len(args)):
                args[i](inner_args[i])

            for k in kwargs:
                kwargs[k](inner_kwargs.get(k))

            typesafe_args = (args[i](inner_args[i]) for i in range(len(args)))
            typesafe_kwargs = {k:kwargs[k](inner_kwargs[k]) for k in kwargs}
            return fun(*typesafe_args, **typesafe_kwargs)
        return f

    return wrapper

def returning(combinator):
    def wrapper(fun):
        def f(*inner_args, **inner_kwargs):
            result = fun(*inner_args, **inner_kwargs)

            return combinator(result, ctx=_new_ctx())
        return f

    return wrapper
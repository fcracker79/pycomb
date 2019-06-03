from pycomb import combinators, context
from pycomb.decorators import returning
import unittest


class TestCustomContextInDecorators(unittest.TestCase):
    def test(self):
        def is_positive(x: int) -> bool:
            return x >= 0

        def is_integer(x: int) -> bool:
            return x % 1 == 0

        def is_natural(x: int) -> bool:
            return is_positive(x) and is_integer(x)

        natural_numbers = combinators.subtype(
            combinators.Int, is_natural, example=42, name="Natural number"
        )

        class MyException(Exception):
            def __init__(self, expected_type, found_type, found_value):
                self.expected_type, self.found_type, self.found_value = expected_type, found_type, found_value

        class MyObserver(context.ValidationErrorObserver):
            def on_error(self, ctx, expected_type, found_type):
                raise MyException(expected_type, found_type, ctx.validating_value)

        my_context = context.create(validation_error_observer=MyObserver())
        fun = combinators.function(natural_numbers, natural_numbers).with_context(my_context)

        @fun
        @returning(natural_numbers, ctx=my_context)
        def add(a, b) -> int:
            return a + b

        add(1, 2)
        with self.assertRaises(MyException) as e:
            add(1, "hello")
        self.assertEqual(str, e.exception.found_type)
        self.assertEqual('Int', e.exception.expected_type)
        self.assertEqual("hello", e.exception.found_value)
        @fun
        @returning(natural_numbers, ctx=my_context)
        def bad_add(a, b):
            return "hello_return"
        with self.assertRaises(MyException) as e:
            bad_add(1, 2)
        self.assertEqual(str, e.exception.found_type)
        self.assertEqual('Int', e.exception.expected_type)
        self.assertEqual("hello_return", e.exception.found_value)

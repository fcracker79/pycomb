from unittest import TestCase
from pycomb import predicates, combinators


class TestPredicates(TestCase):
    def test_is_list_of(self):
        l = [1, 2, 3]
        self.assertTrue(predicates.is_list_of(l, combinators.Number))
        self.assertFalse(predicates.is_list_of(l, combinators.String))

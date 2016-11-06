import contextlib
import unittest


@contextlib.contextmanager
def throws_with_message(*messages):
    tc = unittest.TestCase('__init__')

    with tc.assertRaises(Exception) as e:
        yield
    msg = e.exception.args[0]
    tc.assertTrue(
        msg in messages,
        msg='Message: {}\nPossible messages: {}'.format(msg, messages)
    )

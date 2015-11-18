import unittest

def throws_with_message(f, *messages):
    tc = unittest.TestCase('__init__')

    msg = None
    try:
        f()
    except Exception as e:
        msg = e.args[0]

    tc.assertTrue(
        msg in messages,
        msg='Message: {}\nPossible messages: {}'.format(msg, messages)
    )
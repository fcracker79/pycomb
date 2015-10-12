import unittest

def throws_with_message(f, message):
    tc = unittest.TestCase('__init__')

    msg = None
    try:
        f()
    except Exception as e:
        msg = e.args[0]

    tc.assertEqual(message, msg)
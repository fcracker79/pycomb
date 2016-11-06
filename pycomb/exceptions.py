class PyCombValidationError(Exception):
    def __init__(self, *a, expected_type=None, found_type=None, **kw):
        self.expected_type = expected_type
        self.found_type = found_type
        Exception.__init__(self, *a, **kw)

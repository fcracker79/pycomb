import abc


class ValidationErrorObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_error(self, ctx, expected_type, found_type):
        pass


class ValidationErrorObservable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_error_listener(self, error_listener):
        pass

    @abc.abstractmethod
    def notify_error(self, expected_type, found_type):
        pass


class ValidationContext(ValidationErrorObservable, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, path_element):
        pass  # pragma: no cover

    @abc.abstractmethod
    def path(self):
        pass  # pragma: no cover

    @property
    @abc.abstractmethod
    def empty(self):
        pass  # pragma: no cover


class ValidationContextImpl(ValidationContext):
    def __init__(self):
        self._path = []
        self._path_str = None
        self._error_listeners = []

    def append(self, path_element, separator='.'):
        self._path_str = None
        if self._path:
            self._path.append(separator)
        self._path.append(path_element)

    @property
    def path(self):
        if self._path_str is None:
            self._path_str = ''.join(self._path)
        return self._path_str

    @property
    def empty(self):
        return not bool(self._path)

    def copy(self):
        result = ValidationContextImpl()
        result._path = [x for x in self._path]
        result._path_str = self._path_str
        result._error_listeners = [x for x in self._error_listeners]
        return result

    def add_error_listener(self, error_listener):
        self._error_listeners.append(error_listener)

    def notify_error(self, expected_type, found_type):
        for l in self._error_listeners:
            l.on_error(self, expected_type, found_type)


def _assert_msg(guard, msg, ctx):
    if not guard:
        raise ValueError(_generate_error_message(ctx, msg=msg))


def _generate_error_message(ctx, expected=None, found_type=None, msg=None):
    return 'Error on {}: {}'.format(ctx.path, msg) if msg \
        else 'Error on {}: expected {} but was {}'.format(
            ctx.path, expected, found_type)


class _DefaultValidationErrorObserver(ValidationErrorObserver):
    def on_error(self, ctx, expected_type, found_type):
        found_type = found_type if type(found_type) is str else found_type.__name__
        raise ValueError(_generate_error_message(ctx, expected_type, found_type))

_default_validation_error_observer = _DefaultValidationErrorObserver()


def create(base_ctx=None, validation_error_observer=_default_validation_error_observer):
    result = base_ctx.copy() if base_ctx else ValidationContextImpl()
    if validation_error_observer:
        result.add_error_listener(validation_error_observer)
    return result


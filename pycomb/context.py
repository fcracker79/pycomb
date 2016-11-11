import abc
from pycomb import exceptions


class ValidationErrorObserver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_error(self, ctx, expected_type, found_type):
        pass  # pragma: no cover


class ValidationErrorObservable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_error_observer(self, error_observer):
        pass  # pragma: no cover

    @abc.abstractmethod
    def notify_error(self, expected_type, found_type):
        pass  # pragma: no cover


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

    @property
    @abc.abstractmethod
    def production_mode(self):
        pass  # pragma: no cover


class ValidationContextImpl(ValidationContext):
    def __init__(self, production_mode):
        self._path = []
        self._path_str = None
        self._error_observers = []
        self._production_mode = production_mode

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
        result = ValidationContextImpl(self.production_mode)
        result._path = [x for x in self._path]
        result._path_str = self._path_str
        result._error_observers = [x for x in self._error_observers]
        return result

    def add_error_observer(self, error_observer):
        self._error_observers.append(error_observer)

    def notify_error(self, expected_type, found_type):
        for l in self._error_observers:
            l.on_error(self, expected_type, found_type)

    @property
    def production_mode(self):
        return self._production_mode


def _generate_error_message(ctx, expected=None, found_type=None, msg=None):
    return 'Error on {}: {}'.format(ctx.path, msg) if msg \
        else 'Error on {}: expected {} but was {}'.format(
            ctx.path, expected, found_type)


class _DefaultValidationErrorObserver(ValidationErrorObserver):
    def on_error(self, ctx, expected_type, found_type):
        found_type = found_type if type(found_type) is str else found_type.__name__
        raise exceptions.PyCombValidationError(
            _generate_error_message(ctx, expected_type, found_type),
            expected_type=expected_type, found_type=found_type)

_default_validation_error_observer = _DefaultValidationErrorObserver()


def create(base_ctx=None, validation_error_observer=_default_validation_error_observer,
           production_mode=False):
    result = base_ctx.copy() if base_ctx else ValidationContextImpl(production_mode)
    if not base_ctx:
        result.add_error_observer(validation_error_observer)
    return result

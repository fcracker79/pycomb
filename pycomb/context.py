import abc


class ValidationContext(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, path_element):
        pass

    @abc.abstractmethod
    def path(self):
        pass

    @property
    @abc.abstractmethod
    def path_elements(self):
        pass

    @property
    @abc.abstractmethod
    def empty(self):
        pass


class ValidationContextImpl(ValidationContext):
    def __init__(self):
        self._path = []
        self._path_str = None

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
    def path_elements(self):
        return tuple(self._path)

    @property
    def empty(self):
        return not bool(self._path)

    def copy(self):
        result = ValidationContextImpl()
        result._path = [x for x in self._path]
        result._path_str = self._path_str
        return result


def create(base_ctx=None):
    return base_ctx.copy() if base_ctx else ValidationContextImpl()

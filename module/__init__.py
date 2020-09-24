from object.value_object import ValueObject


class Module:

    def __init__(self):
        self.prepared = False

    def _prepare(self):
        raise NotImplementedError()

    def _process(self, value_object: ValueObject) -> ValueObject:
        raise NotImplementedError()

    def prepare(self):
        if not self.prepared:
            self._prepare()

    def process(self, value_object: ValueObject) -> ValueObject:
        return self._process(value_object)

import logging

from module import Module
from object.value_object import ValueObject

logger = logging.getLogger(__name__)


class SubTractModule(Module):

    NAMESPACE = 'module_subtract'

    def _prepare(self):
        logger.info('Module {} initialized.'.format(self.__class__))

    def _process(self, value_object: ValueObject):
        value_object.value = value_object.value - 10
        return value_object

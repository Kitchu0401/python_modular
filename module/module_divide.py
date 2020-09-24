import logging

from module import Module
from object.value_object import ValueObject

logger = logging.getLogger(__name__)


class DivideModule(Module):

    NAMESPACE = 'module_divide'

    def _prepare(self):
        logger.info('Module {} initialized.'.format(self.__class__))

    def _process(self, value_object: ValueObject):
        value_object.value = value_object.value / 2
        return value_object

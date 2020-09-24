import logging
import unittest

from module.module_manager import ModuleManager
from object.value_object import ValueObject

logger = logging.getLogger(__name__)


class ModuleTestCase:

    def __init__(self, initial_value=0, module_list=[], expected_value=0):
        self.initial_value = initial_value
        self.module_list = module_list
        self.expected_value = expected_value


class SimpleTest(unittest.TestCase):

    def setUp(self) -> None:
        self.cases = [
            ModuleTestCase(initial_value=0,
                           module_list=['module_add', 'module_add', 'module_multiply'],
                           expected_value=40)
        ]

    def test(self):
        for case in self.cases:
            assert isinstance(case, ModuleTestCase)

            value_object = ValueObject(initial_value=case.initial_value)

            module_manager = ModuleManager()
            module_manager.default_modules = case.module_list

            result: ValueObject = module_manager.process(value_object=value_object)

            self.assertEqual(result.value, case.expected_value)


if __name__ == '__main__':
    unittest.main()

from module import Module
from module.module_add import AddModule
from module.module_divide import DivideModule
from module.module_multiply import MultiplyModule
from module.module_subtract import SubTractModule
from object.value_object import ValueObject

MODULES = {
    AddModule,
    DivideModule,
    MultiplyModule,
    SubTractModule
}


class ModuleManager:

    def __init__(self):
        self._modules = dict()  # {namespace: instance}
        self._default_modules = None  # namespaces

        self._init_modules()

    def _init_modules(self):
        # containing {module_namespace: module_instance}
        self.modules = {m.NAMESPACE: m() for m in MODULES}

        for module in self.modules.values():
            isinstance(module, Module)
            module.prepare()

    def process(self, value_object: ValueObject, modules=None) -> ValueObject:
        modules = modules or self.default_modules
        modules = [self.modules[m] for m in modules]

        for module in modules:
            isinstance(module, Module)
            value_object = module.process(value_object=value_object)
        return value_object

    @property
    def modules(self):
        return self._modules

    @modules.setter
    def modules(self, modules):
        self._modules = modules

    @property
    def default_modules(self):
        return self._default_modules

    @default_modules.setter
    def default_modules(self, default_modules):
        self._default_modules = default_modules

class ValueObject:

    def __init__(self, value=0, module_namespaces=[]):
        self.value = value
        self.module_namespaces = module_namespaces


class ModuleTest:

    def __init__(self, pipe_in, pipe_out):
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

    def _prepare(self):
        print(f'Module initialized: [{self.__class__.NAMESPACE}]')

    def prepare(self):
        self._prepare()

    def _process(self, value_object: ValueObject) -> ValueObject:
        raise NotImplementedError

    def process(self, value_object: ValueObject) -> ValueObject:
        # value_object: ValueObject = self.pipe_in.recv()
        # value_object = self._process(value_object=value_object)
        # self.pipe_out.send(value_object)
        return self._process(value_object=value_object)


class ModuleTestAdd(ModuleTest):

    NAMESPACE = 'module_add'

    def _process(self, value_object: ValueObject) -> ValueObject:
        value_object.value += 10
        return value_object


class ModuleTestSubtract(ModuleTest):

    NAMESPACE = 'module_subtract'

    def _process(self, value_object: ValueObject) -> ValueObject:
        value_object.value -= 10
        return value_object


class ModuleTestMultiply(ModuleTest):

    NAMESPACE = 'module_multiply'

    def _process(self, value_object: ValueObject) -> ValueObject:
        value_object.value *= 2
        return value_object


class ModuleTestDivide(ModuleTest):

    NAMESPACE = 'module_divide'

    def _process(self, value_object: ValueObject) -> ValueObject:
        value_object.value /= 2
        return value_object


from multiprocessing import Pipe, Process
from threading import Thread


class ModuleManagerTest:

    MODULES = {
        ModuleTestAdd,
        ModuleTestDivide,
        ModuleTestMultiply,
        ModuleTestSubtract
    }

    def __init__(self):
        self.modules = dict()
        self.module_input = dict()
        self.module_output = dict()
        self.routing_threads = list()

        for module in ModuleManagerTest.MODULES:
            module_input, module_output = Pipe()
            self.module_input[module.NAMESPACE] = module_input
            self.module_output[module.NAMESPACE] = module_output

            self.modules[module.NAMESPACE] = module(module_input, module_output)
            self.modules[module.NAMESPACE].prepare()

            routing_thread = Thread(target=self.route, args=(module_output, module.NAMESPACE,), daemon=True)
            routing_thread.start()
            self.routing_threads.append(routing_thread)

        # setting consumer handler?
        self.input, self.output = Pipe()
        consumer_handler = Thread(target=self.route, args=(self.output, 'consumer_handler',), daemon=True)
        consumer_handler.start()
        self.routing_threads.append(consumer_handler)

    def route(self, module_output, namespace_for_debug):
        """
        receive module process output from individual modules,
        forward it to another module (or Provider) referencing namespace in module chain
        """

        value_object: ValueObject = module_output.recv()
        print(f'[{namespace_for_debug}] Received:', value_object.value)

        # if there're remaining namespaces, route it.
        if value_object.module_namespaces:
            namespace = value_object.module_namespaces.pop(0)
            print('Sending to:', namespace)
            # self.module_input[value_object.module_namespaces.pop(0)].send(value_object)
            self.modules[namespace].process(value_object)
            self.module_output[namespace].send(value_object)
        # else if there's no remaining namespace, send it to Provider
        else:
            print('Ending process.')
            self.provide(value_object)

    def provide(self, value_object: ValueObject):
        """
        finish routing request and hand it over to output.
        currently, just print result value simply for debug.
        """

        print('Request done. Result value: ', value_object.value)

    def start(self):
        """
        start consuming request from implementable any sources.
        """

        print('Start consuming.')

        namespaces = list()
        namespaces_available = [m.NAMESPACE for m in ModuleManagerTest.MODULES]

        while True:
            try:
                text = input()

                if text == 'quit':
                    print('Process quit.')
                    break
                elif text in namespaces_available:
                    namespaces.append(text)
                    print('Current modules:', namespaces)
                elif text == 'go':
                    print('Job launched:', namespaces)
                    self.input.send(ValueObject(module_namespaces=namespaces.copy()))
                    namespaces = list()
                else:
                    print('Available namespaces:', namespaces_available)

            except KeyboardInterrupt as _:
                print('Process quit.')
                break


if __name__ == '__main__':
    manager = ModuleManagerTest()
    manager.start()

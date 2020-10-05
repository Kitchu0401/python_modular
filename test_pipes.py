from multiprocessing import Pipe, Process


class ValueObject:

    def __init__(self, value=0, module_namespaces=None):
        self.value = value
        self.module_namespaces = module_namespaces or list()


class ModuleTest:

    NAMESPACE = None

    def __init__(self):
        pass

    def _prepare(self):
        print(f'Module initialized: [{self.__class__.NAMESPACE}]')

    def prepare(self):
        self._prepare()

    def _process(self, value_object: ValueObject) -> ValueObject:
        raise NotImplementedError

    def process(self, value_object: ValueObject) -> ValueObject:
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


class ModuleManagerTest:

    MODULES = {
        ModuleTestAdd,
        ModuleTestDivide,
        ModuleTestMultiply,
        ModuleTestSubtract
    }

    def __init__(self):
        # initialize Pipe for finish
        self.process_input, self.process_output = Pipe()

        self.module_input = dict()
        self.module_output = dict()
        self.modules = list()

        # initialize individual modules as multiprocessing.Process
        # prepare input / output pipes before calling start()
        for module in ModuleManagerTest.MODULES:
            pipe_in, pipe_out = Pipe()
            self.module_input[module.NAMESPACE] = pipe_in
            self.module_output[module.NAMESPACE] = pipe_out

        # as arguments for Process seems to be copied at the moment of calling start(),
        # delay calling start() after all process input / output pipes initialized.
        for module in ModuleManagerTest.MODULES:
            module = module()
            module.prepare()

            process_params = (module, self.module_output, self.module_input)
            process = Process(target=self._handle_process, args=process_params)
            process.start()

    def _handle_process(self, module: ModuleTest, pipes_out: dict, pipes_in: dict):
        """
        process and route request.
        """

        namespace = module.NAMESPACE

        # TODO should we name process?

        while True:
            value_object: ValueObject = pipes_out[namespace].recv()
            value_object = module.process(value_object=value_object)

            # if there're remaining namespaces, route it.
            if value_object.module_namespaces:
                namespace_next = value_object.module_namespaces.pop(0)
                print('Sending to:', namespace_next)
                pipes_in[namespace_next].send(value_object)
            # else if there's no remaining namespace, send it to Provider
            else:
                print('Ending process.')
                self.process_input.send(value_object)

    def _consume(self) -> ValueObject:
        """
        receive request, prepare as ValueObject and feed into module chain.
        """

        raise NotImplementedError

    def _finish(self, value_object: ValueObject):
        """
        finish processed request, sending it out.
        """

        raise NotImplementedError

    def start(self):
        """
        start consuming and processing requests.
        """

        print('Start consuming.')

        try:
            while True:
                # initialize request and feed into module chain
                value_object: ValueObject = self._consume()
                namespace_next = value_object.module_namespaces.pop(0)
                print('Sending to:', namespace_next)
                self.module_input[namespace_next].send(value_object)

                # wait and receive processed result and send it out.
                value_object: ValueObject = self.process_output.recv()
                self._finish(value_object=value_object)

        except KeyboardInterrupt:
            print('Process stopped.')


class ModuleManagerSimpleTest(ModuleManagerTest):

    def _consume(self) -> ValueObject:
        namespaces = list()
        namespaces_available = [m.NAMESPACE for m in ModuleManagerTest.MODULES]

        while True:
            # receive keyboard input
            text = input()

            # 'quit': exit process
            if text == 'quit':
                print('Process quit.')
                raise KeyboardInterrupt

            # 'go': send request with selected module namespaces
            elif text == 'go':
                if not namespaces:
                    print('Job have no process.')
                    continue

                print('Job launched:', namespaces)
                return ValueObject(value=0, module_namespaces=namespaces.copy())

            # available namespace: add to module namespaces
            elif text in namespaces_available:
                namespaces.append(text)
                print('Current modules:', namespaces)

            else:
                print('Available namespaces:', namespaces_available)

    def _finish(self, value_object: ValueObject):
        print('Job finished:', value_object.value)


if __name__ == '__main__':
    manager = ModuleManagerSimpleTest()
    manager.start()

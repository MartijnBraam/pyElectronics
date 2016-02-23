class PinReference(object):
    def __init__(self, chip_instance, method, arguments=None):
        self.chip = chip_instance
        self.method = method
        self.arguments = arguments or {}


class DigitalInputPin(PinReference):
    def read(self):
        m = getattr(self.chip, self.method)
        return m(**self.arguments)


class DigitalOutputPin(PinReference):
    def write(self, value):
        m = getattr(self.chip, self.method)
        m(value, **self.arguments)


class GPIOPin(PinReference):
    MODE_INPUT = 0
    MODE_OUTPUT = 1

    def __init__(self, chip_instance, method, arguments=None):
        self.mode = self.MODE_INPUT
        super().__init__(chip_instance, method, arguments)

    def set_mode(self, mode):
        self.mode = mode

    def read(self):
        return False

    def write(self, value):
        pass


class AnalogOutputPin(PinReference):
    def __init__(self, chip_instance, method, arguments=None):
        self.max = 1024
        super().__init__(chip_instance, method, arguments)

    def write(self, value):
        pass


class AnalogInputPin(PinReference):
    def __init__(self, chip_instance, method, arguments=None):
        super().__init__(chip_instance, method, arguments)

    def read(self):
        pass

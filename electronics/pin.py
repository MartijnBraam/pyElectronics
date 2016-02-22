class PinReference(object):
    pass


class DigitalInputPin(PinReference):
    def read(self):
        pass


class DigitalOutputPin(PinReference):
    def write(self, value):
        pass


class GPIOPin(PinReference):
    MODE_INPUT = 0
    MODE_OUTPUT = 1

    def __init__(self):
        self.mode = self.MODE_INPUT

    def set_mode(self, mode):
        self.mode = mode

    def read(self):
        return False

    def write(self, value):
        pass


class AnalogOutputPin(PinReference):
    def __init__(self):
        self.max = 1024

    def write(self, value):
        pass


class AnalogInputPin(PinReference):
    def __init__(self):
        pass

    def read(self):
        pass

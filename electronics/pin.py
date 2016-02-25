class PinReference(object):
    """ This is a reference to a pin on a gateway or a chip somewhere behind a gateway.
    You should not use this class directly but use one of the subclasses
    """

    def __init__(self, chip_instance, method, arguments=None, inverted=False, name=""):
        self.chip = chip_instance
        self.method = method
        self.inverted = inverted
        self.name = name
        self.arguments = arguments or {}

    def __invert__(self):
        t = type(self)
        return t(self.chip, self.method, self.arguments, ~self.inverted)

    def __repr__(self):
        pin_type = type(self).__name__
        chip_name = type(self.chip).__name__
        if self.inverted:
            return '<{} {} on {} (inverted)>'.format(pin_type, self.name, chip_name)
        else:
            return '<{} {} on {}>'.format(pin_type, self.name, chip_name)


class DigitalInputPin(PinReference):
    """ This is a reference to a pin that only has input capabilities """

    def read(self):
        """ Get the logic input level for the pin

        :return: True if the input is high
        """
        m = getattr(self.chip, self.method)
        return m(**self.arguments)


class DigitalOutputPin(PinReference):
    """ This is a reference to a pin that only has output capabilities """

    def write(self, value):
        """ Set the logic output level for the pin.

        :type value: bool
        :param value: True for a logic high
        """
        m = getattr(self.chip, self.method)
        m(value, **self.arguments)


class GPIOPin(PinReference):
    """ This is a reference to a pin that can be used in input and output mode. This is most pins on microcontrollers
    """
    MODE_INPUT = 0
    MODE_OUTPUT = 1

    def __init__(self, chip_instance, method, arguments=None, inverted=False, name=""):
        self.mode = self.MODE_INPUT
        super().__init__(chip_instance, method, arguments, inverted, name)

    def set_mode(self, mode):
        self.mode = mode

    def read(self):
        """ Get the logic input level for the pin

        :return: True if the input is high
        """
        m = getattr(self.chip, self.method)
        return m(value=None, **self.arguments)

    def write(self, value):
        """ Set the logic output level for the pin.

        :type value: bool
        :param value: True for a logic high
        """
        if self.inverted:
            value = not value
        m = getattr(self.chip, self.method)
        m(value=value, **self.arguments)


class AnalogOutputPin(PinReference):
    def __init__(self, chip_instance, method, arguments=None, name=""):
        self.max = 1024
        super().__init__(chip_instance, method, arguments, name=name)

    def write(self, value):
        pass


class AnalogInputPin(PinReference):
    def __init__(self, chip_instance, method, arguments=None, name=""):
        super().__init__(chip_instance, method, arguments, name=name)

    def read(self):
        pass

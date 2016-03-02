class GPIOBus(object):
    """ This is a helper class for when your pins don't line up with ports. """

    def __init__(self, pins):
        self.pins = pins
        self.width = len(pins)
        self.max = pow(2, len(pins)) - 1

    def write(self, value):
        if value > self.max:
            raise AttributeError('{} pins is not enough to represent {}'.format(len(self.pins), value))

        for i in range(0, len(self.pins)):
            self.pins[i].write(value & (1 << i) > 0)

    def read(self):
        result = 0
        for i in range(0, len(self.pins)):
            result <<= 1
            result |= self.pins[i].read()
        return result

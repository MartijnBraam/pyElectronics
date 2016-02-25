class MockGateway(object):
    """
    This is a gateway designed to be used for doctest. It uses a ...ahem... deterministic pre-seeded random number
    generator. This ensures that the values in the doctests are the same but random.
    """
    def __init__(self):
        self.counter = 0

    def i2c_write_register(self, address, register, bytes):
        pass

    def i2c_read(self, address, length):
        result = bytearray()
        for i in range(0, length):
            self.counter += 1
            if self.counter > 255:
                self.counter = 0
            result.append(self.counter)
        return result

    def i2c_read_register(self, address, register, length):
        return self.i2c_read(address, length)

    def i2c_write(self, address, bytes):
        pass
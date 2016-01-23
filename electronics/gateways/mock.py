import os


class MockGateway(object):
    def __init__(self):
        self.counter = 0

    def i2c_write_register(self, address, register, bytes):
        pass

    def i2c_read(self, address, register):
        self.counter += 1
        if self.counter > 255:
            self.counter = 0
        return self.counter

    def i2c_read_register(self, address, register, length):
        result = bytearray()
        for i in range(0, length):
            result.append(self.i2c_read(address, register))
        return result

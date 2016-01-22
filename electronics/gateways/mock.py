import os


class MockGateway(object):
    def i2c_write(self, address, bytes):
        pass

    def i2c_read(self, address, length):
        return os.urandom(length)

class I2CDevice(object):
    def __init__(self, bus, address):
        if not hasattr(bus, 'i2c_write_register') or not hasattr(bus, 'i2c_read_register'):
            raise Exception('Bus does not support i2c read and write')

        self.i2c_bus = bus
        self.address = address

    def i2c_read_register(self, register, length):
        return self.i2c_bus.i2c_read_register(self.address, register, length)

    def i2c_write_register(self, register, bytes):
        return self.i2c_bus.i2c_write_register(self.address, register, bytes)

class I2CDevice(object):
    def __init__(self, bus, address):
        if not hasattr(bus, 'i2c_write') or not hasattr(bus, 'i2c_read'):
            raise Exception('Bus does not support i2c read and write')

        self.i2c_bus = bus
        self.address = address

    def i2c_read(self, length):
        return self.i2c_bus.i2c_read(self.address, length)

    def i2c_write(self, bytes):
        return self.i2c_bus.i2c_write(self.address, bytes)

    def i2c_read_register(self, register, length):
        self.i2c_write(register)
        return self.i2c_read(length)

    def i2c_write_register(self, register, bytes):
        raw = bytearray()
        raw.append(register)
        if isinstance(bytes, int):
            raw.append(bytes)
        self.i2c_write(raw)

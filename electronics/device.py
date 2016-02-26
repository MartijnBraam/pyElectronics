import logging


class I2CDevice(object):
    def __init__(self, bus, address):
        if not hasattr(bus, 'i2c_write_register') or not hasattr(bus, 'i2c_read_register'):
            raise Exception('Bus does not support i2c read and write')

        self.i2c_bus = bus
        self.address = address

    def i2c_read(self, length):
        response = self.i2c_bus.i2c_read(self.address, length)
        logging.debug('{} -> PC: {}'.format(self.address, repr(response)))
        return response

    def i2c_write(self, bytes):
        logging.debug('PC -> {}: {}'.format(self.address, repr(bytes)))
        return self.i2c_bus.i2c_write(self.address, bytes)

    def i2c_read_register(self, register, length):
        logging.debug('0x{:02X} -> PC: reg 0x{:02X}:'.format(self.address, register))
        response = self.i2c_bus.i2c_read_register(self.address, register, length)
        logging.debug(repr(response))
        return response

    def i2c_write_register(self, register, bytes):
        logging.debug('PC -> 0x{:02X} reg 0x{:02X}: {}'.format(self.address, register, repr(bytes)))
        return self.i2c_bus.i2c_write_register(self.address, register, bytes)


class GPIODevice(object):
    pass

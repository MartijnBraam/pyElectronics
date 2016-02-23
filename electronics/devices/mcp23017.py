from electronics.device import I2CDevice
from electronics.pin import GPIOPin
import struct


class MCP23017I2C(I2CDevice):
    """
    Interface for the Microchip MCP23017/MCP23S17 16-Bit I/O Expander with Serial Interface

    :Usage:

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import MCP23017I2C
        gw = MockGateway()

    :Example:

    >>> expander = MCP23017I2C(gw)
    """

    DIRECTION_INPUT = True
    DIRECTION_OUTPUT = False
    POLARITY_NORMAL = False
    POLARITY_INVERTED = True

    def __init__(self, bus, address=0x20):
        super().__init__(bus, address)

        self.IODIRA = 0xff
        self.IODIRB = 0xff
        self.IPOLA = 0x00
        self.IPOLB = 0x00
        self.GPINTENA = 0x00
        self.GPINTENB = 0x00
        self.GPPUA = 0x00
        self.GPPUB = 0x00
        self.GPIOA = 0x00
        self.GPIOB = 0x00

        self._IODIRA = 0xff
        self._IODIRB = 0xff
        self._IPOLA = 0x00
        self._IPOLB = 0x00
        self._GPINTENA = 0x00
        self._GPINTENB = 0x00
        self._GPPUA = 0x00
        self._GPPUB = 0x00
        self._GPIOA = 0x00
        self._GPIOB = 0x00

        # Set basic device configuration
        self.i2c_write_register(0x0A, [0b00100000])
        self.i2c_write_register(0x0B, [0b00100000])

        # Set all ports to input on init
        self.i2c_write_register(0x00, [0xff])
        self.i2c_write_register(0x01, [0xff])

    def __setattr__(self, key, value):
        part = key.split('_')
        if len(part) > 1:
            if part[0] in ['direction', 'polarity', 'pullup', 'value']:
                port, pin = self.pin_to_port(part[1])
                portname = 'A'
                if port == 1:
                    portname = 'B'

                if part[0] == 'direction':
                    self._update_register('IODIR' + portname, pin, value)
                elif part[0] == 'polarity':
                    self._update_register('IPOL' + portname, pin, value)
                elif part[0] == 'pullup':
                    self._update_register('GPPU' + portname, pin, value)
                elif part[0] == 'value':
                    self._update_register('GPIO' + portname, pin, value)
            else:
                super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)

    def _update_register(self, register, bit, value):
        reg = getattr(self, register)
        if value:
            reg |= 1 << bit
        else:
            reg &= ~(1 << bit)
        setattr(self, register, reg)

    def read(self, pin):
        port, pin = self.pin_to_port(pin)
        self.i2c_write([0x12 + port])
        raw = self.i2c_read(1)
        value = struct.unpack('>B', raw)[0]
        return (value & (1 << pin)) > 0

    def read_port(self, port):
        if port == 'A':
            raw = self.i2c_read_register(0x12, 1)
        elif port == 'B':
            raw = self.i2c_read_register(0x13, 1)
        return struct.unpack('>B', raw)[0]

    def write(self, pin, value):
        port, pin = self.pin_to_port(pin)
        portname = 'A'
        if port == 1:
            portname = 'B'
        self._update_register('GPIO' + portname, pin, value)
        self.sync()

    def sync(self):
        registers = {
            0x00: 'IODIRA',
            0x01: 'IODIRB',
            0x02: 'IPOLA',
            0x03: 'IPOLB',
            0x04: 'GPINTENA',
            0x05: 'GPINTENB',
            0x0C: 'GPPUA',
            0x0D: 'GPPUB',
            0x12: 'GPIOA',
            0x13: 'GPIOB'
        }
        for reg in registers:
            name = registers[reg]
            if getattr(self, name) != getattr(self, '_' + name):
                self.i2c_write_register(reg, [getattr(self, name)])
                setattr(self, '_' + name, getattr(self, name))

    def pin_to_port(self, pin):
        if len(pin) != 2:
            raise AttributeError('Invalid pin name: {}'.format(pin))

        if pin[0] == 'A':
            port = 0
        elif pin[0] == 'B':
            port = 1
        else:
            raise AttributeError('Invalid pin name: {}'.format(pin))

        pin = int(pin[1])
        return port, pin

    def _action(self, pin, value=None):
        if value is None:
            return self.read(pin)
        else:
            self.write(pin, value)

    def get_pins(self):
        result = []
        for a in range(0, 7):
            result.append(GPIOPin(self, '_action', {'pin': 'A{}'.format(a)}))
        for b in range(0, 7):
            result.append(GPIOPin(self, '_action', {'pin': 'B{}'.format(b)}))
        return result

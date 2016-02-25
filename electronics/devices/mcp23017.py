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
        import pprint
        gw = MockGateway()

    :Example:

    >>> expander = MCP23017I2C(gw)
    >>> # Set up a few ports
    >>> expander.direction_A6 = MCP23017I2C.DIRECTION_OUTPUT
    >>> expander.direction_A7 = MCP23017I2C.DIRECTION_OUTPUT
    >>> expander.direction_B0 = MCP23017I2C.DIRECTION_OUTPUT
    >>> # Send the new pin config to the expander chip
    >>> expander.sync()
    >>> # Set pin A7 high
    >>> expander.write('A7', True)

    Instead of manually setting pins to states on the expander you can also get a reference to the pins that you can
    pass to other devices. For example: driving a HD44780 lcd.

    :Example:

    >>> expander = MCP23017I2C(gw)
    >>> # Set all A pins to output mode
    >>> expander.IODIRA = 0xff
    >>> expander.sync()
    >>> # Get references for all pins
    >>> pins = expander.get_pins()
    >>> # Give them names, not required
    >>> datalines = pins[0:4]
    >>> rs = pins[5]
    >>> enable = pins[6]
    >>> rw = pins[7]
    >>> # Pass them to the hypothetical HD44780 module
    >>> lcd = HD44780(gw, datapins=datalines, enable=enable, rs=rs, rw=rw) # doctest: +SKIP
    >>> lcd.write("Hello pyElectronics") # doctest: +SKIP

    Most operations on this module modify the copy of the registers in the class instance. If you modify one of the
    register attributes or use the helper attributes (like direction_A0) then you need to call sync() to send the
    modified registers to the chip.

    Configuring pins with the helper attributes
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This class exposes 4 helper attributes for every pin. For pin A0 this is:

    * mcp23017.direction_A0
    * mcp23017.polarity_A0
    * mcp23017.pullup_A0
    * mcp23017.value_A0

    You can set the ``direction_x`` register to one of the ``mcp23017.DIRECTION_*`` constants to set the pin to input
    or output mode. The ``polarity_x`` registers inverses the polarity for the pin. The ``pullup_x`` attribute can be
    used to enable the internal pull-up resister for the pin on the chip. Use the ``value_x`` attribute to set the value
    for the pin.

    After you changed the state of the chip with these attributes you need to call the ``sync()`` method to actually
    modify the registers on the device
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
        """ Read the pin state of an input pin.
        Make sure you put the pin in input modus with the IODIR* register or direction_* attribute first.

        :Example:

        >>> expander = MCP23017I2C(gw)
        >>> # Read the logic level on pin B3
        >>> expander.read('B3')
        False
        >>> # Read the logic level on pin A1
        >>> expander.read('A1')
        True

        :param pin: The label for the pin to read. (Ex. A0)
        :return: Boolean representing the input level
        """
        port, pin = self.pin_to_port(pin)
        self.i2c_write([0x12 + port])
        raw = self.i2c_read(1)
        value = struct.unpack('>B', raw)[0]
        return (value & (1 << pin)) > 0

    def read_port(self, port):
        """ Read the pin state of a whole port (8 pins)

        :Example:

        >>> expander = MCP23017I2C(gw)
        >>> # Read pin A0-A7 as a int (A0 and A1 are high)
        >>> expander.read_port('A')
        3
        >>> # Read pin B0-B7 as a int (B2 is high)
        >>> expander.read_port('B')
        4

        :param port: use 'A' to read port A and 'B' for port b
        :return: An int where every bit represents the input level.
        """
        if port == 'A':
            raw = self.i2c_read_register(0x12, 1)
        elif port == 'B':
            raw = self.i2c_read_register(0x13, 1)
        return struct.unpack('>B', raw)[0]

    def write(self, pin, value):
        """ Set the pin state.
        Make sure you put the pin in output mode first.

        :param pin: The label for the pin to write to. (Ex. A0)
        :param value: Boolean representing the new state
        """
        port, pin = self.pin_to_port(pin)
        portname = 'A'
        if port == 1:
            portname = 'B'
        self._update_register('GPIO' + portname, pin, value)
        self.sync()

    def write_port(self, port, value):
        """ Use a whole port as a bus and write a byte to it.

        :param port: Name of the port ('A' or 'B')
        :param value: Value to write (0-255)
        """
        if port == 'A':
            self.GPIOA = value
        elif port == 'B':
            self.GPIOB = value
        else:
            raise AttributeError('Port {} does not exist, use A or B'.format(port))
        self.sync()

    def sync(self):
        """ Upload the changed registers to the chip

        This will check which register have been changed since the last sync and send them to the chip.
        You need to call this method if you modify one of the register attributes (mcp23017.IODIRA for example) or
        if you use one of the helper attributes (mcp23017.direction_A0 for example)
        """
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
        """ Get a list containing references to all 16 pins of the chip.

        :Example:

        >>> expander = MCP23017I2C(gw)
        >>> pins = expander.get_pins()
        >>> pprint.pprint(pins)
        [<GPIOPin A0 on MCP23017I2C>,
         <GPIOPin A1 on MCP23017I2C>,
         <GPIOPin A2 on MCP23017I2C>,
         <GPIOPin A3 on MCP23017I2C>,
         <GPIOPin A4 on MCP23017I2C>,
         <GPIOPin A5 on MCP23017I2C>,
         <GPIOPin A6 on MCP23017I2C>,
         <GPIOPin B0 on MCP23017I2C>,
         <GPIOPin B1 on MCP23017I2C>,
         <GPIOPin B2 on MCP23017I2C>,
         <GPIOPin B3 on MCP23017I2C>,
         <GPIOPin B4 on MCP23017I2C>,
         <GPIOPin B5 on MCP23017I2C>,
         <GPIOPin B6 on MCP23017I2C>]


        """
        result = []
        for a in range(0, 7):
            result.append(GPIOPin(self, '_action', {'pin': 'A{}'.format(a)}, name='A{}'.format(a)))
        for b in range(0, 7):
            result.append(GPIOPin(self, '_action', {'pin': 'B{}'.format(b)}, name='B{}'.format(b)))
        return result

    def get_pin(self, name):
        """ Get a reference to a named pin on the chip.

        :Example:

        >>> expander = MCP23017I2C(gw)
        >>> expander.get_pin('B3')
        <GPIOPin B3 on MCP23017I2C>

        :param name: Name of the pin (Ex: B3)
        :return: GPIOPin instance for the pin
        """
        return GPIOPin(self, '_action', {'pin': name}, name=name)

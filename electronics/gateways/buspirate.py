import serial
from electronics.pin import DigitalOutputPin


class BusPirate(object):
    """
    Class for using a Bus Pirate as I2C, GPIO or SPI or UART gateway. The code uses the Bus Pirate in bitbang mode
    (This doesn't mean the pins are bitbanged but that the communication is in binary mode instead of an ascii shell)
    For bitbang mode to work you need at least the v2.6 firmware. I'm testing this code on a Bus Pirate v3.5, other
    devices probably work.

    :example:
    >>> from electronics.gateways import BusPirate
    >>> # Open the Bus Pirate at the first USB-serial port
    >>> gw = BusPirate("/dev/ttyUSB0") # doctest: +SKIP
    >>> # It is also possible to specify the baudrate
    >>> other_pirate = BusPirate("/dev/ttyUSB1", baud=9600) # doctest: +SKIP

    The Bus Pirate supports multiple modes. This module will make sure the Bus Pirate is in the correct mode as soon
    as you use a read or write command. You can specify the peripheral configuration as attributes on the gateway
    instance. The configuration will be applied when switching the Bus Pirate mode. You can also switch the peripheral
    configuration at runtime with the set_peripheral command.

    :example:
    >>> from electronics.gateways import BusPirate
    >>> from electronics.devices import LM75
    >>> # Open the Bus Pirate
    >>> gw = BusPirate("/dev/ttyUSB0") # doctest: +SKIP
    >>> # Enable the power supply and the pull-ups in the next mode switch
    >>> gw.power = True # doctest: +SKIP
    >>> gw.pullup = True # doctest: +SKIP
    >>> gw.i2c_speed = '50kHz' # doctest: +SKIP
    >>> # Add a device so the config will apply
    >>> sensor = LM75(gw) # doctest: +SKIP
    >>> # The power and pullup is now enabled.
    >>> # Changing peripherals at runtime:
    >>> gw.set_peripheral(pullup=False, aux=True) # doctest: +SKIP
    >>> # The pullup is now  disabled and the aux pin set to VCC

    :param device: The path to the unix device created when plugging in the Bus Pirate.
    :param baud: The Bus Pirate baudrate. The default is 115200
    """

    MODE_RAW = 0
    MODE_SPI = 1
    MODE_I2C = 2
    MODE_UART = 3
    MODE_ONEWIRE = 4

    def __init__(self, device, baud=115200, debug=False):
        self.device = serial.Serial(device, baud)
        self.mode = self.MODE_RAW
        self.debug = debug

        self.pullup = False
        self.power = False
        self.aux = False
        self.chip_select = False
        self.i2c_speed = None  # default

        for i in range(0, 20):
            self.device.timeout = 0.1
            self.device.write(b"\x00")
            try:
                if self.device.read(5) == b"BBIO1":
                    break
            except TimeoutError:
                print("Timeout")
        else:
            raise Exception("Could not initialize BusPirate in binary mode")
        self.device.timeout = 1
        self.device.flushInput()
        self.device.flushOutput()
        
    def close(self):
        """disconnect from the hardware and make it available again."""
        self.device.close()
        
    def switch_mode(self, new_mode):
        """ Explicitly switch the Bus Pirate mode

        :param new_mode: The mode to switch to. Use the buspirate.MODE_* constants
        """
        packet = bytearray()
        packet.append(new_mode)
        self.device.write(packet)
        possible_responses = {
            self.MODE_I2C: b'I2C1',
            self.MODE_RAW: b'BBIO1',
            self.MODE_SPI: b'API1',
            self.MODE_UART: b'ART1',
            self.MODE_ONEWIRE: b'1W01'
        }
        expected = possible_responses[new_mode]
        response = self.device.read(4)
        if response != expected:
            raise Exception('Could not switch mode')
        self.mode = new_mode
        self.set_peripheral()
        if self.i2c_speed:
            self._set_i2c_speed(self.i2c_speed)

    def set_peripheral(self, power=None, pullup=None, aux=None, chip_select=None):
        """ Set the peripheral config at runtime.
        If a parameter is None then the config will not be changed.

        :param power: Set to True to enable the power supply or False to disable
        :param pullup: Set to True to enable the internal pull-up resistors. False to disable
        :param aux: Set the AUX pin output state
        :param chip_select: Set the CS pin output state
        """
        if power is not None:
            self.power = power
        if pullup is not None:
            self.pullup = pullup
        if aux is not None:
            self.aux = aux
        if chip_select is not None:
            self.chip_select = chip_select
        # Set peripheral status
        peripheral_byte = 64
        if self.chip_select:
            peripheral_byte |= 0x01
        if self.aux:
            peripheral_byte |= 0x02
        if self.pullup:
            peripheral_byte |= 0x04
        if self.power:
            peripheral_byte |= 0x08

        self.device.write(bytearray([peripheral_byte]))
        response = self.device.read(1)
        if response != b"\x01":
            raise Exception("Setting peripheral failed. Received: {}".format(repr(response)))

    def i2c_write_then_read(self, data, read_length):
        packet = bytearray()
        # Write then read mode
        packet.append(0x08)

        # Write data length
        packet.append(0x00)
        packet.append(len(data))

        # Read data length
        packet.append(0x00)
        packet.append(read_length)

        self.device.write(packet)

        if self.debug:
            status = self.device.read(1)
            if status == b'\x00':
                raise Exception('Read or write out of bounds')

        self.device.write(bytearray(data))
        response = self.device.read(read_length + 1)
        if response[0] == 0x00:
            raise Exception('No ack from device')

        if response[0] == 0x01:
            return response[1:]
        else:
            raise Exception('Unknown response: {}'.format(repr(response)))

    def i2c_read(self, address, length):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)
        read_address = (address << 1) | 0b00000001
        return self.i2c_write_then_read([read_address], length)

    def i2c_write(self, address, data):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)
        write_address = (address << 1)
        out = bytearray([write_address]) + bytearray(data)
        self.i2c_write_then_read(out, 0)

    def i2c_read_register(self, address, register, length):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)
        read_address = (address << 1) | 0b00000001
        return self.i2c_write_then_read([read_address, register], length)

    def i2c_write_register(self, address, register, data):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)
        write_address = address << 1
        payload = [write_address, register]
        payload.extend(data)
        self.i2c_write_then_read(payload, 0)

    def get_aux_pin(self):
        """ Get reference to the aux output on the Bus Pirate
        :return: DigitalOutputPin instance
        """
        return DigitalOutputPin(self, '_write_aux')

    def get_chip_select_pin(self):
        """ Get reference to the chip select output on the Bus Pirate
        :return: DigitalOutputPin instance
        """
        return DigitalOutputPin(self, '_write_cs')

    def _write_aux(self, value):
        self.set_peripheral(aux=value)

    def _write_cs(self, value):
        self.set_peripheral(chip_select=value)

    def _set_i2c_speed(self, i2c_speed):
        """ Set I2C speed to one of '400kHz', '100kHz', 50kHz', '5kHz'
        """
        lower_bits_mapping = {
            '400kHz': 3,
            '100kHz': 2,
            '50kHz': 1,
            '5kHz': 0,
        }
        if i2c_speed not in lower_bits_mapping:
            raise ValueError('Invalid i2c_speed')
        speed_byte = 0b01100000 | lower_bits_mapping[i2c_speed]
        self.device.write(bytearray([speed_byte]))
        response = self.device.read(1)
        if response != b"\x01":
            raise Exception("Changing I2C speed failed. Received: {}".format(repr(response)))

from electronics.device import I2CDevice
import struct


class BMP180(I2CDevice):
    """
    Interface for the Bosch BMP180 Digital pressure sensor

    :Usage:

    * Use load_calibration() to fetch the calibration data from the sensor
    * Use temperature() and pressure() to get the current pressure

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import BMP180
        gw = MockGateway()

    :Example:

    >>> sensor = BMP180(gw)
    >>> sensor.load_calibration()
    >>> sensor.temperature()
    12.5
    >>> sensor.pressure()
    360808

    """
    MODE_ULTRALOWPOWER = 0
    MODE_STANDARD = 1
    MODE_HIGHRESOLUTION = 2
    MODE_ULTRAHIGHRESOLUTION = 3

    BMP085_CONTROL = 0xF4
    BMP085_TEMPDATA = 0xF6
    BMP085_PRESSUREDATA = 0xF6
    BMP085_READTEMPCMD = 0x2E
    BMP085_READPRESSURECMD = 0x34

    def __init__(self, bus, address=0x77):
        # This is the calibration from the datasheet.
        self.cal = {
            'AC1': 480,
            'AC2': -72,
            'AC3': -14383,
            'AC4': 32741,
            'AC5': 32757,
            'AC6': 23153,
            'B1': 6190,
            'B2': 4,
            'MB': -32767,
            'MC': -8711,
            'MD': 2868
        }
        self.mode = self.MODE_STANDARD
        super().__init__(bus, address)

    def load_calibration(self):
        """Load factory calibration data from device."""
        registers = self.i2c_read_register(0xAA, 22)
        (
            self.cal['AC1'],
            self.cal['AC2'],
            self.cal['AC3'],
            self.cal['AC4'],
            self.cal['AC5'],
            self.cal['AC6'],
            self.cal['B1'],
            self.cal['B2'],
            self.cal['MB'],
            self.cal['MC'],
            self.cal['MD']
        ) = struct.unpack('>hhhHHHhhhhh', registers)

    def get_raw_temp(self):
        self.i2c_write_register(0xF4, 0x2E)
        raw = self.i2c_read_register(0xF6, 2)
        return struct.unpack('>h', raw)[0]

    def get_raw_pressure(self):
        self.i2c_write_register(0xF4, 0x34 + (self.mode << 6))
        raw = self.i2c_read_register(0xF6, 3)
        (msw, lsb) = struct.unpack('>HB', raw)
        return ((msw << 8) + lsb) >> (8 - self.mode)

    def temperature(self):
        """Get the temperature from the sensor.

        :returns: The temperature in degree celcius as a float

        :example:

        >>> sensor = BMP180(gw)
        >>> sensor.load_calibration()
        >>> sensor.temperature()
        21.4

        """
        ut = self.get_raw_temp()
        x1 = ((ut - self.cal['AC6']) * self.cal['AC5']) >> 15
        x2 = (self.cal['MC'] << 11) // (x1 + self.cal['MD'])
        b5 = x1 + x2
        return ((b5 + 8) >> 4) / 10

    def pressure(self):
        """
        Get barometric pressure in milibar

        :returns: The pressure in milibar as a int

        :example:

        >>> sensor = BMP180(gw)
        >>> sensor.load_calibration()
        >>> sensor.pressure()
        75216

        """
        ut = self.get_raw_temp()
        up = self.get_raw_pressure()
        x1 = ((ut - self.cal['AC6']) * self.cal['AC5']) >> 15
        x2 = (self.cal['MC'] << 11) // (x1 + self.cal['MD'])
        b5 = x1 + x2
        b6 = b5 - 4000
        x1 = (self.cal['B2'] * (b6 * b6) >> 12) >> 11
        x2 = (self.cal['AC2'] * b6) >> 11
        x3 = x1 + x2
        b3 = (((self.cal['AC1'] * 4 + x3) << self.mode) + 2) // 4
        x1 = (self.cal['AC3'] * b6) >> 13
        x2 = (self.cal['B1'] * ((b6 * b6) >> 12)) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self.cal['AC4'] * (x3 + 32768)) >> 15
        b7 = (up - b3) * (50000 >> self.mode)
        if b7 < 0x80000000:
            p = (b7 * 2) // b4
        else:
            p = (b7 // b4) * 2
        x1 = (p >> 8) * (p >> 8)
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16
        p += (x1 + x2 + 3791) >> 4
        return p

from electronics.device import I2CDevice
import struct


class HMC5883L(I2CDevice):
    """Interface for the Honeywell 3-Axis Digital Compass IC HMC5883L

    :Usage:

    * Use config() to specify the filtering and datarate
    * Use set_resolution() to configure the gain for the internal ADC
    * Use raw() and gauss() to get the sensor values

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import HMC5883L
        gw = MockGateway()

    :Example:

    >>> sensor = HMC5883L(gw)
    >>> sensor.config(averaging=4, datarate=15)
    >>> sensor.set_resolution(1090)
    >>> # Read a value
    >>> sensor.gauss()
    (2.3736, 7.1024, 11.831199999999999)
    """
    MODE_NORMAL = 0
    MODE_POSITIVE_BIAS = 1
    MODE_NEGATIVE_BIAS = 2

    def __init__(self, bus, address=0x1e):
        self.resolution = 1090
        super().__init__(bus, address)

    def config(self, averaging=1, datarate=15, mode=MODE_NORMAL):
        """
        Set the base config for sensor

        :param averaging: Sets the numer of samples that are internally averaged
        :param datarate: Datarate in hertz
        :param mode: one of the MODE_* constants
        """
        averaging_conf = {
            1: 0,
            2: 1,
            4: 2,
            8: 3
        }

        if averaging not in averaging_conf.keys():
            raise Exception('Averaging should be one of: 1,2,4,8')
        datarates = {
            0.75: 0,
            1.5: 1,
            3: 2,
            7.5: 4,
            15: 5,
            30: 6,
            75: 7
        }
        if datarate not in datarates.keys():
            raise Exception(
                    'Datarate of {} Hz is not support choose one of: {}'.format(datarate, ', '.join(datarates.keys())))

        config_a = 0
        config_a &= averaging_conf[averaging] << 5
        config_a &= datarates[datarate] << 2
        config_a &= mode

        self.i2c_write_register(0x00, config_a)

    def set_resolution(self, resolution=1090):
        """
        Set the resolution of the sensor

        The resolution value is the amount of steps recorded in a single Gauss. The possible options are:

        =======================  ==========  =============
        Recommended Gauss range  Resolution  Gauss per bit
        =======================  ==========  =============
        0.88 Ga                  1370        0.73 mGa
        1.3 Ga                   1090        0.92 mGa
        1.9 Ga                   820         1.22 mGa
        2.5 Ga                   660         1.52 mGa
        4.0 Ga                   440         2.27 mGa
        4.7 Ga                   390         2.56 mGa
        5.6 Ga                   330         3.03 mGa
        8.1 Ga                   230         4.35 mGa
        =======================  ==========  =============

        :param resolution: The resolution of the sensor
        """
        options = {
            1370: 0,
            1090: 1,
            820: 2,
            660: 3,
            440: 4,
            390: 5,
            330: 6,
            230: 7
        }

        if resolution not in options.keys():
            raise Exception('Resolution of {} steps is not supported'.format(resolution))

        self.resolution = resolution

        config_b = 0
        config_b &= options[resolution] << 5
        self.i2c_write_register(0x01, config_b)

    def raw(self):
        """
        Get the magnetometer values as raw data from the sensor as tuple (x,y,z)

        :example:

        >>> sensor = HMC5883L(gw)
        >>> sensor.raw()
        (3342, 3856, 4370)
        """
        result = self.i2c_read_register(0x03, 6)
        return struct.unpack('>HHH', result)

    def gauss(self):
        """
        Get the magnetometer values as gauss for each axis as a tuple (x,y,z)

        :example:

        >>> sensor = HMC5883L(gw)
        >>> sensor.gauss()
        (16.56, 21.2888, 26.017599999999998)
        """
        raw = self.raw()
        factors = {
            1370: 0.73,
            1090: 0.92,
            820: 1.22,
            660: 1.52,
            440: 2.27,
            390: 2.56,
            330: 3.03,
            230: 4.35
        }
        factor = factors[self.resolution] / 100
        return raw[0] * factor, raw[1] * factor, raw[2] * factor

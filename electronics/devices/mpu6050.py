from electronics.device import I2CDevice
import struct


class MPU6050I2C(I2CDevice):
    """
    Interface to a MPU-6050 Six-Axis (Gyro + Accelerometer) MEMS MotionTracking™ Device

    :Usage:

    * Use set_range() to specify the measurement range of to accel and gyro sensor
    * Use wakeup() to start the MEMS units in the sensor or use instance of this class as a new context
    * Use temperature(), acceleration() and angular_rate() to read the sensor values

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import MPU6050I2C
        gw = MockGateway()

    :Example:

    >>> sensor = MPU6050I2C(gw)
    >>> sensor.set_range(accel=MPU6050I2C.RANGE_ACCEL_2G, gyro=MPU6050I2C.RANGE_GYRO_250DEG)
    >>>
    >>> # Read a value
    >>> sensor.wakeup()
    >>> sensor.temperature()
    37.29
    >>> sensor.sleep()
    >>>
    >>> # Read a value using a context manager instead of wakeup() and sleep()
    >>> with sensor:
    ...     sensor.temperature()
    38.8

    """
    RANGE_ACCEL_2G = 0x00
    RANGE_ACCEL_4G = 0x08
    RANGE_ACCEL_8G = 0x10
    RANGE_ACCEL_16G = 0x18

    RANGE_GYRO_250DEG = 0x00
    RANGE_GYRO_500DEG = 0x08
    RANGE_GYRO_1000DEG = 0x10
    RANGE_GYRO_2000DEG = 0x18

    def __init__(self, bus, address=0x68):
        self.accel_range = None
        self.gyro_range = None
        self.awake = False
        super().__init__(bus, address)
        self.set_range(self.RANGE_ACCEL_16G, self.RANGE_GYRO_2000DEG)

    def set_range(self, accel=1, gyro=1):
        """Set the measurement range for the accel and gyro MEMS. Higher range means less resolution.

        :param accel: a RANGE_ACCEL_* constant
        :param gyro: a RANGE_GYRO_* constant

        :Example:

        .. code-block:: python

            sensor = MPU6050I2C(gateway_class_instance)
            sensor.set_range(
                accel=MPU6050I2C.RANGE_ACCEL_2G,
                gyro=MPU6050I2C.RANGE_GYRO_250DEG
                )

        """
        self.i2c_write_register(0x1c, accel)
        self.i2c_write_register(0x1b, gyro)
        self.accel_range = accel
        self.gyro_range = gyro

    def set_slave_bus_bypass(self, enable):
        """Put the aux i2c bus on the MPU-6050 in bypass mode, thus connecting it to the main i2c bus directly

        Dont forget to use wakeup() or else the slave bus is unavailable
        :param enable:
        :return:
        """
        current = self.i2c_read_register(0x37, 1)[0]
        if enable:
            current |= 0b00000010
        else:
            current &= 0b11111101
        self.i2c_write_register(0x37, current)

    def wakeup(self):
        """Wake the sensor from sleep."""
        self.i2c_write_register(0x6b, 0x00)
        self.awake = True

    def sleep(self):
        """Put the sensor back to sleep."""
        self.i2c_write_register(0x6b, 0x01)
        self.awake = False

    def temperature(self):
        """Read the value for the internal temperature sensor.

        :returns: Temperature in degree celcius as float

        :Example:

        >>> sensor = MPU6050I2C(gw)
        >>> sensor.wakeup()
        >>> sensor.temperature()
        49.38
        """
        if not self.awake:
            raise Exception("MPU6050 is in sleep mode, use wakeup()")

        raw = self.i2c_read_register(0x41, 2)
        raw = struct.unpack('>h', raw)[0]
        return round((raw / 340) + 36.53, 2)

    def acceleration(self):
        """Return the acceleration in G's

        :returns: Acceleration for every axis as a tuple

        :Example:

        >>> sensor = MPU6050I2C(gw)
        >>> sensor.wakeup()
        >>> sensor.acceleration()
        (0.6279296875, 0.87890625, 1.1298828125)
        """
        if not self.awake:
            raise Exception("MPU6050 is in sleep mode, use wakeup()")

        raw = self.i2c_read_register(0x3B, 6)
        x, y, z = struct.unpack('>HHH', raw)
        scales = {
            self.RANGE_ACCEL_2G: 16384,
            self.RANGE_ACCEL_4G: 8192,
            self.RANGE_ACCEL_8G: 4096,
            self.RANGE_ACCEL_16G: 2048
        }
        scale = scales[self.accel_range]
        return x / scale, y / scale, z / scale

    def angular_rate(self):
        """Return the angular rate for every axis in degree/second.

        :returns: Angular rate for every axis as a tuple

        :Example:

        >>> sensor = MPU6050I2C(gw)
        >>> sensor.wakeup()
        >>> sensor.angular_rate()
        (1.380859375, 1.6318359375, 1.8828125)
        """
        if not self.awake:
            raise Exception("MPU6050 is in sleep mode, use wakeup()")

        raw = self.i2c_read_register(0x43, 6)
        x, y, z = struct.unpack('>HHH', raw)
        scales = {
            self.RANGE_GYRO_250DEG: 16384,
            self.RANGE_GYRO_500DEG: 8192,
            self.RANGE_GYRO_1000DEG: 4096,
            self.RANGE_GYRO_2000DEG: 2048
        }
        scale = scales[self.gyro_range]
        return x / scale, y / scale, z / scale

    def __enter__(self):
        self.wakeup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sleep()

from electronics.device import I2CDevice
import struct


class MPU6050I2C(I2CDevice):
    """
    Interface to a MPU-6050 Six-Axis (Gyro + Accelerometer) MEMS MotionTracking™ Device

    Usage:
        Use set_range() to specify the measurement range of to accel and gyro sensor
        Use wakeup() to start the MEMS units in the sensor or use instance of this class as a new context
        Use temperature(), acceleration() and angular_rate() to read the sensor values

    Example:
        sensor = MPU6050I2C(gateway_class_instance)
        sensor.set_range(accel=MPU6050I2C.RANGE_ACCEL_2G, gyro=MPU6050I2C.RANGE_GYRO_250DEG)

        # Read a value
        sensor.wakeup()
        temperature = sensor.temperature()
        sensor.sleep()

        # Read a value using a context manager instead of wakeup() and sleep()
        with sensor:
            temperature = sensor.temperature()

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

    def set_range(self, accel=1, gyro=1):
        """Set the measurement range for the accel and gyro MEMS. Higher range means less resolution.
        :param accel: a RANGE_ACCEL_* constant
        :param gyro: a RANGE_GYRO_* constant
        """
        self.i2c_write_register(0x1c, accel)
        self.i2c_write_register(0x1b, gyro)
        self.accel_range = accel
        self.gyro_range = gyro

    def wakeup(self):
        """Wake the sensor from sleep."""
        self.i2c_write_register(0x6b, 0x00)
        self.awake = True

    def sleep(self):
        """Put the sensor back to sleep."""
        self.i2c_write_register(0x6b, 0x01)
        self.awake = False

    def temperature(self):
        """Read the value for the internal temperature sensor."""
        if not self.awake:
            raise Exception("MPU6050 is in sleep mode, use wakeup()")

        raw = self.i2c_read_register(0x41, 2)
        raw = struct.unpack('>h', raw)[0]
        return round((raw / 340) + 36.53, 2)

    def acceleration(self):
        """Return the acceleration for every axis in g."""
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
        """Return the angular rate for every axis in degree/second."""
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

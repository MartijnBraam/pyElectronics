from electronics.device import I2CDevice
import struct


class MPU6050I2C(I2CDevice):
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
        self.i2c_write_register(0x1c, accel)
        self.i2c_write_register(0x1b, gyro)
        self.accel_range = accel
        self.gyro_range = gyro

    def wakeup(self):
        """
        Wake the sensor from sleep
        :return:
        """
        self.i2c_write_register(0x6b, 0x00)
        self.awake = True

    def sleep(self):
        """
        Put the sensor back to sleep
        :return:
        """
        self.i2c_write_register(0x6b, 0x01)
        self.awake = False

    def temperature(self):
        """
        Read the value for the internal temperature sensor
        :return:
        """
        if not self.awake:
            raise Exception("MPU6050 is in sleep mode, use wakeup()")

        raw = self.i2c_read_register(0x41, 2)
        raw = struct.unpack('>h', raw)[0]
        return round((raw / 340) + 36.53, 2)

    def acceleration(self):
        """
        Return the acceleration for every axis in g
        :return:
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
        """
        Return the angular rate for every axis in degree/second
        :return:
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

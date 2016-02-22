Intro
=====

This is a library for interfacing with various chips and sensors that can be connected to a computer. It abstracts away
the connection between the bus master and slave for the protocols so that, for example, a LM75 sensor can both be used when
connected to the internal smbus on the motherboard on your computer or when connected to a buspirate through usb.

the electronics.gateways module contains the definitions for the bus masters and electronics.devices contains the
definitions for the chips that can be connected to one of the bus masters.

Usage
-----

To use a sensor first create a instance of the gateway you wil be using. In this case the MockGateway for testing

    >>> from electronics.gateways import MockGateway
    >>> gw = MockGateway()

Then initialize the sensors that are connected to the bus

    >>> from electronics.devices import BMP180, MPU6050I2C
    >>> barometer = BMP180(gw)
    >>> sixaxis = MPU6050I2C(gw)
    >>>
    >>> # Do device specific initialisation
    >>> barometer.load_calibration()
    >>> sixaxis.set_range(accel=MPU6050I2C.RANGE_ACCEL_2G, gyro=MPU6050I2C.RANGE_GYRO_250DEG)
    >>> sixaxis.wakeup()

After all initialisation is done then your sensors can be used as any Python object

    >>> sixaxis.angular_rate()
    (0.36083984375, 0.3922119140625, 0.423583984375)
    >>> barometer.pressure()
    420597
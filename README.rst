pyElectronics
=============

This is a python library for using electronics (like i2c or spi devices) with a unified interface. It currently supports
connecting to stuff through the Raspberry Pi gpio with the i2c kernel driver and using the Bus Pirate.

Installation
------------

Install it from pypi::

    $ pip3 install pyelectronics

Usage
-----

Read the full docs at pythonhosted_.

.. _pythonhosted: https://pythonhosted.org/pyelectronics/index.html


First create a instance of a gateway::

    from electronics.gateways import BusPirate
    from electronics.gateways import LinuxDevice
    
    # Use a BusPirate to connect to a bus
    gw = BusPirate('/dev/ttyUSB0')
    
    # Use a i2c bus with a linux driver (like the raspberry pi)
    gw = LinuxDevice(1) # /dev/i2c-1

Create instances for components connected to the gateway::

    from electronics.devices import BMP180
    from electronics.devices import MPU6050I2C
    
    barometer = BMP180(gw, address=0x77) # Address is optional
    inertia = MPU6050(gw)
    
    # Do chip specific initialisation
    barometer.load_calibration()
    inertia.wakeup()

Read values from sensors::

    temperature = barometer.temperature()
    pressure = barometer.pressure()
    acceleration = inertia.acceleration()
    rotation = inertia.angular_rate()

Supported chips/devices
-----------------------

* Bosch BMP180 Digital pressure sensor
* Honeywell 3-Axis Digital Compass IC HMC5883L
* MPU-6050 Six-Axis (Gyro + Accelerometer) MEMS MotionTracking™ Device
* NXP LM75A Digital temperature sensor
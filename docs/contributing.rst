Contributing
============

This library works fine now but it only supports a few chips. So here is a tutorial for adding support for a chip or
other electronic component.

Creating a module with a class
------------------------------

Every chips gets its own module. Create a new file under electronics/devices with the most generic name possible for the
chip. For example lm75.py for the NXP LM75A. If a chip supports multiple communication modes then create two classes in
the same file (for example the MPU-6050, although it only supports I2C now it has the I2C suffix).

The class for the device should subclass the communication bus. It should also at least implement the same arguments
for the ``__init__`` call::

    from electronics.device import I2CDevice

    class LM75(I2CDevice):
        def __init__(self, bus, address=0x49):
            super().__init__(bus, address)


The superclass contains the logic for communicating with the bus. To communicate with the outside world you need to call
the communication methods on the superclass. In the case of I2c you would use ``i2c_read_register`` and ``i2c_write_register``
and if some device is doing wierd stuff you can use ``i2c_read`` and ``i2c_write``

If something invokes an action on the communication bus it should be in a method, not in a attribute getter/setter. It
should be clear that calling it might be an expensive operation. If you need to set a lot of properties (like device
configuration) then you can put the settings in class attribute and use a method to sync those values with the device.

Writing tests
-------------

Writing tests for the hardware is challenging since they don't behave very predictable (They're sensors. you use them
because you don't know something). To add tests for the calculations you add an example in the inline documentation
that uses the MockGateway. The MockGateway will return the exact same values everytime ``make doctest`` is ran::

        .. testsetup::

            # This is hidden in the documentation but creates the variables we need
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


Registering the class in the library
------------------------------------

To add the device to the library properly:

* Create a device
* Write documentation in the class of the device. Examples are great, write examples.
* Add the class to ``electronics/devices/__init__.py``
* Create a file in ``docs/devices`` that renders the inline documentation for the class
* Add that file to ``docs/devices.rst``
* Create a pull request
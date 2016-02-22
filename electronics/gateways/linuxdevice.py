import smbus
import struct


class LinuxDevice(object):
    """
    Class for using a i2c master that is supported by a Linux kernel module. An example is the internal smbus in a
    computer motherboard (supported by i2c-dev) or the i2c connection on the Raspberry Pi (supported by i2c-bcm2708).
    Linux gives every i2c bus a number. For the Raspberry Pi 2 this is "1"

    :example:
    >>> from electronics.gateways.linuxdevice import LinuxDevice
    >>> # Open /dev/i2c-1
    >>> gw = LinuxDevice(1) # doctest: +SKIP

    :param i2c_bus_index: The number of the i2c bus.
    """

    def __init__(self, i2c_bus_index):
        self.i2c_index = i2c_bus_index
        self.bus = smbus.SMBus(i2c_bus_index)

    def i2c_write_register(self, address, register, data):
        if isinstance(data, int):
            data = [data]
        for b in data:
            self.bus.write_byte_data(address, register, b)

    def i2c_read_register(self, address, register, length):
        result = b""
        for r in range(register, register + length):
            value = self.bus.read_byte_data(address, r)
            # smbus module uses struct.unpack('@b') but almost nothing is a signed byte with native ordening...
            temp = struct.pack('@b', value)
            result += temp
        return result

    def i2c_read(self, address, length):
        raise NotImplementedError()

    def i2c_write(self, address, data):
        raise NotImplementedError()
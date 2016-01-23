import smbus
import struct


class LinuxDevice(object):
    def __init__(self, i2c_bus_index):
        self.i2c_index = i2c_bus_index
        self.bus = smbus.SMBus(i2c_bus_index)

    def i2c_write_register(self, address, register, bytes):
        if isinstance(bytes, int):
            bytes = [bytes]
        for b in bytes:
            self.bus.write_byte_data(address, register, b)

    def i2c_read_register(self, address, register, length):
        result = b""
        for r in range(register, register + length):
            value = self.bus.read_byte_data(address, r)
            # smbus module uses struct.unpack('@b') but almost nothing is a signed byte with native ordening...
            temp = struct.pack('@b', value)
            result += temp
        return result

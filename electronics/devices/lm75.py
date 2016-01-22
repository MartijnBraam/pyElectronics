from electronics.device import I2CDevice
import struct


class LM75(I2CDevice):
    def __init__(self, bus, address=0x48):
        super().__init__(bus, address)

    def temperature(self):
        result = self.i2c_read_register(0x00, 2)
        value = struct.unpack('>H', result)[0]

        if value < 32768:
            return value / 256.0
        else:
            return (value - 65536) / 256.0

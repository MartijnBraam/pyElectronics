from electronics.device import I2CDevice
import struct


class LM75(I2CDevice):
    """
    Interface to any LM75 compatible temperature sensor (Used NXP LM75A for testting)

    :Usage:

    * Use temperature() to get the temperature in degree celcius

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import LM75
        gw = MockGateway()

    :Example:

    >>> sensor = LM75(gw)
    >>> sensor.temperature()
    1.0078125
    """

    def __init__(self, bus, address=0x49):
        super().__init__(bus, address)

    def temperature(self):
        """ Get the temperature in degree celcius
        """
        result = self.i2c_read(2)
        value = struct.unpack('>H', result)[0]

        if value < 32768:
            return value / 256.0
        else:
            return (value - 65536) / 256.0

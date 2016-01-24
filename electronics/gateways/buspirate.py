import serial


class BusPirate(object):
    MODE_RAW = 0
    MODE_SPI = 1
    MODE_I2C = 2
    MODE_UART = 3
    MODE_ONEWIRE = 4

    def __init__(self, device, baud=115200):
        self.device = serial.Serial(device, baud)
        self.mode = self.MODE_RAW

        for i in range(0, 20):
            self.device.timeout = 0.1
            self.device.write(b"\x00")
            try:
                if self.device.read(5) == b"BBIO1":
                    break
            except TimeoutError:
                print("Timeout")
        else:
            raise Exception("Could not initialize BusPirate in binary mode")
        self.device.timeout = 1
        self.device.flushInput()
        self.device.flushOutput()

    def switch_mode(self, new_mode):
        packet = bytearray()
        packet.append(new_mode)
        self.device.write(packet)
        possible_responses = {
            self.MODE_I2C: b'I2C1',
            self.MODE_RAW: b'BBIO1',
            self.MODE_SPI: b'API1',
            self.MODE_UART: b'ART1',
            self.MODE_ONEWIRE: b'1W01'
        }
        expected = possible_responses[new_mode]
        response = self.device.read(4)
        if response != expected:
            raise Exception('Could not switch mode')
        self.mode = new_mode

    def i2c_read(self):
        pass

    def i2c_write(self, address, data):
        packet = bytearray()
        packet.append(0x02)
        packet.append(data)
        packet.append(0x03)
        self.device.write(packet)

    def i2c_read_register(self, address, register, length):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)

    def i2c_write_register(self, address, register, data):
        if self.mode != self.MODE_I2C:
            self.switch_mode(self.MODE_I2C)

from electronics.device import GPIODevice


class SevenSegmentGPIO(GPIODevice):
    """Class for driving a single character 7 segment display connected to GPIO pins

    @TODO: Add wireing instruction
    """

    font = {
        '0': 0b01110111,
        '1': 0b00100100,
        '2': 0b01011101,
        '3': 0b01101101,
        '4': 0b00101110,
        '5': 0b01101011,
        '6': 0b01111011,
        '7': 0b00100111,
        '8': 0b01111111,
        '9': 0b01101111
    }

    def __init__(self, segments):
        """
        :param segments: GPIOBus instance with the pins
        :return:
        """
        self.segments = segments

    def write(self, char):
        """ Display a single character on the display

        :type char: str
        :param char: Character to display
        """
        char = str(char)
        self.segments.write(self.font[char])

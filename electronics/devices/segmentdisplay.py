from electronics.device import GPIODevice
from electronics.gpio import GPIOBus


class SevenSegmentDisplayFont(object):
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
        '9': 0b01101111,
        'a': 0b00111111,
        'b': 0b01111010,
        'c': 0b01010011,
        'd': 0b01111100,
        'e': 0b01011011,
        'f': 0b00011011,
        'g': 0b01101111,
        'h': 0b00111110,
        'i': 0b00010010,
        'j': 0b01110100,
        'k': 0b00111110,
        'l': 0b01010010,
        'm': 0b00110001,
        'n': 0b00111000,
        'o': 0b01110111,
        'p': 0b00011111,
        'q': 0b00101111,
        'r': 0b00011000,
        's': 0b01101011,
        't': 0b01011010,
        'u': 0b01110110,
        'v': 0b01110000,
        'w': 0b01000110,
        'x': 0b00111110,
        'y': 0b00001110,
        'z': 0b01011101,
        ' ': 0b00000000,
        '_': 0b01000000
    }

    def __getitem__(self, item):
        return self.font[str(item).lower()]


class FourteenSegmentDisplayFont(object):
    font = {
        '0': 0b0000110000111111,
        '1': 0b0000000000000110,
        '2': 0b0000000011011011,
        '3': 0b0000000010001111,
        '4': 0b0000000011100110,
        '5': 0b0010000001101001,
        '6': 0b0000000011111101,
        '7': 0b0000000000000111,
        '8': 0b0000000011111111,
        '9': 0b0000000011101111,
        'A': 0b0000000011110111,
        'B': 0b0001001010001111,
        'C': 0b0000000000111001,
        'D': 0b0001001000001111,
        'E': 0b0000000011111001,
        'F': 0b0000000001110001,
        'G': 0b0000000010111101,
        'H': 0b0000000011110110,
        'I': 0b0001001000000000,
        'J': 0b0000000000011110,
        'K': 0b0010010001110000,
        'L': 0b0000000000111000,
        'M': 0b0000010100110110,
        'N': 0b0010000100110110,
        'O': 0b0000000000111111,
        'P': 0b0000000011110011,
        'Q': 0b0010000000111111,
        'R': 0b0010000011110011,
        'S': 0b0000000011101101,
        'T': 0b0001001000000001,
        'U': 0b0000000000111110,
        'V': 0b0000110000110000,
        'W': 0b0010100000110110,
        'X': 0b0010110100000000,
        'Y': 0b0001010100000000,
        'Z': 0b0000110000001001,
        'a': 0b0001000001011000,
        'b': 0b0010000001111000,
        'c': 0b0000000011011000,
        'd': 0b0000100010001110,
        'e': 0b0000100001011000,
        'f': 0b0000000001110001,
        'g': 0b0000010010001110,
        'h': 0b0001000001110000,
        'i': 0b0001000000000000,
        'j': 0b0000000000001110,
        'k': 0b0011011000000000,
        'l': 0b0000000000110000,
        'm': 0b0001000011010100,
        'n': 0b0001000001010000,
        'o': 0b0000000011011100,
        'p': 0b0000000101110000,
        'q': 0b0000010010000110,
        'r': 0b0000000001010000,
        's': 0b0010000010001000,
        't': 0b0000000001111000,
        'u': 0b0000000000011100,
        'v': 0b0010000000000100,
        'w': 0b0010100000010100,
        'x': 0b0010100011000000,
        'y': 0b0010000000001100,
        'z': 0b0000100001001000,
        ' ': 0b0000000000000000,
        '!': 0b0000000000000110,
        '"': 0b0000001000100000,
        '#': 0b0001001011001110,
        '$': 0b0001001011101101,
        '%': 0b0000110000100100,
        '&': 0b0010001101011101,
        "'": 0b0000010000000000,
        '(': 0b0010010000000000,
        ')': 0b0000100100000000,
        '*': 0b0011111111000000,
        '+': 0b0001001011000000,
        ',': 0b0000100000000000,
        '-': 0b0000000011000000,
        '.': 0b0000000000000000,
        '/': 0b0000110000000000,
        '{': 0b0000100101001001,
        '|': 0b0001001000000000,
        '}': 0b0010010010001001,
        '~': 0b0000010100100000,
        ':': 0b0001001000000000,
        ';': 0b0000101000000000,
        '<': 0b0010010000000000,
        '=': 0b0000000011001000,
        '>': 0b0000100100000000,
        '?': 0b0001000010000011,
        '@': 0b0000001010111011,
        '[': 0b0000000000111001,
        ']': 0b0000000000001111,
        '^': 0b0000110000000011,
        '_': 0b0000000000001000,
        '`': 0b0000000100000000
    }

    def __getitem__(self, item):
        return self.font[str(item)]


class SegmentDisplayGPIO(GPIODevice):
    """Class for driving a single character 7 or 14 segment display connected to GPIO pins

    This class only works with segment displays that are not multiplexed. Connect a gpio pin to every segment
    pin of the display and connect to common anode or cathode to vcc or gnd.

    Initialize this class with the pins in this order:

    1. top segment
    2. top left segment
    3. top right segment
    4. middle segment
    5. bottom left segment
    6. bottom right segment
    7. bottom segment

    .. testsetup::

        from electronics.gateways import MockGateway
        from electronics.devices import SevenSegmentGPIO
        from electronics.devices import MCP23017I2C
        gw = MockGateway()

    :Example:

    >>> # Connect to a MCP23017 port expander because we need 7 GPIOs
    >>> expander = MCP23017I2C(gw)
    >>> display_pins = expander.get_pins()[0:7]
    >>> # Create a SevenSegmentGPIO instance for the display
    >>> display = SegmentDisplayGPIO(display_pins)
    >>> # Display a number
    >>> display.write(6)
    >>> # Letters are also supported
    >>> display.write('h')

    """

    def __init__(self, segments):
        """
        :param segments: GPIOBus instance with the pins or array of pins
        """

        if isinstance(segments, list):
            segments = GPIOBus(segments)
        if segments.width == 7:
            self.font = SevenSegmentDisplayFont()
        if segments.width == 14:
            self.font = FourteenSegmentDisplayFont()
        else:
            raise AttributeError('Incorrect number of pins supplied, use 7 or 14 pins')
        self.segments = segments

    def write(self, char):
        """ Display a single character on the display

        :type char: str or int
        :param char: Character to display
        """
        char = str(char).lower()
        self.segments.write(self.font[char])

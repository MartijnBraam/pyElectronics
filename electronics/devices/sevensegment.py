from electronics.device import GPIODevice
from electronics.gpio import GPIOBus


class SevenSegmentGPIO(GPIODevice):
    """Class for driving a single character 7 segment display connected to GPIO pins

    This class only works with 8-pin 7 segment displays (not multiplexed in any way). Connect a gpio pin to every segment
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
    >>> display = SevenSegmentGPIO(display_pins)
    >>> # Display a number
    >>> display.write(6)
    >>> # Letters are also supported
    >>> display.write('h')

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
        ' ': 0b00000000
    }

    def __init__(self, segments):
        """
        :param segments: GPIOBus instance with the pins or array of pins
        """

        if isinstance(segments, list):
            segments = GPIOBus(segments)
        self.segments = segments

    def write(self, char):
        """ Display a single character on the display

        :type char: str or int
        :param char: Character to display
        """
        char = str(char).lower()
        self.segments.write(self.font[char])

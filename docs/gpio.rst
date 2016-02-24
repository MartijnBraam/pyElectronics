GPIO, ADC and DAC
=================

Communicating with busses is easy, just hook everything up, add pull-ups and pull-downs everywhere and stuff starts
working. But a lot of devices don't connect to an I2C or SPI bus but need some GPIO bitbanging. Also a lot of interesting
things can be done with analog pins.

The problem is that these pins can be anywhere and be used by anything. So pyElectronics provide a common interface for
all digital and analog pins. These can be provided by the gateways themselves (The Raspberry Pi has a lot of GPIO) or
by devices connected to a bus like I2C port extenders and ADC/DAC chips.

The provider for the pin provides an instance of one of these classes:

* DigitalInputPin: Can only read a boolean
* DigitalOutputPin: Can only write a boolean
* GPIOPin: Can switch between input and output mode
* AnalogInputPin: Can read a float between 0 and 1
* AnalogOutputPin: Can write a float betwoon 0 and 1

Example
-------

The Bus Pirate has an aux pin that can be used as an digital output::

    gw = BusPirate("/dev/ttyUSB0")

    # Get a reference to the aux pin.
    # This is an instance of DigitalOutputPin
    aux = gw.get_aux_pin()

    # Set the output of the pin
    aux.write(True)

Using a pin on a port expander::

    gw = BusPirate("/dev/ttyUSB0")

    # Initialize a i2c port expander
    expander = MCP23017I2C(gw)

    # Get a reference to pin 4 on port B
    my_own_led_pin = expander.get_pin('B4')

    # Obligatory blink-a-led example
    for i in range(0, 20):
        my_own_led_pin.write(True)
        sleep(0.5)
        my_own_led_pin.write(False)
        sleep(0.5)

    display_pins = expander.get_pins()[2:8]

    # This also doesn't exist yet.
    display = HD4470(display_pins)
    display.write_text("Hello World!")


GPIO Bus
--------

Sometimes (most of the times) you need to connect a data bus to gpio ports but they don't line op nice with a whole port.
In that case you can use GPIOBus to put a bunch of GPIO pins together to create a virtual port. You can create a bus of
any width this way::

    gw = BusPirate("/dev/ttyUSB0")
    expander = MCP23017I2C(gw)

    pins = expander.get_pins()

    # Use pin 5,6,7 and 2 from the port expander
    buspins = pins[5:8]
    buspins.append(pins[2])

    # Create a bus
    bus = GPIOBus(buspins)

    # Write data to the bus
    bus.write(13)

The pins in the bus don't have any relation to eachother, they don't even have to be on the same chip::

    gw = BusPirate("/dev/ttyUSB0")
    expander = MCP23017I2C(gw)

    # Get references for all the pins on the expander
    pins = expander.get_pins()

    # Get reference to the aux pin on the Bus Pirate
    aux = gw.get_aux_pin()

    # Use pin 5,6 and from the port expander
    buspins = pins[5:8]

    # Add the aux pin from the Bus Pirate
    buspins.append(aux)

    # Create a bus
    bus = GPIOBus(buspins)

    # Write data to the bus the same way as the previous example
    bus.write(13)

The problem is if your pins are open-drain, you get an even bigger problem if a subset of your pins is open-drain. You
can individually invert pins in the bus on definition. This is not handled by the GPIOBus class but by the GPIOPins
themselves::

    # Get references for a bunch of leds
    red = expander.get_pin('A0')
    green = expander.get_pin('A1')
    blue = gw.get_aux_pin()

    # Define a bus with the expander pins inverted
    colorbus = GPIOBus([~red, ~green, blue])

    # Disco!
    for i in range(0,8):
        colorbus.write(i)
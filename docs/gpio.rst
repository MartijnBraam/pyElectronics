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

This hasn't been implemented yet but the example for an I2C port expander::

    gw = BusPirate("/dev/ttyUSB0")

    # This class doesn't exist yet
    expander = MCP23017(gw)

    # Get a reference to pin 4
    my_own_led_pin = expander.get_pin(4)

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


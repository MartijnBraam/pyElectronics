## Usage

The full documentation is at: http://pyelectronics.brixit.nl/docs/

First create a instance of a gateway

```python
from electronics.gateways import BusPirate
from electronics.gateways import LinuxDevice

# Use a BusPirate to connect to a bus
gw = BusPirate('/dev/ttyUSB0')

# Use a i2c bus with a linux driver (like the raspberry pi)
gw = LinuxDevice(1) # /dev/i2c-1
```

Create instances for components connected to the gateway

```python
from electronics.devices import BMP180
from electronics.devices import MPU6050I2C

barometer = BMP180(gw, address=0x77) # Address is optional
inertia = MPU6050(gw)

# Do chip specific initialisation
barometer.load_calibration()
inertia.wakeup()
```

Read values from sensors

```python
temperature = barometer.temperature()
pressure = barometer.pressure()
acceleration = inertia.acceleration()
rotation = inertia.angular_rate()
```
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, sh1107, ws0010

import time

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)

def teletype(string, delay):
    current_output = ""
    for char in string:
        current_output += char
        with canvas(device) as draw:
            draw.text((0, 32), current_output, fill = "white")
            time.sleep(delay)
    time.sleep(100*delay)
    
teletype("dih and balls type shi", 0.005)

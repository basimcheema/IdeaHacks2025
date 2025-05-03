""" Run these before
sudo apt update
sudo apt full-upgrade
sudo apt install python3-picamera2

Then,
sudo raspi-config

Navigate to "Interface Options -> Camera -> Enable"
Reboot
"""


from picamera2 import Picamera2
from time import sleep

# Initialize the camera
picam2 = Picamera2()

# Configure for still image capture
config = picam2.create_still_configuration()
picam2.configure(config)

# Start the camera
picam2.start()
sleep(2)  # Warm-up time for auto-exposure

# Capture and save as JPEG
picam2.capture_file("image.jpg")
print("Saved image as image.jpg")

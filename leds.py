from rpi_ws281x import *
import time
from multiprocessing import Process, Queue

LED_COUNT = 24
LED_PIN = 18

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

class LEDController:
    def __init__(self):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, 800000, 10, False, 65, 0)
        self.strip.begin()
        self.queue = Queue()  # For receiving commands

    def think(self, cycles=3, speed=0.1):
        """Pulsing blue animation for thinking state"""
        for _ in range(cycles):
            # Fade in
            for i in range(0, 100, 5):
                color = Color(0, 0, int(i * 2.55))
                for led in range(self.strip.numPixels()):
                    self.strip.setPixelColor(led, color)
                self.strip.show()
                time.sleep(speed)
            
            # Fade out
            for i in range(100, 0, -5):
                color = Color(0, 0, int(i * 2.55))
                for led in range(self.strip.numPixels()):
                    self.strip.setPixelColor(led, color)
                self.strip.show()
                time.sleep(speed)

    def answer(self, color=Color(0, 255, 0), duration=2):
        """Green spiral animation for answering state"""
        start_time = time.time()
        while time.time() - start_time < duration:
            for i in range(self.strip.numPixels()):
                # Set current pixel and the one opposite to it
                self.strip.setPixelColor(i, color)
                opposite = (i + LED_COUNT//2) % LED_COUNT
                self.strip.setPixelColor(opposite, color)
                self.strip.show()
                time.sleep(0.05)
                # Turn off previous pixels
                self.strip.setPixelColor(i, Color(0,0,0))
                self.strip.setPixelColor(opposite, Color(0,0,0))
        
        # Final confirmation flash
        for _ in range(3):
            colorWipe(self.strip, color, 10)
            colorWipe(self.strip, Color(0,0,0), 10)

    def run(self):
        while True:
            if not self.queue.empty():
                command = self.queue.get()
                if command == "think":
                    self.think()
                elif command == "answer":
                    self.answer()
                elif command == "clear":
                    colorWipe(self.strip, Color(0, 0, 0))
            time.sleep(0.1)  # Prevents CPU overload

if __name__ == "__main__":
    # Create and start controller
    controller = LEDController()
    controller_process = Process(target=controller.run)
    controller_process.start()

    # Example commands
    try:
        controller.queue.put("think")    # Start thinking animation
        time.sleep(2)
        controller.queue.put("answer")   # Switch to answer animation
        time.sleep(2)
        controller.queue.put("clear")    # Turn off LEDs
        
        # Keep process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.queue.put("clear")
        controller_process.terminate()


# example main.py

# from multiprocessing import Process, Queue
# import time

# def main():
#     # Start LED controller in a separate process
#     from led_controller import LEDController
#     controller_process = Process(target=LEDController().run)
#     controller_process.start()

#     # Example: Send commands to the LED controller
#     led_queue = LEDController().queue  # Shared queue
#     led_queue.put("think")    # Start thinking animation
#     time.sleep(2)
#     led_queue.put("answer")   # Switch to answer animation
#     time.sleep(2)
#     led_queue.put("clear")    # Turn off LEDs

# if __name__ == "__main__":
#     main()
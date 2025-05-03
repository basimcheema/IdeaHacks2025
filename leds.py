from rpi_ws281x import Adafruit_NeoPixel, Color
import time
from multiprocessing import Queue

# LED strip configuration
LED_COUNT = 24         # Number of LED pixels.
LED_PIN = 18           # GPIO pin connected to the pixels (must support PWM!).

class LEDController:
    def __init__(self, queue):
        self.queue = queue
        self.strip = Adafruit_NeoPixel(
            LED_COUNT, LED_PIN, 800000, 10, False, 65, 0
        )
        self.strip.begin()

    def colorWipe(self, color, wait_ms=50):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def clear(self):
        self.colorWipe(Color(0, 0, 0), 10)

    def think(self, cycles=3, speed=0.1):
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
        start_time = time.time()
        while time.time() - start_time < duration:
            for i in range(self.strip.numPixels()):
                opposite = (i + LED_COUNT // 2) % LED_COUNT
                self.strip.setPixelColor(i, color)
                self.strip.setPixelColor(opposite, color)
                self.strip.show()
                time.sleep(0.05)
                self.strip.setPixelColor(i, Color(0, 0, 0))
                self.strip.setPixelColor(opposite, Color(0, 0, 0))

        # Final confirmation flash
        for _ in range(3):
            self.colorWipe(color, 10)
            self.colorWipe(Color(0, 0, 0), 10)

    def run(self):
        while True:
            if not self.queue.empty():
                command = self.queue.get()
                if command == "think":
                    self.think()
                elif command == "answer":
                    self.answer()
                elif command == "clear":
                    self.clear()
            time.sleep(0.1)


# from multiprocessing import Process, Queue
# import time
# from leds import LEDController

# main function for testing, comment out later

from multiprocessing import Process

def main():
    queue = Queue()
    controller = LEDController(queue)
    controller_process = Process(target=controller.run)
    controller_process.start()

    try:
        # Send commands to the LED controller
        queue.put("think")
        time.sleep(2)
        queue.put("answer")
        time.sleep(2)
        queue.put("clear")

        # Keep main process alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        queue.put("clear")
        controller_process.terminate()

if __name__ == "__main__":
    main()

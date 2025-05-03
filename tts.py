from gtts import gTTS
import pygame
import os
import time

language = 'en'

pygame.mixer.init()

def say(text = "default response"):
    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("speech.mp3")

    try: 
        pygame.mixer.music.load("speech.mp3")
        pygame.mixer.Channel(0).play(pygame.mixer.Sound('speech.mp3'))
        while pygame.mixer.Channel(0).get_busy():
            time.sleep(.1)
    finally:
        pygame.mixer.music.stop()
        if os.path.exists():
            os.remove("speech.mp3")

# example code
# say("hello")

from gtts import gTTS
import pygame
import os
import time

language = 'en'

pygame.mixer.init()
pygame.mixer.set_num_channels(1)  

def say(text="default response"):
    try:
        # Stop any currently playing audio
        pygame.mixer.Channel(0).stop()
        
        # Clean up previous file if exists
        if os.path.exists("speech.mp3"):
            os.remove("speech.mp3")
            print("old file removed")
        
        # Generate new speech file
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("speech.mp3")
        
        # Load and play without delay
        sound = pygame.mixer.Sound("speech.mp3")
        pygame.mixer.Channel(0).play(sound)
        
    except Exception:
        print(Exception)

# if __name__ == "__main__":
#     say("This message will be interrupted this message will be")
#     print("Main thread continues immediately")
#     time.sleep(2)  
#     say("This is the interrupting message")  
#     time.sleep(2)

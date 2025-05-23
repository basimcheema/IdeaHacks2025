from gtts import gTTS
import pygame
from warnings import catch_warnings
from faster_whisper import WhisperModel
import os
from openai import OpenAI
import pvporcupine
import numpy as np
from pvrecorder import PvRecorder
import time
import wave
import struct
import base64
import requests
# from picamera2 import Picamera2

language = 'en'

pygame.mixer.init()
pygame.mixer.set_num_channels(1)  

promptAudio = [] # audio frames get appended here
AUDIO_OUTPUT_PATH = "recording.wav"
IMAGE_OUTPUT_PATH = "image.jpg"
SILENCE_THRESHOLD = 8000 # need to tweak
SILENCE_DURATION = 2.0 # 2s
silence_start = None
message_limit = 0
keywords = ["terminator"] # keywords array, update later

porcupine = pvporcupine.create(
        access_key="cjaWz5omdLyHn7Rw4jBQjBSQKLPIhnKuRlx9GwfLLJuWhdn9v3e6hw==",
        keywords=keywords
)

# print(PvRecorder.get_available_devices())

recorder = PvRecorder(device_index = 3, frame_length = porcupine.frame_length)
model = WhisperModel("base", device="cpu", compute_type="int8")  # Use "cuda" if GPU available
# -1 is default microphone

# code for feeding prompt to Gemini
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

messages = [
    {"role": "system", "content": "You are a very concise AI assistent named Terminator that limit his responses to 10-30 words. Prompts will always be accompanied by an image; please ignore the image if it doesn't seem to relate to the current prompt."}
]

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
'''# start camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
# sleep(2)  # Give it time to warm up'''

status = True

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
        
    except Exception as e:
        print(e)

try: 
    while True:
        print("\nSay the wake word...")
        recorder.start()
        promptAudio = []
        silence_start = None

        while True:

            keyword_index = porcupine.process(recorder.read())
            # -1 if no keyword heard, 0 otherwise

            if keyword_index >= 0:
                # hotword detected
                print("I'm listening...")
                os.system(f"rpicam-still -o ~{IMAGE_OUTPUT_PATH}")
                say("I am listening")
                break

                #begin recording prompt
        while True:
            currFrame = recorder.read()
            promptAudio.extend(currFrame)
            volume = np.linalg.norm(currFrame) # energy level
            #print(volume)
            
            if volume < SILENCE_THRESHOLD:
                if (silence_start is None):
                    silence_start = time.time()
                elif (time.time() - silence_start >= SILENCE_DURATION):
                    print("\nSilence Detected")
                    recorder.stop()

                    # rewrites given wav file
                    with wave.open(AUDIO_OUTPUT_PATH, 'w') as f:
                        f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
                        f.writeframes(struct.pack("h" * len(promptAudio), *promptAudio))
                    break
            else:
                silence_start = None


        # transcribe wav file into text
        segments, info = model.transcribe(AUDIO_OUTPUT_PATH, beam_size=5)
        promptString = "".join([seg.text for seg in segments])
        print(f"\nUser said: {promptString}")

        if (promptString == ""):
            continue
        if ( "terminate" in promptString.lower()):
            say("Terminating")
            time.sleep(2)
            status = False
            break


        message_limit += 1
        
        if message_limit > 2:
            try:
                messages.pop(1)
                messages.pop(1) 
            except Exception as e:
                print(e)


        
        # encode image
        base64_image = encode_image_to_base64(IMAGE_OUTPUT_PATH)
        data_url = f"data:image/jpeg;base64,{base64_image}"

        # Append user message to history
        messages.append({"role": "user", 
                    "content": [
                        {"type": "text", "text": promptString},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]})


        # Get assistant response
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages
        )


        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})


        print(f"\n Response:\n{response.choices[0].message.content}")
        print("\n--- Ready for the next prompt ---\n")

        
        if not status:
            raise KeyboardInterrupt

        say(response.choices[0].message.content)
except KeyboardInterrupt:
    print("Exiting gracefully.")
    recorder.delete()
    porcupine.delete()

import os
from openai import OpenAI
import pvporcupine
import numpy as np
from pvrecorder import PvRecorder
import time
import wave
import struct


promptAudio = [] # audio frames get appended here
AUDIO_OUTPUT_PATH = "recording.wav" # update
SILENCE_THRESHOLD = 8000 # need to tweak
SILENCE_DURATION = 2.0 # 2s
silence_start = None
keywords = ["americano"] # keywords array, update later

porcupine = pvporcupine.create(
        access_key="i9jM7i+d65cZ/X7fAv+E4lDvsi8RF2asrHqr1bEVIqV4HMZ4eUBCsA==",
        keywords=keywords
)

# print(PvRecorder.get_available_devices())

recorder = PvRecorder(device_index = 1, frame_length = porcupine.frame_length)
# -1 is default microphone

recorder.start()
while True:
    keyword_index = porcupine.process(recorder.read())
    # -1 if no keyword heard, 0 otherwise

    if keyword_index >= 0:
        # hotword detected
        print("I'm listening...")

        #begin recording prompt
        while True:
            currFrame = recorder.read()
            promptAudio.extend(currFrame)
            volume = np.linalg.norm(currFrame) # energy level
            # print(volume)
            
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
    if (len(promptAudio) != 0):
        break

# release jawns
recorder.delete()
porcupine.delete()



# code for feeding prompt to DeepSeek
'''while True:
    keyword_index = porcupine.process(recorder.read())
    if keyword_index >= 0:
        print(f"Detected {keywords[keyword_index]}")
        break'''


'''client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="deepseek/deepseek-chat:free",
    messages=[
        {"role": "system", "content": "You are a coding assistant that talks like a pirate."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ]
)

print(response.choices[0].message.content)'''


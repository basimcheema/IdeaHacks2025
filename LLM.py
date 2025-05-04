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


promptAudio = [] # audio frames get appended here
AUDIO_OUTPUT_PATH = "recording.wav" # update
SILENCE_THRESHOLD = 8000 # need to tweak
SILENCE_DURATION = 2.0 # 2s
silence_start = None
message_limit = 0
keywords = ["terminator"] # keywords array, update later

porcupine = pvporcupine.create(
        access_key="Iuo3C4EYlw48BoN9o7teihdZFtn3Bvc/JuF6NfUp7CnSOiqiel6CFg==",
        keywords=keywords
)

# print(PvRecorder.get_available_devices())

recorder = PvRecorder(device_index = 0, frame_length = porcupine.frame_length)
model = WhisperModel("base", device="cpu", compute_type="int8")  # Use "cuda" if GPU available
# -1 is default microphone

# code for feeding prompt to DeepSeek
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

messages = [
    {"role": "system", "content": "You are a very concise AI assistent named chat that limit his responses to 2 sentences"}
]


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

        # Respond using LLM
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "user", "content": promptString}
            ]
        )


        message_limit += 1
        
        if message_limit > 2:
            try:
                messages.pop(1)
                messages.pop(1) 
            except Exception as e:
                print(e)


        
        # Append user message to history
        messages.append({"role": "user", "content": promptString})


        # Get assistant response
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": "You are a very concise AI assistent named chat that limit his responses to 2 sentences"},
                {"role": "user", "content": promptString},
            ]
        )


        reply = response.choices[0].message.content
        messages.append({"role": "system", "content": reply})


        print(f"\n Response:\n{response.choices[0].message.content}")
        print("\n--- Ready for the next prompt ---\n")
except KeyboardInterrupt:
    print("Exiting gracefully.")
    recorder.delete()
    porcupine.delete()





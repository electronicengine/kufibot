import subprocess
import re
import json
import sounddevice as sd
from piper.voice import PiperVoice
import numpy as np


class SpeechProcessor:
    
    def __init__(self, model):
        self.model = model
        self.config = model + ".json"
        self.voice = PiperVoice.load(self.model, self.config)
        
        self.stream = sd.OutputStream(samplerate=self.voice.config.sample_rate, channels=1, dtype='int16')
        
        
    def start_stream(self):
        self.stream.start()

        
    def stop_stream(self):
        self.stream.stop()
        self.stream.close()

        
    def execute_curl(self, prompt):
        command = [
            "curl", "-X", "POST", "http://192.168.1.20:11434/api/generate",
            "-d", json.dumps({"model": "kufi", "prompt": prompt, "options":{"num_predict":120}})
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout

    def parse_and_concatenate(self, output):
        pattern = re.compile(r'"response":"(.*?)"')
        responses = pattern.findall(output)
        return ''.join(responses)

    def clean_text(self, text):
        pattern = r'\\n|\\t'
        return re.sub(pattern, ' ', text)

    def speak_text(self, text):
        
        for audio_bytes in self.voice.synthesize_stream_raw(text):
            int_data = np.frombuffer(audio_bytes, dtype=np.int16)
            self.stream.write(int_data)
                


    def translate(self, text, source_language, target_language):
        command = ['trans', '-b', f'{source_language}:{target_language}', text]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()

import pyaudio
import json
from vosk import Model, KaldiRecognizer

class SpeechRecognizer:
    def __init__(self, model_path, sample_rate=16000):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        self.stream = self._initialize_stream(sample_rate)

    def _initialize_stream(self, sample_rate):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=4096)
        stream.start_stream()
        return stream

    def recognize(self):
        data = self.stream.read(4096)
        
        if len(data) == 0:
            return None 
        
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            if(len(result['text']) >= 3):
                return result['text']
            else:
                return None
        else:
            None
            

    def start_listen(self) : 
        self.stream.start_stream()

    def stop_listen(self) :
        self.stream.stop_stream()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        pyaudio.PyAudio().terminate()

    def getComplatedMessage(self) :
        return json.loads(self.recognizer.Result())
    
    def getPartialMessage(self) :
        return json.loads(self.recognizer.PartialResult())

        
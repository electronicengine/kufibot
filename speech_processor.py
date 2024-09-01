import subprocess
import re
import json

class SpeechProcessor:
    
    def __init__(self, model):
        self.model = model
    
    def execute_curl(self, prompt):
        command = [
            "curl", "-X", "POST", "http://192.168.1.20:11434/api/generate",
            "-d", json.dumps({"model": "kufi", "prompt": prompt, "options":{"num_predict":50}})
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
                
        try:
            subprocess.run(['sounds/testSound.sh'], capture_output=True, text=True)
            echo_process = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
            piper_process = subprocess.Popen(
                ['../piper/piper', '--model', self.model, '--output-raw'],
                stdin=echo_process.stdout, stdout=subprocess.PIPE)
            echo_process.stdout.close()
            aplay_process = subprocess.Popen(
                ['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-'],
                stdin=piper_process.stdout)
            piper_process.stdout.close()
            aplay_process.wait()
        except Exception as e:
            print(f"Error during speech synthesis: {e}")

    def translate(self, text, source_language, target_language):
        command = ['trans', '-b', f'{source_language}:{target_language}', text]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()

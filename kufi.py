from speech_recognizer import SpeechRecognizer
from speech_processor import SpeechProcessor
import pyaudio
import json
from vosk import Model, KaldiRecognizer
from remote_controller import RemoteController
from motor_driver import MotorDriver
from servo_driver import ServoDriver
import tkinter as tk
from tkinter import ttk
import threading
from gesture_control import GestureControl
from object_tracking_color import ColorTracker
from compass_driver import CompassDriver
from distance_driver import DistanceDriver
from power_driver import PowerDriver


import cv2
import numpy as np
import time
import asyncio


    
    
# Function to check condition after a delay
def check_condition(processor, responded):
    if not responded:
        gesture.doit("thinking")
        processor.speak_text("Düşünüyorum...")  # Assuming 'speak_text' is a method in recognizer



# Function to run the while loop
def listen_loop(recognizer, processor, motor):
    
    responded = False


    try:
        while True:
            
            result_text = recognizer.recognize()
            if result_text != None:  # Completed Message
                print(f"Completed: {result_text}")
                recognizer.stop_listen()
                                
                if "çekiyorum" in result_text.lower():
                    gesture.doit("salute", 3)
                    processor.speak_text("herkese selam")
                    responded = True
                    recognizer.start_listen()
                    continue
                    
                if "leri git" in result_text.lower():
                    processor.speak_text("ileri komutu çalıştırılıyor")
                    print("komut: ileri")
                    responded = True
                    recognizer.start_listen()
                    continue
                    
                if "hareket" in result_text.lower():
                    processor.speak_text("Tabiki hareket edebilirim. Beni yapan Yusuf Bülbül saolsun")
                    print("hareket et")
                    motor.forward()
                    time.sleep(2)
                    motor.backward()
                    time.sleep(2)
                    motor.stop()

                    responded = True
                    recognizer.start_listen()
                    continue
                
                if "bu nedir" in result_text.lower():
                    processor.speak_text("o bir bluetut hopörlör.")
                    recognizer.start_listen()
                    responded = True
                    continue
                
                responded = False
                timer = threading.Timer(3, check_condition, args=(processor, responded))
                timer.start()               
                eng_text = processor.translate(result_text, "tr", "en")
                output = processor.execute_curl(eng_text)
                final_response = processor.parse_and_concatenate(output)
                cleaned_text = processor.clean_text(final_response)
                translated_response = processor.translate(cleaned_text, "en", "tr")
                responded = True
                print(translated_response)
                

                
                if "selam" in translated_response.lower() or "merhaba" in translated_response.lower() or "selamlar" in translated_response.lower():
                    gesture.doit("salute", 3)
                else : 
                    gesture.doit("talking")
    
                processor.speak_text(translated_response)
                
                recognizer.start_listen()
                gesture.stop()

            else:
                result = recognizer.getPartialMessage()

                if 'text' in result:
                    print(f"Partial: {result['text']}")
                else : 
                    pass
                
    except KeyboardInterrupt:
        print("Stopping the stream...")
    finally:
        recognizer.close()


if __name__ == "__main__":
    
    motor = MotorDriver()
    servo = ServoDriver ()
    gesture = GestureControl()
    tracker = ColorTracker()  
    compass = CompassDriver()
    distance = DistanceDriver()
    power = PowerDriver()
    
    com = False

    
    recognizer = SpeechRecognizer("ai.models/trRecognizeModel")
    processor = SpeechProcessor("ai.models/trSpeechModel/dfki.onnx")
    processor.start_stream()
    
    tracker = ColorTracker()
    remote_controller = RemoteController(motor, servo, compass, distance, power)

    listen_thread = threading.Thread(target=listen_loop, args=(recognizer,processor, motor,))
    listen_thread.start()
    
    # track_thread = threading.Thread(target=tracker.start)
    # track_thread.start()

    asyncio.run(remote_controller.main())

    # Optionally, you can wait for the thread to finish if needed
    listen_thread.join()
    
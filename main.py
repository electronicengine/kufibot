from speech_recognizer import SpeechRecognizer
from speech_processor import SpeechProcessor
import pyaudio
import json
from vosk import Model, KaldiRecognizer

from motor_driver import MotorDriver
from motor_controller import MotorController
from servo_driver import ServoDriver
import tkinter as tk
from tkinter import ttk
import threading
from gesture_control import GestureControl
from object_tracking_color import ColorTracker
import cv2
import numpy as np
import time

def update_servo_angle(event, channel, joint, label):
    angle = angle_sliders[channel].get()
    servo.set_absolute_servo_angle(joint, angle)
    label.config(text=f"{joint}: {angle}°")
    
    
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
                    print("recognized none")
                
    except KeyboardInterrupt:
        print("Stopping the stream...")
    finally:
        recognizer.close()

def setup_ui(root, motor, servo):
    # Frame for movement controls
    button_frame = tk.Frame(root)
    button_frame.pack(side="top", anchor="nw", pady=10)

    # Movement buttons
    btn_forward = tk.Button(button_frame, text="Forward", command=motor.forward)
    btn_forward.grid(row=0, column=1, padx=5, pady=5)

    btn_backward = tk.Button(button_frame, text="Backward", command=motor.backward)
    btn_backward.grid(row=2, column=1, padx=5, pady=5)

    btn_right = tk.Button(button_frame, text="Right", command=motor.turnRight)
    btn_right.grid(row=1, column=2, padx=5, pady=5)

    btn_left = tk.Button(button_frame, text="Left", command=motor.turnLeft)
    btn_left.grid(row=1, column=0, padx=5, pady=5)

    btn_stop = tk.Button(root, text="Stop", command=motor.stop)
    btn_stop.pack(side="top", pady=10)

    # Frame for head controls
    head_control_frame = tk.Frame(root)
    head_control_frame.pack(side="top", anchor="nw", pady=10)

    # Head control buttons
    head_up = tk.Button(head_control_frame, text="Head Up", command=servo.head_up)
    head_up.grid(row=0, column=1, padx=5, pady=5)

    head_down = tk.Button(head_control_frame, text="Head Down", command=servo.head_down)
    head_down.grid(row=2, column=1, padx=5, pady=5)

    head_right = tk.Button(head_control_frame, text="Head Right", command=servo.head_right)
    head_right.grid(row=1, column=2, padx=5, pady=5)

    head_left = tk.Button(head_control_frame, text="Head Left", command=servo.head_left)
    head_left.grid(row=1, column=0, padx=5, pady=5)



if __name__ == "__main__":
    
    motor = MotorDriver()
    servo = ServoDriver ()
    gesture = GestureControl()
    tracker = ColorTracker()  
    com = False

    # Initialize the main window
    root = tk.Tk()
    root.title("6-Servo Motor Control")

    angle_sliders = []
    angle_labels = []

    setup_ui(root, motor, servo)

    servo_angles = servo.get_all_joint_angles()
    servo_channels = servo.get_joint_channels()

    for joint, angle in servo_angles.items():
        
        label = ttk.Label(root, text=f"{joint}: {angle}°", font=("Helvetica", 12))
        label.pack(pady=5)
        angle_labels.append(label)
        
        slider = ttk.Scale(root, from_=0, to=180, orient="horizontal", length=400)
        slider.set(angle)  # Set the default angle
        slider.pack(pady=10)
        angle_sliders.append(slider)

        slider.bind("<Motion>", lambda event, channel=servo_channels[joint], joint=joint, label=label: update_servo_angle(event, channel, joint, label))

    
    recognizer = SpeechRecognizer("ai.models/trRecognizeModel")
    processor = SpeechProcessor("ai.models/trSpeechModel/dfki.onnx")
    tracker = ColorTracker()
    
    listen_thread = threading.Thread(target=listen_loop, args=(recognizer,processor, motor,))
    listen_thread.start()
    
    # track_thread = threading.Thread(target=tracker.start)
    # track_thread.start()

    
    # Start the GUI loop
    root.mainloop()

    # Optionally, you can wait for the thread to finish if needed
    listen_thread.join()
    
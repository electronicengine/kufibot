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



def update_servo_angle(event, channel, joint, label):
    angle = angle_sliders[channel].get()
    servo.set_servo_angle(joint, angle)
    label.config(text=f"{joint}: {angle}°")
    
    
# Function to check condition after a delay
def check_condition(processor, responsed):
    if not responsed:
        processor.speak_text("Düşünüyorum...")  # Assuming 'speak_text' is a method in recognizer



# Function to run the while loop
def listen_loop(recognizer, processor):
    
    responsed = False


    try:
        while True:
            
            result_text = recognizer.recognize()
            if result_text != None:  # Completed Message
                print(f"Completed: {result_text}")
                recognizer.stop_listen()
                responsed = False
                timer = threading.Timer(3, check_condition, args=(processor, responsed))
                timer.start()               
                eng_text = processor.translate(result_text, "tr", "en")
                output = processor.execute_curl(eng_text)
                final_response = processor.parse_and_concatenate(output)
                cleaned_text = processor.clean_text(final_response)
                translated_response = processor.translate(cleaned_text, "en", "tr")
                responsed = True
                processor.speak_text(translated_response)
                recognizer.start_listen()

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
   
    
if __name__ == "__main__":
    
    motor = MotorDriver()
    servo = ServoDriver ()

    com = False

    # Initialize the main window
    root = tk.Tk()
    root.title("6-Servo Motor Control")

    angle_sliders = []
    angle_labels = []

    # Add DC motor control buttons
    btn_forward = tk.Button(root, text="Forward", command=motor.forward)
    btn_forward.pack(pady=10)

    btn_backward = tk.Button(root, text="Backward", command=motor.backward)
    btn_backward.pack(pady=10)

    btn_right = tk.Button(root, text="Right", command=motor.turnRight)
    btn_right.pack(pady=10)

    btn_left = tk.Button(root, text="Left", command=motor.turnLeft)
    btn_left.pack(pady=10)

    btn_stop = tk.Button(root, text="stop", command=motor.stop)
    btn_stop.pack(pady=10)

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
    
    listen_thread = threading.Thread(target=listen_loop, args=(recognizer,processor,))
    listen_thread.start()

    # Start the GUI loop
    root.mainloop()

    # Optionally, you can wait for the thread to finish if needed
    listen_thread.join()
    
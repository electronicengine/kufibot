
import pyaudio
import json

from motor_driver import MotorDriver
from motor_driver import MotorDriver
from servo_driver import ServoDriver
import tkinter as tk
from tkinter import ttk
import threading

import random
import time

class GestureControl():
    def __init__(self):
        self.servo_driver = ServoDriver()
        self.stop_current_gesture = False
        self.running_gestures = []
        pass
        
    
    def stop(self):
        self.stop_current_gesture = True
        
    def default(self) :
        joint_angles = {"right_arm":15, "left_arm":170, "neck_down":20, "neck_up": 15, "neck_right":90, "eye_right": 0, "eye_left":0} #default
        self.servo_driver.set_all_angles(joint_angles)
        
    def salute(self, repeat):
        self.running_gestures.append("salute")

        for i in range(repeat):
            
            if self.stop_current_gesture :
                break
            
            print("salute")
            joint_angles = {"right_arm":15, "left_arm":150, "neck_down":78, "neck_up": 15, "neck_right":68, "eye_right": 0, "eye_left":0} 
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(0.5)
            joint_angles = {"right_arm":15, "left_arm":122, "neck_down":78, "neck_up": 15, "neck_right":68, "eye_right": 0, "eye_left":0} 
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(0.5)
            
        time.sleep(1)
        
        self.stop_current_gesture = False
        self.running_gestures.remove("salute")


        
    def talking(self) :
        self.running_gestures.append("talking")
        while True:
            if self.stop_current_gesture :
                break
            
            right_arm = random.randint(0, 30)
            left_arm = random.randint(120, 160)
            joint_angles = {"right_arm":right_arm, "left_arm":left_arm, "neck_down":152, "neck_up": 70, "neck_right":48, "eye_right": 0, "eye_left":0} 
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(3)
        
        self.stop_current_gesture = False
        self.running_gestures.remove("talking")

        
    def thinking(self) :
        self.running_gestures.append("thinking")
         
        joint_angles = {"right_arm":24, "left_arm":180, "neck_down":20, "neck_up": 50, "neck_right":68, "eye_right": 0, "eye_left":0} 
        self.servo_driver.set_all_angles(joint_angles)
        self.running_gestures.remove("thinking")
        self.stop_current_gesture = False
        


    def doit(self, name, repeat = 1, time = 1):
        
        if len(self.running_gestures) > 0:
            print("A gesture is running curently... ")
            return 
        
        if(name == "salute") :
            print("salute")
            gesture_thread = threading.Thread(target=self.salute, args=(repeat,))
            gesture_thread.start()
            
        if(name == "talking") :
            print("talking")
            gesture_thread = threading.Thread(target=self.talking)
            gesture_thread.start()
            
        if(name == "thinking") :
            print("thinking")
            gesture_thread = threading.Thread(target=self.thinking)
            gesture_thread.start()
        if(name == "default") :
            print("default")
            gesture_thread = threading.Thread(target=self.default)
            gesture_thread.start()

        
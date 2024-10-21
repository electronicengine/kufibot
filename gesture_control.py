import pyaudio
import json
from motor_driver import MotorDriver
from servo_driver import ServoDriver
import tkinter as tk
from tkinter import ttk
import threading
import random
import time

class GestureControl:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'servo_driver'):
            self.servo_driver = ServoDriver()
            self.stop_current_gesture = False
            self.running_gestures = []

    def stop(self):
        self.stop_current_gesture = True

    def default(self):
        joint_angles = {
            "right_arm": 15, "left_arm": 170, 
            "neck_down": 20, "neck_up": 15, 
            "neck_right": 90, "eye_right": 0, "eye_left": 0
        }
        self.servo_driver.set_all_angles(joint_angles)

    def salute(self, repeat):
        self.running_gestures.append("salute")
        for i in range(repeat):
            if self.stop_current_gesture:
                break
            print("salute")
            joint_angles = {
                "right_arm": 15, "left_arm": 150, 
                "neck_down": 78, "neck_up": 15, 
                "neck_right": 68, "eye_right": 0, "eye_left": 0
            }
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(0.5)
            joint_angles["left_arm"] = 122  # Adjusting the angle
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(0.5)
        time.sleep(1)
        self.stop_current_gesture = False
        self.running_gestures.remove("salute")

    def talking(self):
        self.running_gestures.append("talking")
        while not self.stop_current_gesture:
            right_arm = random.randint(0, 30)
            left_arm = random.randint(120, 160)
            joint_angles = {
                "right_arm": right_arm, "left_arm": left_arm,
                "neck_down": 152, "neck_up": 70,
                "neck_right": 48, "eye_right": 0, "eye_left": 0
            }
            self.servo_driver.set_all_angles(joint_angles)
            time.sleep(3)
        self.stop_current_gesture = False
        self.running_gestures.remove("talking")

    def thinking(self):
        self.running_gestures.append("thinking")
        joint_angles = {
            "right_arm": 24, "left_arm": 180, 
            "neck_down": 20, "neck_up": 50, 
            "neck_right": 68, "eye_right": 0, "eye_left": 0
        }
        self.servo_driver.set_all_angles(joint_angles)
        self.running_gestures.remove("thinking")
        self.stop_current_gesture = False

    def doit(self, name, repeat=1):
        if self.running_gestures:
            print("A gesture is currently running...")
            return
        gesture_thread = None
        if name == "salute":
            print("salute")
            gesture_thread = threading.Thread(target=self.salute, args=(repeat,))
        elif name == "talking":
            print("talking")
            gesture_thread = threading.Thread(target=self.talking)
        elif name == "thinking":
            print("thinking")
            gesture_thread = threading.Thread(target=self.thinking)
        elif name == "default":
            print("default")
            gesture_thread = threading.Thread(target=self.default)

        if gesture_thread:
            gesture_thread.start()
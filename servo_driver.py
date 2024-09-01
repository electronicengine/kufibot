#!/usr/bin/python

import time
import math
import smbus
import tkinter as tk
from tkinter import ttk
import time
# Assuming you have a function to set the servo pulse
# pwm.setServoPulse(channel, pulse)

  
from PCA9685 import PCA9685
import time

class ServoDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

        self.joint_channels = {"right_arm":0, "left_arm":1, "neck_down":2, "neck_up": 3, "neck_right":4, "eye_right": 5, "eye_left":6}
        self.joint_angles = {"right_arm":90, "left_arm":90, "neck_down":30, "neck_up": 120, "neck_right":90, "eye_right": 0, "eye_left":0} #default
        
    def set_servo_angle(self, joint, angle):
      # Convert the angle (0-180) to a pulse width
      pulse = int(500 + (angle / 180.0) * 2000)
      print(f"{joint} : {angle} : {self.joint_channels[joint]}")
      self.pwm.setServoPulse(self.joint_channels[joint], pulse)  

    def set_all_angles(self, angles):
      for joint, angle in angles.items():
          self.set_servo_angle(self.channels[joint], angle)
          
    def get_all_joint_angles(self):
      return self.joint_angles
    
    def get_joint_channels(self):
      return self.joint_channels
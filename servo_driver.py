#!/usr/bin/python

import time
import math
import smbus
import tkinter as tk
from tkinter import ttk
import time
# Assuming you have a function to set the servo pulse
# pwm.setServoPulse(channel, pulse)
import json
  
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
      self.joint_angles = self.load_joint_angles() or {"right_arm":15, "left_arm":170, "neck_down":78, "neck_up": 15, "neck_right":90, "eye_right": 0, "eye_left":0}


  def save_joint_angles(self):
    # Save the current joint angles to a JSON file
    with open('joint_angles.json', 'w') as f:
        json.dump(self.joint_angles, f)

  def load_joint_angles(self):
    # Load joint angles from a JSON file, if it exists
    try:
        with open('joint_angles.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
          
  def set_all_angles(self, angles):
    
    for joint, angle in angles.items():
      print(joint, angle)
      self.set_absolute_servo_angle(joint, angle)
      self.save_joint_angles()
  
  def set_absolute_servo_angle(self, joint, target_angle, step=1, delay=0.01):

    current_angle = self.joint_angles.get(joint, 0)  # Get the current angle, default to 0 if not set
    direction = 1 if target_angle > current_angle else -1  # Determine direction of movement

    # Loop until the current angle reaches the target angle
    while current_angle != target_angle:
        current_angle += direction * step

        # Ensure that we do not overshoot the target angle
        if (direction == 1 and current_angle > target_angle) or (direction == -1 and current_angle < target_angle):
            current_angle = target_angle

        # Convert the angle to a pulse width
        pulse = int(500 + (current_angle / 180.0) * 2000)
        print(f"{joint} : {current_angle} : {self.joint_channels[joint]}")
        self.pwm.setServoPulse(self.joint_channels[joint], pulse)

        # Optionally, add a delay for smoother motion
        time.sleep(delay)

    # Update the stored angle once the target is reached
    self.joint_angles[joint] = target_angle
                
  def get_all_joint_angles(self):
    return self.joint_angles

  def get_joint_channels(self):
    return self.joint_channels
  
  # Head movement functions
  def head_down(self):
    
      current_angle = self.joint_angles["neck_up"]
      target_angle = current_angle + 1  # Increase angle up to 90 degrees
      if target_angle >= 180 :
        target_angle = 180

      self.set_absolute_servo_angle("neck_up", target_angle)
      self.joint_angles["neck_up"] = target_angle
      
      current_angle = self.joint_angles["neck_down"]
      target_angle = current_angle - 1  # Increase angle up to 90 degrees
      if target_angle <= 0 :
        target_angle = 0  
      
      self.set_absolute_servo_angle("neck_down", target_angle)
      self.joint_angles["neck_down"] = target_angle
      self.save_joint_angles()

  def head_up(self):
      current_angle = self.joint_angles["neck_up"]
      target_angle = current_angle - 1  # Increase angle up to 90 degrees
      if target_angle <= 20 :
        target_angle = 20
        
      self.set_absolute_servo_angle("neck_up", target_angle)
      self.joint_angles["neck_up"] = target_angle
      
      current_angle = self.joint_angles["neck_down"]
      target_angle = current_angle + 1  # Increase angle up to 90 degrees
      if target_angle >= 180 :
        target_angle = 180
      
      self.set_absolute_servo_angle("neck_down", target_angle)
      self.joint_angles["neck_down"] = target_angle
      self.save_joint_angles()


  def head_left(self):
      current_angle = self.joint_angles["neck_right"]
      target_angle = current_angle + 1  # Increase angle up to 90 degrees
      if target_angle >= 180 :
        target_angle = 180
        
      self.set_absolute_servo_angle("neck_right", target_angle)
      self.joint_angles["neck_right"] = target_angle
      self.save_joint_angles()

  def head_right(self):
      current_angle = self.joint_angles["neck_right"]
      target_angle = current_angle - 1  # Increase angle up to 90 degrees
      if target_angle <= 0 :
        target_angle = 0
        
      self.set_absolute_servo_angle("neck_right", target_angle)
      self.joint_angles["neck_right"] = target_angle
      self.save_joint_angles()

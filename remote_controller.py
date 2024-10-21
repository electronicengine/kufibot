import asyncio
import websockets
import cv2
import numpy as np
import json
import math
import logging
from motor_driver import MotorDriver
from servo_driver import ServoDriver
from compass_driver import CompassDriver
from distance_driver import DistanceDriver
from power_driver import PowerDriver
import threading
import time

class RemoteController:
    def __init__(self, motor_driver, servo_driver, compass_driver, distance_driver, power_driver):
        self.cap = cv2.VideoCapture(0)
        self.servo_driver = servo_driver
        self.motor_driver = motor_driver
        self.compass_driver  = compass_driver
        self.distance_driver = distance_driver
        self.power_driver = power_driver
        self.current_thread = None  # To track the running thread
        self.motor_controling = False

        self.joint_angles = {}
        self.compass = {}
        self.distance  = {}
        self.power = {}
        

    async def remote_stream(self, websocket, path):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send(buffer.tobytes())

            metadata = {
                "joint_angles": self.joint_angles,
                "compass": self.compass,
                "distance": self.distance,
                "power": self.power 
            }
            metadata_json = json.dumps(metadata)
            await websocket.send(metadata_json)  # Send metadata as text
            
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.04)  
                self.handle_robot_control(message)  
            except asyncio.TimeoutError:
                print("Remote Controller Stream Timeout!")
                pass 
            
        self.cap.release()

    def run_in_thread(self, target, *args):

        if self.current_thread and self.current_thread.is_alive():
            return  
        
        self.current_thread = threading.Thread(target=target, args=args)
        self.current_thread.start()

    def control_body(self, angle, magnitude):        
        if magnitude == 0 and angle == 0:
            print("stop")
            self.run_in_thread(self.motor_driver.stop)
        elif 45 <= angle < 135:
            print("forward")
            self.run_in_thread(self.motor_driver.forward, magnitude)
        elif -45 <= angle < 45:
            print("turnRight")
            self.run_in_thread(self.motor_driver.turnRight, magnitude)
        elif -135 <= angle < -45:
            print("backward")
            self.run_in_thread(self.motor_driver.backward, magnitude)
        elif angle >= 135 or angle < -135:
            print("turnLeft")
            self.run_in_thread(self.motor_driver.turnLeft, magnitude)
        else:
            print("stop")
            self.run_in_thread(self.motor_driver.stop)
        
    def control_head(self, angle, magnitude):
        if magnitude == 0 and angle == 0:
            return
        elif 45 <= angle < 135:
            self.run_in_thread(self.servo_driver.head_up)
        elif -45 <= angle < 45:
            self.run_in_thread(self.servo_driver.head_right)
        elif -135 <= angle < -45:
            self.run_in_thread(self.servo_driver.head_down)
        elif angle >= 135 or angle < -135:
            self.run_in_thread(self.servo_driver.head_left)
        else:
            return 

    def control_arm(self,control_id, angle):
        mapped_angle = (angle / 100) * 180
        if control_id == "left_arm":
            print("left_arm: ", angle)
            self.run_in_thread(self.servo_driver.set_absolute_servo_angle, "left_arm", mapped_angle)
        elif control_id == "right_arm" :
            print("right_arm: ", angle)
            self.run_in_thread(self.servo_driver.set_absolute_servo_angle, "right_arm", mapped_angle)
        else :
            pass

    def control_eye(self, angle):
        if angle == 180:
            print("eye_up")
            self.run_in_thread(self.servo_driver.eye_up)
        elif angle == 0 :
            print("eye_down")
            self.run_in_thread(self.servo_driver.eye_down)
        else :
            pass

    def handle_robot_control(self, input_message):
        try:
            data = json.loads(input_message)
            if data:
                object_name = list(data.keys())[0]
                control_id = object_name
                
                if control_id != None:
                    self.motor_controling = True

                if control_id == "body_joystick":
                    angle = data[object_name]["Angle"]
                    strength = data[object_name]["Strength"]
                    self.control_body(angle, strength)
                elif control_id == "head_joystick":
                    angle = data[object_name]["Angle"]
                    strength = data[object_name]["Strength"]
                    self.control_head(angle, strength)
                elif control_id in ["right_arm", "left_arm"]:
                    angle = data[object_name]["Angle"]
                    self.control_arm(control_id, angle)
                elif control_id in ["right_eye", "left_eye"]:
                    angle = data[object_name]["Angle"]
                    self.control_eye(angle)
                else : 
                    self.motor_controling = False
                    
            else:
                self.motor_controling = False

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"Missing key in JSON data: {e}")

    async def timer_loop(self):

        while True:
            
            if self.motor_controling == False:
                self.compass = await asyncio.to_thread(self.compass_driver.get_all)
                self.distance = await asyncio.to_thread(self.distance_driver.get_distance)
                self.power = await asyncio.to_thread(self.power_driver.get_consumption)
                self.joint_angles = self.servo_driver.get_all_joint_angles()
                
            await asyncio.sleep(0.5)  # Wait for 1 second
            
    async def main(self):
        ip = "192.168.1.44"
        # controller_port = 8766
        remote_server_port = 8765
        
        print(f"Starting WebSocket server at {ip}:{remote_server_port}...")
        remote_server = await websockets.serve(self.remote_stream, ip, remote_server_port)

        asyncio.create_task(self.timer_loop())
        
        await remote_server.wait_closed()

        


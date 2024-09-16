import asyncio
import websockets
import cv2
import numpy as np
import json
import math
import logging
from motor_driver import MotorDriver
from servo_driver import ServoDriver
import time

class RemoteController:
    def __init__(self, motor_driver, servo_driver):
        self.cap = cv2.VideoCapture(0)
        self.servo_driver = servo_driver
        self.motor_driver = motor_driver

    async def video_stream(self, websocket, path):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send(buffer.tobytes())
            await asyncio.sleep(0.04)


        self.cap.release()

    async def controller_handler(self, websocket, path):
        async for message in websocket:

            if message == "Get Info":
                joint_angles = self.servo_driver.get_all_joint_angles()
                joint_angles_json = json.dumps(joint_angles)
                print(f"sending: {joint_angles_json}")
                await websocket.send(joint_angles_json)
            else:
                self.handle_robot_control(message)

    def control_body(self, angle, magnitude):
        if magnitude == 0 and angle == 0:
            self.motor_driver.stop()
        elif 45 <= angle < 135:
            print("forward")
            self.motor_driver.forward(magnitude)
        elif -45 <= angle < 45:
            print("turnRight")
            self.motor_driver.turnRight(magnitude)
        elif -135 <= angle < -45:
            print("turnRight")
            self.motor_driver.backward(magnitude)
        elif angle >= 135 or angle < -135:
            self.motor_driver.turnLeft(magnitude)
        else:
            self.motor_driver.stop()

    def control_head(self, angle, magnitude):
        if magnitude == 0 and angle == 0:
            pass
        elif 45 <= angle < 135:
            self.servo_driver.head_up()
        elif -45 <= angle < 45:
            self.servo_driver.head_right()
        elif -135 <= angle < -45:
            self.servo_driver.head_down()
        elif angle >= 135 or angle < -135:
            self.servo_driver.head_left()

    def control_arm(self,control_id, angle):
        mapped_angle = (angle / 100) * 180
        if control_id == "left_arm":
            self.servo_driver.set_absolute_servo_angle("left_arm", mapped_angle)
        elif control_id == "right_arm" :
            self.servo_driver.set_absolute_servo_angle("right_arm", mapped_angle)
        else :
            pass

    def control_eye(self, control_id, angle):
        
        if control_id == "left_eye":
            self.servo_driver.set_absolute_servo_angle("left_eye", angle)
        elif control_id == "right_eye" :
            self.servo_driver.set_absolute_servo_angle("right_eye", angle)
        else :
            pass

    def handle_robot_control(self, input_message):
        try:
            data = json.loads(input_message)
            control_id = data.get("Id")
            angle = data.get("Angle")
            strength = data.get("Strength")
            print(control_id)

            if control_id == "body_joystick":
                self.control_body(angle, strength)
            elif control_id == "head_joystick":
                self.control_head(angle, strength)
            elif control_id in ["right_arm", "left_arm"]:
                self.control_arm(control_id, angle)
            elif control_id in ["right_eye", "left_eye"]:
                self.control_eye(angle)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"Missing key in JSON data: {e}")

    async def main(self):
        ip = "192.168.1.39"
        controller_port = 8766
        video_stream_port = 8765
        
        controller_server = await websockets.serve(self.controller_handler, ip, controller_port)
        video_server = await websockets.serve(self.video_stream, ip, video_stream_port)

        await asyncio.gather(
            controller_server.wait_closed(),
            video_server.wait_closed()
        )
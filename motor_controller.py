import time
from motor_driver import MotorDriver

class MotorController:
    def __init__(self, motor_driver):
        self.motor_driver = motor_driver

    def forward_motor(self):
        print("Moving forward for 2 seconds...")
        self.motor_driver.run(0, 'forward', 100)
        time.sleep(2)
        print("Stopping motor...")
        self.motor_driver.stop(0)

    def backward_motor(self):
        print("Moving backward for 2 seconds...")
        self.motor_driver.run(0, 'backward', 100)
        time.sleep(2)
        print("Stopping motor...")
        self.motor_driver.stop(0)

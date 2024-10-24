from PCA9685 import PCA9685
import time

class MotorDriver:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, address=0x40, frequency=50):
        if not hasattr(self, 'pwm'):  # Avoid re-initialization
            self.pwm = PCA9685(address, debug=False)
            self.pwm.setPWMFreq(frequency)
            self.PWMA = 0
            self.AIN1 = 1
            self.AIN2 = 2
            self.PWMB = 5
            self.BIN1 = 3
            self.BIN2 = 4
            self.direction = ['forward', 'backward']
            self.motor = {"right": 0, "left": 1}

    def run(self, motor, direction, speed):
        if speed > 100:
            raise ValueError("Speed must be between 0 and 100.")

        if motor == 0:
            self.pwm.setDutycycle(self.PWMA, speed)
            self._set_direction(self.AIN1, self.AIN2, direction)
        else:
            self.pwm.setDutycycle(self.PWMB, speed)
            self._set_direction(self.BIN1, self.BIN2, direction)

    def _set_direction(self, pin1, pin2, direction):
        if direction == self.direction[0]:  # Forward
            self.pwm.setLevel(pin1, 0)
            self.pwm.setLevel(pin2, 1)
        else:  # Backward
            self.pwm.setLevel(pin1, 1)
            self.pwm.setLevel(pin2, 0)

    def forward(self, magnitude):
        self.run(self.motor["right"], 'forward', magnitude)
        self.run(self.motor["left"], 'forward', magnitude)

    def backward(self, magnitude):
        self.run(self.motor["right"], 'backward', magnitude)
        self.run(self.motor["left"], 'backward', magnitude)

    def turnRight(self, magnitude):
        self.run(self.motor["right"], 'forward', magnitude)
        self.run(self.motor["left"], 'backward', magnitude)

    def turnLeft(self, magnitude):
        self.run(self.motor["right"], 'backward', magnitude)
        self.run(self.motor["left"], 'forward', magnitude)

    def stop(self):
        self.pwm.setDutycycle(self.PWMA, 0)
        self.pwm.setDutycycle(self.PWMB, 0)
import serial
import time

class DistanceDriver:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'uart'):
            self.uart = serial.Serial("/dev/ttyAMA0", 115200)

    def read_data(self):
        time.sleep(1)
        while True:
            counter = self.uart.in_waiting
            if counter > 8:
                bytes_serial = self.uart.read(9)
                self.uart.reset_input_buffer()

                if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                    distance = bytes_serial[2] + bytes_serial[3] * 256
                    strength = bytes_serial[4] + bytes_serial[5] * 256
                    temperature = bytes_serial[6] + bytes_serial[7] * 256
                    temperature = (temperature / 8) - 256
                    self.uart.reset_input_buffer()
                    return {"Distance": distance, "Strength": strength, "Temperature": temperature}

                if bytes_serial[0] == b"Y" and bytes_serial[1] == b"Y":
                    distL = int(bytes_serial[2].hex(), 16)
                    distH = int(bytes_serial[3].hex(), 16)
                    stL = int(bytes_serial[4].hex(), 16)
                    stH = int(bytes_serial[5].hex(), 16)
                    distance = distL + distH * 256
                    strength = stL + stH * 256
                    tempL = int(bytes_serial[6].hex(), 16)
                    tempH = int(bytes_serial[7].hex(), 16)
                    temperature = tempL + tempH * 256
                    temperature = (temperature / 8) - 256
                    self.uart.reset_input_buffer()
                    return {"Distance": distance, "Strength": strength, "Temperature": temperature}

    def get_distance(self):
        if not self.uart.isOpen():
            self.uart.open()
        return self.read_data()

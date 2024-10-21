from ina219 import INA219, DeviceRangeError
from time import sleep

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 2.0


class PowerDriver:
    _instance = None  # Class-level variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'ina'):
            self.ina = INA219(SHUNT_OHMS, busnum = 1, address = 0x44)
            self.ina.configure(self.ina.RANGE_16V)
            
    def get_consumption(self):
        return {
            "BusVoltage": self.ina.voltage(),
            "BusCurrent": self.ina.current(),
            "Power": self.ina.power(),
            "ShuntVoltage": self.ina.shunt_voltage()
        }
